#!/usr/bin/env python3
"""公開Googleスプレッドシートを全シートCSV取得→Markdown変換して保存する。

使い方:
    python3 download.py <スプレッドシートURL> <出力先ディレクトリ> [--gid GID]

- 標準ライブラリのみ使用（venv不要）
- htmlview からスプレッドシートのタイトルと全シートの gid・シート名を列挙し、シートごとに CSV を取得
- 複数シート時: <出力先>/<スプシタイトル>/ 配下に各シート名の md と index.md、csv/ を保存
- 単一シート時: <出力先>/<スプシタイトル>.md として保存（index.md なし、生CSVは <出力先>/csv/）
- export が 401/403（閲覧者のダウンロード禁止設定）のときは gviz エンドポイントへ自動フォールバック
- --gid 指定時はそのシートのみ取得
"""

import csv
import html as html_lib
import io
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
RETRY = 3
SLEEP_BETWEEN = 0.5


def fetch(url: str) -> bytes:
    last_err = None
    for attempt in range(1, RETRY + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as res:
                final_url = res.geturl()
                if "accounts.google.com" in final_url:
                    raise PermissionError("ログインページへリダイレクトされました（非公開の可能性）")
                return res.read()
        except PermissionError:
            raise
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise PermissionError(
                    f"HTTP {e.code}（非公開、または閲覧者のダウンロード禁止設定の可能性）"
                )
            last_err = e
            if attempt < RETRY:
                time.sleep(attempt * 2)
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < RETRY:
                time.sleep(attempt * 2)
    raise RuntimeError(f"取得失敗: {url} ({last_err})")


def extract_spreadsheet_id(url: str) -> str:
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        raise ValueError(f"スプレッドシートIDをURLから抽出できません: {url}")
    return m.group(1)


def js_unescape(s: str) -> str:
    """JS文字列リテラルのエスケープ（\\/, \\xHH, \\uHHHH など）を解除する。"""

    def repl(m: re.Match) -> str:
        t = m.group(1)
        if t[0] in ("u", "x"):
            return chr(int(t[1:], 16))
        return {"n": "\n", "t": "\t", "r": "\r"}.get(t, t)

    return re.sub(r"\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", repl, s)


def list_sheets(sheet_id: str) -> tuple[str, list[dict]]:
    """htmlview のHTMLからスプレッドシートのタイトルと全シートの name / gid を列挙する。"""
    page = fetch(f"https://docs.google.com/spreadsheets/d/{sheet_id}/htmlview").decode(
        "utf-8", errors="replace"
    )
    title = ""
    m = re.search(r"<title>(.*?)</title>", page, re.S)
    if m:
        title = html_lib.unescape(m.group(1))
        title = re.sub(
            r"\s*-\s*Google\s*(ドライブ|スプレッドシート|Drive|Sheets)\s*$", "", title
        ).strip()
    sheets = []
    for m in re.finditer(r'\{name:\s*"((?:[^"\\]|\\.)*)",\s*pageUrl:[^}]*?gid:\s*"(\d+)"', page):
        sheets.append({"name": js_unescape(m.group(1)), "gid": m.group(2)})
    if not sheets:
        raise RuntimeError(
            "シート一覧を抽出できませんでした。非公開シートか、Google側の仕様変更の可能性があります"
        )
    return title or "無題のスプレッドシート", sheets


def fetch_csv(sheet_id: str, gid: str) -> tuple[list[list[str]], bytes]:
    try:
        raw = fetch(
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        )
    except PermissionError:
        # 閲覧者のダウンロード禁止設定でも gviz 経由なら表示値のCSVを取得できる
        raw = fetch(
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
        )
    text = raw.decode("utf-8-sig", errors="replace")
    return list(csv.reader(io.StringIO(text))), raw


def trim_rows(rows: list[list[str]]) -> list[list[str]]:
    """末尾の空行と、全行で空の末尾列を削る。"""
    while rows and all(c.strip() == "" for c in rows[-1]):
        rows.pop()
    if not rows:
        return rows
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    while width > 0 and all(r[width - 1].strip() == "" for r in rows):
        width -= 1
    return [r[:width] for r in rows]


def md_cell(value: str) -> str:
    v = value.replace("|", "\\|")
    v = re.sub(r"\r\n|\r|\n", "<br>", v)
    return v.strip()


def rows_to_md_table(rows: list[list[str]]) -> str:
    if not rows:
        return "（空シート）\n"
    header = rows[0]
    lines = [
        "| " + " | ".join(md_cell(c) for c in header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for r in rows[1:]:
        lines.append("| " + " | ".join(md_cell(c) for c in r) + " |")
    return "\n".join(lines) + "\n"


def safe_filename(name: str) -> str:
    s = re.sub(r'[/\\:*?"<>|]', "_", name).strip().strip(".")
    return s or "無題"


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only_gid = None
    argv = sys.argv[1:]
    if "--gid" in argv:
        only_gid = argv[argv.index("--gid") + 1]
    if len(args) < 2:
        print("使い方: download.py <スプレッドシートURL> <出力先ディレクトリ> [--gid GID]")
        sys.exit(1)

    url, out_dir = args[0], Path(args[1])
    sheet_id = extract_spreadsheet_id(url)
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")

    print(f"スプレッドシートID: {sheet_id}")
    title, sheets = list_sheets(sheet_id)
    print(f"タイトル: {title}")
    print(f"シート数: {len(sheets)}")
    for s in sheets:
        print(f"  - {s['name']} (gid={s['gid']})")

    if only_gid is not None:
        sheets = [s for s in sheets if s["gid"] == only_gid]
        if not sheets:
            print(f"エラー: gid={only_gid} のシートが見つかりません")
            sys.exit(1)

    # 単一シートなら <出力先>/<タイトル>.md、複数なら <出力先>/<タイトル>/ 配下に展開
    single = len(sheets) == 1
    title_base = safe_filename(title)
    base_dir = out_dir if single else out_dir / title_base
    (base_dir / "csv").mkdir(parents=True, exist_ok=True)
    ok, ng = 0, 0
    used_names: set[str] = set()
    index_lines = []

    for i, s in enumerate(sheets, 1):
        name, gid = s["name"], s["gid"]
        base = title_base if single else safe_filename(name)
        if base in used_names:
            base = f"{base}_{gid}"
        used_names.add(base)
        try:
            rows, raw = fetch_csv(sheet_id, gid)
            (base_dir / "csv" / f"{base}.csv").write_bytes(raw)
            rows = trim_rows(rows)
            heading = title if single else name
            front = (
                "---\n"
                f"source: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid={gid}\n"
                f"spreadsheet_title: \"{title}\"\n"
                f"sheet_name: \"{name}\"\n"
                f"gid: \"{gid}\"\n"
                f"exported: {now}\n"
                "---\n\n"
                f"# {heading}\n\n"
            )
            (base_dir / f"{base}.md").write_text(front + rows_to_md_table(rows), encoding="utf-8")
            index_lines.append(f"- [[{base}]]（{len(rows)}行）")
            ok += 1
            print(f"[{i}/{len(sheets)}] 成功: {name} ({len(rows)}行)")
        except Exception as e:  # noqa: BLE001
            ng += 1
            index_lines.append(f"- {name}（取得失敗）")
            print(f"[{i}/{len(sheets)}] 失敗: {name} ({e})")
        time.sleep(SLEEP_BETWEEN)

    if not single:
        index = (
            "---\n"
            f"source: https://docs.google.com/spreadsheets/d/{sheet_id}/edit\n"
            f"spreadsheet_title: \"{title}\"\n"
            f"exported: {now}\n"
            "---\n\n"
            f"# {title}\n\n"
            f"> 取得元: https://docs.google.com/spreadsheets/d/{sheet_id}/edit\n"
            f"> 取得日時: {now} JST\n\n"
            "## シート一覧\n\n" + "\n".join(index_lines) + "\n"
        )
        (base_dir / "index.md").write_text(index, encoding="utf-8")
    print(f"完了: シート 成功 {ok} / 失敗 {ng}")
    print(f"出力先: {base_dir if not single else out_dir / (title_base + '.md')}")


if __name__ == "__main__":
    main()
