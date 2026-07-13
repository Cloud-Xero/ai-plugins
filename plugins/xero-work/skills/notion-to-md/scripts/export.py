#!/usr/bin/env python3
"""公開Notionページ（notion.site）を子ページ・データベースも含めて再帰的に
Markdownエクスポートする。

使い方:
    python3 export.py <NotionURL> <出力先ディレクトリ>

- 各ページに frontmatter（source / notion_created / notion_updated / exported）を付与
- トップページには取得元URLと取得日時も記載
- 画像は <出力先>/attachments/ にダウンロードし、相対パスで参照
- 依存: Python 3 標準ライブラリのみ
"""
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
JST = datetime.timezone(datetime.timedelta(hours=9))

img_stats = {"ok": 0, "fail": 0}
page_count = {"ok": 0, "fail": 0}
visited = set()


def log(msg):
    print(msg, flush=True)


class Exporter:
    def __init__(self, base, out_dir):
        self.base = base
        self.out_dir = out_dir
        self.attach_dir = os.path.join(out_dir, "attachments")
        self.space_id = None
        self.exported_at = datetime.datetime.now(JST).strftime("%Y-%m-%d %H:%M")
        os.makedirs(self.attach_dir, exist_ok=True)

    # ---------- API ----------

    def api(self, path, payload):
        req = urllib.request.Request(
            self.base + "/api/v3/" + path,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "User-Agent": UA},
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.load(r)
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))

    def load_all_blocks(self, page_id):
        """loadPageChunk をカーソルが尽きるまで叩き、全レコードを返す。"""
        record_map = {"block": {}, "collection_view": {}, "collection": {}}
        cursor = {"stack": []}
        chunk = 0
        while True:
            res = self.api("loadPageChunk", {
                "pageId": page_id, "limit": 100, "cursor": cursor,
                "chunkNumber": chunk, "verticalColumns": False,
            })
            for table in record_map:
                for rid, wrap in res.get("recordMap", {}).get(table, {}).items():
                    v = wrap.get("value", {})
                    if "value" in v:
                        v = v["value"]
                    if v:
                        record_map[table][rid] = v
                        if self.space_id is None and v.get("space_id"):
                            self.space_id = v["space_id"]
                        if self.space_id is None and wrap.get("spaceId"):
                            self.space_id = wrap["spaceId"]
            cursor = res.get("cursor") or {"stack": []}
            chunk += 1
            if not cursor.get("stack"):
                break
        return record_map

    def query_collection(self, collection_id, view_id):
        """データベース（コレクション）の全アイテムIDとレコードを返す。"""
        res = self.api("queryCollection?src=initial_load", {
            "collection": {"id": collection_id, "spaceId": self.space_id},
            "collectionView": {"id": view_id, "spaceId": self.space_id},
            "loader": {"type": "reducer",
                       "reducers": {"collection_group_results":
                                    {"type": "results", "limit": 1000}},
                       "searchQuery": "", "userTimeZone": "Asia/Tokyo"},
        })
        ids = (res.get("result", {}).get("reducerResults", {})
               .get("collection_group_results", {}).get("blockIds", []))
        blocks = {}
        for rid, wrap in res.get("recordMap", {}).get("block", {}).items():
            v = wrap.get("value", {})
            if "value" in v:
                v = v["value"]
            if v:
                blocks[rid] = v
        return ids, blocks

    # ---------- 変換ヘルパ ----------

    @staticmethod
    def rich_text(prop):
        if not prop:
            return ""
        out = []
        for seg in prop:
            text = seg[0]
            fmts = seg[1] if len(seg) > 1 else []
            if text == "⁍":  # 数式
                for f in fmts:
                    if f[0] == "e":
                        text = f"${f[1]}$"
                out.append(text)
                continue
            link = None
            for f in fmts:
                k = f[0]
                if k == "b":
                    text = f"**{text}**"
                elif k == "i":
                    text = f"*{text}*"
                elif k == "s":
                    text = f"~~{text}~~"
                elif k == "c":
                    text = f"`{text}`"
                elif k == "a":
                    link = f[1]
            if link:
                if link.startswith("/"):
                    link = "https://www.notion.so" + link
                text = f"[{text}]({link})"
            out.append(text)
        return "".join(out)

    @staticmethod
    def plain(text):
        return re.sub(r"\*\*|\*|`|~~", "", text)

    @staticmethod
    def sanitize(name):
        return re.sub(r'[/\\:*?"<>|#^\[\]]', "_", name).strip() or "無題"

    @staticmethod
    def jst(ms):
        return datetime.datetime.fromtimestamp(
            ms / 1000, JST).strftime("%Y-%m-%d %H:%M")

    def page_title(self, block):
        t = self.plain(self.rich_text(
            block.get("properties", {}).get("title")))
        return t.strip() or f"無題_{block['id'][:8]}"

    def download_image(self, src, bid):
        url = src
        if (src.startswith("attachment:")
                or "secure.notion-static.com" in src
                or src.startswith("https://prod-files")):
            url = (f"{self.base}/image/{urllib.parse.quote(src, safe='')}"
                   f"?table=block&id={bid}&spaceId={self.space_id}")
        h = hashlib.md5(url.encode()).hexdigest()[:12]
        for existing in os.listdir(self.attach_dir):
            if existing.startswith(h):
                return existing
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                ctype = r.headers.get("Content-Type", "")
            ext = {"image/png": ".png", "image/jpeg": ".jpg",
                   "image/gif": ".gif", "image/webp": ".webp",
                   "image/svg+xml": ".svg"}.get(ctype.split(";")[0], ".png")
            fname = h + ext
            with open(os.path.join(self.attach_dir, fname), "wb") as f:
                f.write(data)
            img_stats["ok"] += 1
            return fname
        except Exception:
            img_stats["fail"] += 1
            return None

    # ---------- レンダリング ----------

    def render(self, bid, blocks, attach_rel, child_pages, depth=0):
        """1ブロックをMarkdown行のリストへ。子ページは child_pages に積む。"""
        b = blocks.get(bid)
        if not b:
            return []
        t = b.get("type")
        props = b.get("properties", {})
        title = self.rich_text(props.get("title"))
        indent = "    " * depth
        lines = []

        def children(extra=0):
            out = []
            for cid in b.get("content", []):
                out.extend(self.render(cid, blocks, attach_rel,
                                       child_pages, depth + extra))
            return out

        if t == "page":
            if depth == 0 and bid not in {p[0] for p in child_pages}:
                # ページ本体（呼び出し元でタイトル・frontmatterを付ける）
                for cid in b.get("content", []):
                    lines.extend(self.render(cid, blocks, attach_rel,
                                             child_pages, 0))
            else:
                name = self.page_title(b)
                child_pages.append((bid, name))
                lines.append(f"{indent}- 📄 [[{self.sanitize(name)}]]")
        elif t == "alias":
            alias_id = (b.get("format", {}).get("alias_pointer", {}) or {}).get("id")
            if alias_id:
                lines.append(f"{indent}- 🔗 リンク: {self.base}/{alias_id.replace('-', '')}")
        elif t == "header":
            lines.append(f"\n## {title}\n")
            lines.extend(children())
        elif t == "sub_header":
            lines.append(f"\n### {title}\n")
            lines.extend(children())
        elif t == "sub_sub_header":
            lines.append(f"\n#### {title}\n")
            lines.extend(children())
        elif t == "text":
            lines.append(f"{indent}{title}" if title else "")
            lines.extend(children(1 if title else 0))
        elif t == "bulleted_list":
            lines.append(f"{indent}- {title}")
            lines.extend(children(1))
        elif t == "numbered_list":
            lines.append(f"{indent}1. {title}")
            lines.extend(children(1))
        elif t == "to_do":
            checked = props.get("checked", [["No"]])[0][0] == "Yes"
            lines.append(f"{indent}- [{'x' if checked else ' '}] {title}")
            lines.extend(children(1))
        elif t == "toggle":
            lines.append(f"{indent}- ▶ {title}")
            lines.extend(children(1))
        elif t == "quote":
            lines.append(f"{indent}> {title}")
            lines.extend(children())
        elif t == "callout":
            icon = b.get("format", {}).get("page_icon", "💡")
            if icon.startswith("/") or icon.startswith("http"):
                icon = "💡"
            lines.append(f"{indent}> {icon} {title}")
            for cid in b.get("content", []):
                for l in self.render(cid, blocks, attach_rel, child_pages, 0):
                    lines.append(f"{indent}> {l}")
        elif t == "code":
            lang = self.rich_text(props.get("language")) or ""
            lines.append(f"```{lang.lower()}\n{title}\n```")
        elif t == "image":
            src = props.get("source", [[""]])[0][0]
            if src:
                fname = self.download_image(src, bid)
                if fname:
                    lines.append(f"{indent}![image]({attach_rel}/{fname})")
                else:
                    lines.append(f"{indent}![image]({src})")
        elif t in ("video", "embed", "bookmark", "audio", "file", "pdf"):
            src = (props.get("source", [[""]])[0][0]
                   or b.get("format", {}).get("bookmark_url", ""))
            lines.append(f"{indent}🔗 {title or t}: {src}")
        elif t == "divider":
            lines.append("\n---\n")
        elif t in ("column_list", "column"):
            lines.extend(children())
        elif t == "table":
            rows = b.get("content", [])
            order = b.get("format", {}).get("table_block_column_order", [])
            for i, rid in enumerate(rows):
                rb = blocks.get(rid, {})
                rprops = rb.get("properties", {})
                cells = [self.rich_text(rprops.get(c)).replace("|", "\\|")
                         for c in order]
                lines.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    lines.append("|" + "---|" * len(order))
        elif t in ("collection_view", "collection_view_page"):
            # データベース: 全アイテムを子ページとして列挙
            view_ids = b.get("view_ids", [])
            cid = b.get("collection_id")
            if not cid and view_ids:
                # view の collection_pointer から取得
                cv = blocks.get(view_ids[0]) or {}
                cid = (cv.get("format", {}).get("collection_pointer", {}) or {}).get("id")
            if cid and view_ids:
                try:
                    item_ids, item_blocks = self.query_collection(cid, view_ids[0])
                    for iid in item_ids:
                        ib = item_blocks.get(iid)
                        if not ib:
                            continue
                        name = self.page_title(ib)
                        child_pages.append((iid, name))
                        lines.append(f"{indent}- 📄 [[{self.sanitize(name)}]]")
                except Exception as e:
                    lines.append(f"{indent}⚠️ データベースの取得に失敗: {e}")
            else:
                lines.append(f"{indent}⚠️ データベース（collection_id不明）をスキップ")
        else:
            if title:
                lines.append(f"{indent}{title}")
            lines.extend(children())
        return lines

    # ---------- ページ単位のエクスポート ----------

    def export_page(self, page_id, dir_path, is_top=False):
        if page_id in visited:
            return
        visited.add(page_id)
        try:
            record_map = self.load_all_blocks(page_id)
        except Exception as e:
            log(f"取得失敗: {page_id}: {e}")
            page_count["fail"] += 1
            return
        blocks = record_map["block"]
        # collection_view レコードもブロック辞書に混ぜて参照可能にする
        blocks.update(record_map["collection_view"])
        page = blocks.get(page_id)
        if not page:
            log(f"ページが見つからない: {page_id}")
            page_count["fail"] += 1
            return

        name = self.sanitize(self.page_title(page))
        os.makedirs(dir_path, exist_ok=True)
        attach_rel = os.path.relpath(self.attach_dir, dir_path)

        child_pages = []
        body_lines = self.render(page_id, blocks, attach_rel, child_pages)
        body = re.sub(r"\n{3,}", "\n\n", "\n".join(body_lines))

        fm = ["---",
              f"source: {self.base}/{page_id.replace('-', '')}",
              f"notion_created: {self.jst(page.get('created_time', 0))}",
              f"notion_updated: {self.jst(page.get('last_edited_time', 0))}",
              f"exported: {self.exported_at}",
              "---", ""]
        header = [f"# {self.plain(self.rich_text(page.get('properties', {}).get('title'))) or name}", ""]
        if is_top:
            header += [f"> 取得元: {self.base}/{page_id.replace('-', '')}",
                       f"> 取得日時: {self.exported_at} JST", "", ""]

        path = os.path.join(dir_path, name + ".md")
        # 同名衝突の回避
        i = 2
        while os.path.exists(path):
            path = os.path.join(dir_path, f"{name}_{i}.md")
            i += 1
        with open(path, "w") as f:
            f.write("\n".join(fm + header) + body + "\n")
        page_count["ok"] += 1
        log(f"[{page_count['ok']}] {os.path.relpath(path, self.out_dir)}"
            f"（子ページ {len(child_pages)}件）")

        # 子ページを再帰処理（子がいるページはフォルダを作ってその中へ）
        if child_pages:
            child_dir = os.path.join(dir_path, name) if not is_top else dir_path
            for cid, _ in child_pages:
                time.sleep(0.3)
                self.export_page(cid, child_dir)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    url, out_dir = sys.argv[1], sys.argv[2]
    m = re.search(r"([0-9a-f]{32})", url.replace("-", ""))
    if not m:
        # ハイフン付きUUIDにも対応
        m2 = re.search(r"([0-9a-f-]{36})", url)
        if not m2:
            print("URLからページIDを抽出できません:", url)
            sys.exit(1)
        pid_raw = m2.group(1).replace("-", "")
    else:
        pid_raw = m.group(1)
    page_id = (f"{pid_raw[0:8]}-{pid_raw[8:12]}-{pid_raw[12:16]}-"
               f"{pid_raw[16:20]}-{pid_raw[20:32]}")
    parsed = urllib.parse.urlparse(url if "://" in url else "https://" + url)
    base = f"https://{parsed.netloc}"

    ex = Exporter(base, out_dir)
    ex.export_page(page_id, out_dir, is_top=True)
    log(f"完了: ページ 成功 {page_count['ok']} / 失敗 {page_count['fail']}, "
        f"画像 成功 {img_stats['ok']} / 失敗 {img_stats['fail']}")


if __name__ == "__main__":
    main()
