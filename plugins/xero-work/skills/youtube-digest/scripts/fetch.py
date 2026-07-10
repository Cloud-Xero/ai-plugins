#!/usr/bin/env python3
"""登録チャンネルの新着動画(または引数で指定した動画)の字幕を取得し pending.json に書き出す。

使い方(スキルのベースディレクトリから):
  .venv/bin/python scripts/fetch.py
  .venv/bin/python scripts/fetch.py <動画URLまたはvideo_id> ...

  動画URL/IDを指定した場合はその動画だけを処理する(チャンネル巡回はしない)。
  未登録チャンネルの動画は folder が null になる — 格納先の決定は呼び出し元(スキル)が行う。

  オプション:
    --dry-run        字幕取得を行わず対象一覧の表示のみ
    --config PATH    config.json のパスを差し替え(テスト用)

state.json は変更しない。処理済みの記録は mark_done.py が行う。
"""

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import defusedxml.ElementTree as ET

BASE = Path(__file__).resolve().parent.parent  # スキルのベースディレクトリ
STATE_PATH = BASE / "state.json"
PENDING_PATH = BASE / "pending.json"
TRANSCRIPTS_DIR = BASE / "transcripts"

ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"

VIDEO_ID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([0-9A-Za-z_-]{11})")
UA = {"User-Agent": "Mozilla/5.0"}


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def http_get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read()


def parse_video_id(arg: str) -> str | None:
    m = VIDEO_ID_RE.search(arg)
    if m:
        return m.group(1)
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", arg):
        return arg
    return None


def parse_feed(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    videos = []
    for entry in root.findall(f"{ATOM}entry"):
        video_id = entry.findtext(f"{YT}videoId")
        if not video_id:
            continue
        videos.append(
            {
                "video_id": video_id,
                "title": (entry.findtext(f"{ATOM}title") or "(no title)").strip(),
                "published": (entry.findtext(f"{ATOM}published") or "")[:10],
            }
        )
    return videos


def fetch_video_meta(video_id: str) -> dict:
    """単体動画のメタデータを取得する。oEmbedが本命、watchページはベストエフォート。"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    meta = {"title": None, "channel": None, "channel_id": None, "published": ""}
    try:
        oembed_url = (
            "https://www.youtube.com/oembed?url="
            + urllib.parse.quote(url, safe="")
            + "&format=json"
        )
        data = json.loads(http_get(oembed_url).decode("utf-8"))
        meta["title"] = (data.get("title") or "").strip() or None
        meta["channel"] = data.get("author_name")
    except Exception as e:  # noqa: BLE001
        print(f"  ! oEmbed取得失敗 ({type(e).__name__})", file=sys.stderr)
    try:
        html = http_get(url).decode("utf-8", errors="replace")
        m = re.search(r'"publishDate":\s*"(\d{4}-\d{2}-\d{2})', html)
        if m:
            meta["published"] = m.group(1)
        m = re.search(r'"externalChannelId":\s*"(UC[0-9A-Za-z_-]{22})"', html) or re.search(
            r'"channelId":\s*"(UC[0-9A-Za-z_-]{22})"', html
        )
        if m:
            meta["channel_id"] = m.group(1)
    except Exception:  # noqa: BLE001
        pass  # 公開日・channel_idは取れなくても続行できる
    return meta


def fetch_transcript(video_id: str, languages: list[str]):
    """(text, lang, error) を返す。取得失敗時は text が None。"""
    from youtube_transcript_api import YouTubeTranscriptApi

    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=languages)
        text = "\n".join(snippet.text for snippet in fetched)
        return text, getattr(fetched, "language_code", ""), None
    except Exception as e:  # noqa: BLE001 - 字幕なし/非公開など全て pending に記録する
        return None, None, f"{type(e).__name__}: {e}"


def sanitize_folder(name: str) -> str:
    for ch in '/\\:*?"<>|':
        name = name.replace(ch, "_")
    return name.strip() or "uncategorized"


def list_channel_videos(channel_id: str, depth: int) -> list[dict]:
    """チャンネルの動画一覧(新しい順・最大depth件)を取得する。RSS(直近15本)より過去に遡れる。

    yt-dlp のフラット抽出を使う。一覧のメタデータ取得のみで動画はダウンロードしない。
    """
    try:
        import yt_dlp
    except ImportError:
        print(f"! backfill には yt-dlp が必要: {BASE}/.venv/bin/pip install yt-dlp", file=sys.stderr)
        return []
    opts = {"extract_flat": True, "playlistend": depth, "quiet": True, "no_warnings": True}
    url = f"https://www.youtube.com/channel/{channel_id}/videos"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:  # noqa: BLE001
        print(f"! backfill 一覧取得失敗 ({type(e).__name__}: {e})", file=sys.stderr)
        return []
    videos = []
    for e in info.get("entries") or []:
        if not e or not e.get("id"):
            continue
        videos.append(
            {
                "video_id": e["id"],
                "title": (e.get("title") or "").strip() or f"(タイトル不明: {e['id']})",
                "published": "",  # フラット抽出では取れないため後で watch ページから補完する
            }
        )
    return videos


def attach_transcript(entry: dict, languages: list[str]) -> None:
    """entry に字幕を取得して transcript_path / error を書き込む。"""
    vid = entry["video_id"]
    transcript_file = TRANSCRIPTS_DIR / f"{vid}.txt"
    label = f"[{entry['published'] or '????-??-??'}] {entry['title']}"

    if transcript_file.exists() and transcript_file.stat().st_size > 0:
        entry["transcript_path"] = str(transcript_file)
        print(f"  ✓ {label} (字幕取得済みを再利用)")
        return

    text, lang, error = fetch_transcript(vid, languages)
    if text:
        header = (
            f"# {entry['title']}\n# {entry['url']}\n# published: {entry['published']}\n\n"
        )
        transcript_file.write_text(header + text, encoding="utf-8")
        entry["transcript_path"] = str(transcript_file)
        entry["transcript_lang"] = lang
        print(f"  ✓ {label} ({lang}, {len(text)}文字)")
    else:
        entry["error"] = error
        print(f"  ✗ {label} 字幕取得失敗: {error}")
    time.sleep(1.5)  # 連続アクセスを避ける


def new_entry(video_id: str, title: str, channel: str, channel_id, folder, published: str, adhoc: bool) -> dict:
    return {
        "video_id": video_id,
        "title": title,
        "channel": channel,
        "channel_id": channel_id,
        "folder": folder,
        "published": published,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "adhoc": adhoc,
        "transcript_path": None,
        "transcript_lang": None,
        "error": None,
    }


def collect_from_channels(config: dict, processed: set) -> list[list[dict]]:
    """チャンネルごとの処理候補(字幕未取得)をリストのリストで返す。"""
    limit = config.get("max_per_channel", config.get("max_new_per_run", 5))
    per_channel = []
    for channel in config.get("channels", []):
        channel_id = channel.get("channel_id", "")
        name = channel.get("name", channel_id)
        if not channel_id or "xxxx" in channel_id:
            print(f"skip(サンプル行): {name}")
            continue
        folder = channel.get("folder") or sanitize_folder(name)

        try:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            videos = parse_feed(http_get(feed_url))
        except Exception as e:  # noqa: BLE001
            print(f"✗ {name}: フィード取得失敗 ({type(e).__name__}: {e})", file=sys.stderr)
            continue

        new_videos = [v for v in videos if v["video_id"] not in processed]
        new_videos = sorted(new_videos, key=lambda v: v["published"])[:limit]
        print(f"{name}: 新着 {len(new_videos)} 件 (フィード内 {len(videos)} 件)")

        # backfill: フィード内の未処理だけでは枠が埋まらない場合、過去の未要約動画(新しい順)で埋める
        remaining = limit - len(new_videos)
        if remaining > 0 and channel.get("backfill"):
            depth = config.get("backfill_scan_depth", 50)
            feed_ids = {v["video_id"] for v in videos}
            older = [
                v
                for v in list_channel_videos(channel_id, depth)
                if v["video_id"] not in processed and v["video_id"] not in feed_ids
            ][:remaining]
            for v in older:
                meta = fetch_video_meta(v["video_id"])
                v["published"] = meta["published"]
                if meta["title"]:
                    v["title"] = meta["title"]
            if older:
                print(f"  backfill: 過去の未要約 {len(older)} 件を追加 (スキャン範囲: 直近{depth}本)")
            new_videos.extend(older)

        per_channel.append(
            [
                new_entry(
                    video["video_id"], video["title"], name, channel_id, folder,
                    video["published"], adhoc=False,
                )
                for video in new_videos
            ]
        )
    return per_channel


def apply_global_cap(per_channel: list[list[dict]], cap: int) -> list[dict]:
    """1回の実行全体の上限を適用する。特定チャンネルが枠を独占しないようラウンドロビンで選ぶ。"""
    selected = []
    index = 0
    while len(selected) < cap:
        picked_any = False
        for videos in per_channel:
            if index < len(videos):
                selected.append(videos[index])
                picked_any = True
                if len(selected) >= cap:
                    break
        if not picked_any:
            break
        index += 1
    return selected


def collect_from_urls(video_args: list[str], config: dict, processed: set, languages: list[str], dry_run: bool, force: bool) -> list[dict]:
    channel_by_id = {
        c["channel_id"]: c
        for c in config.get("channels", [])
        if c.get("channel_id") and "xxxx" not in c["channel_id"]
    }
    pending = []
    for arg in video_args:
        vid = parse_video_id(arg)
        if not vid:
            print(f"✗ video_id を解釈できません: {arg}", file=sys.stderr)
            continue
        if vid in processed:
            if not force:
                print(f"skip(処理済み): {arg} → 再要約する場合は --force を付ける")
                continue
            print(f"! {vid} は処理済みだが --force 指定のため再処理する(ノートは上書き)")

        meta = fetch_video_meta(vid)
        registered = channel_by_id.get(meta["channel_id"])
        if registered:
            folder = registered.get("folder") or sanitize_folder(registered["name"])
            channel_name = registered["name"]
        else:
            folder = None  # 未登録チャンネル: 格納先は呼び出し元が決める
            channel_name = meta["channel"] or "(チャンネル名不明)"

        entry = new_entry(
            vid, meta["title"] or f"(タイトル不明: {vid})", channel_name,
            meta["channel_id"], folder, meta["published"], adhoc=True,
        )
        print(f"指定動画: {entry['title']} / {channel_name}"
              + (f" → {folder}/" if folder else " → 格納先未定(未登録チャンネル)"))
        if dry_run:
            print(f"  - [{entry['published'] or '????-??-??'}] {entry['title']}")
        else:
            attach_transcript(entry, languages)
        pending.append(entry)
    return pending


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("videos", nargs="*", help="動画URLまたはvideo_id(指定時はその動画のみ処理)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="URL指定時、処理済みでも再要約する(ノート上書き)")
    parser.add_argument("--config", type=Path, default=BASE / "config.json")
    args = parser.parse_args()

    config = load_json(args.config, None)
    if config is None:
        print(f"config が見つかりません: {args.config}", file=sys.stderr)
        sys.exit(1)

    state = load_json(STATE_PATH, {"processed": []})
    processed = set(state.get("processed", []))
    languages = config.get("transcript_languages", ["ja", "en"])
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)

    if args.videos:
        # URL指定は明示的な依頼なので全体上限の対象外
        pending = collect_from_urls(args.videos, config, processed, languages, args.dry_run, args.force)
    else:
        per_channel = collect_from_channels(config, processed)
        cap = config.get("max_total_per_run", 5)
        total = sum(len(videos) for videos in per_channel)
        pending = apply_global_cap(per_channel, cap)
        if total > len(pending):
            print(f"\n全体上限 {cap} 本を適用: {total - len(pending)} 件は次回に持ち越し")
        if pending:
            print(f"\n処理対象 {len(pending)} 件:")
        for entry in pending:
            if args.dry_run:
                print(f"  - [{entry['published'] or '????-??-??'}] {entry['channel']}: {entry['title']}")
            else:
                attach_transcript(entry, languages)

    if not args.dry_run:
        PENDING_PATH.write_text(
            json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\npending: {len(pending)} 件 → {PENDING_PATH}")


if __name__ == "__main__":
    main()
