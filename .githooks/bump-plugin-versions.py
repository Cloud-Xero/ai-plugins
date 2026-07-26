#!/usr/bin/env python3
"""直前のコミットの内容から、変更されたプラグインの version を自動で bump する。

post-commit フックから呼ばれる。書き換えたファイルのパスを 1 行ずつ標準出力に返し、
呼び出し元がそれを git add して --amend する。

bump 種別は Conventional Commits のプレフィックスで決める。
  feat!: / fix!: / BREAKING CHANGE  -> major
  feat:                             -> minor
  それ以外 (fix / docs / chore ...) -> patch

対象プラグインは marketplace.json の plugins[].source から解決するため、
`source: "./plugins/foo"` のマルチプラグイン型と `source: "./"` の
単一プラグイン型（リポジトリルートがプラグイン）の両方に対応する。

次の場合は対象から外す。
  - そのコミットで既に version が変わっている (手動 bump の尊重・二重 bump の防止)
  - plugin.json がそのコミットで新規追加された (初期バージョンをそのまま使う)
  - version が未設定 (コミット SHA 運用) / semver 形式でない
"""

import json
import os
import re
import subprocess
import sys

MARKETPLACE = ".claude-plugin/marketplace.json"
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# プラグインルートがリポジトリルートと同じとき、変更検知の対象にする構成要素。
# docs/ や README.md の変更で bump しないよう、実在する構成要素に限定する。
# marketplace.json は挙動を変えないため、トリガーには含めず同期先としてのみ扱う。
# 構成要素が増えたらここに足す。
PLUGIN_COMPONENTS = (
    ".claude-plugin/plugin.json",
    "skills/",
    "commands/",
    "agents/",
    "hooks/",
    ".mcp.json",
)


def git(*args):
    """git を実行して標準出力を返す。失敗したら None。"""
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def bump_kind(message):
    """コミットメッセージから bump 種別を判定する。"""
    subject = message.split("\n", 1)[0]
    body = message[len(subject):]

    # 破壊的変更: `feat!:` `refactor(api)!:` などの `!`、または本文の BREAKING CHANGE
    if re.match(r"^[a-zA-Z]+(\([^)]*\))?!:", subject):
        return "major"
    if re.search(r"^BREAKING[ -]CHANGE:", body, re.MULTILINE):
        return "major"

    if re.match(r"^feat(\([^)]*\))?:", subject):
        return "minor"

    return "patch"


def next_version(current, kind):
    """semver を 1 段階上げる。semver でなければ None。"""
    m = SEMVER.match(current)
    if not m:
        return None
    major, minor, patch = (int(x) for x in m.groups())

    if kind == "major":
        return f"{major + 1}.0.0"
    if kind == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def read_version(text):
    """JSON テキストから version の値を取り出す。"""
    m = re.search(r'"version"\s*:\s*"([^"]*)"', text)
    return m.group(1) if m else None


def replace_version(text, new):
    """JSON テキストの最初の version の値だけを差し替える。

    json.dump で組み直すと整形やキー順、日本語のエスケープが変わってしまうため、
    テキスト上の置換にとどめる。
    """
    return re.sub(
        r'("version"\s*:\s*")[^"]*(")',
        lambda m: m.group(1) + new + m.group(2),
        text,
        count=1,
    )


def normalize_source(source):
    """marketplace の source をリポジトリルートからの相対ディレクトリに正規化する。

    "./" や "." はリポジトリルート自身を指すので空文字を返す。
    """
    s = (source or "").strip()
    s = re.sub(r"^\./", "", s)
    s = s.strip("/")
    return "" if s == "." else s


def plugin_roots():
    """プラグインのルートディレクトリ一覧を返す。

    marketplace.json の source を主に使い、そこに載っていない plugins/<name>/ も
    取りこぼさないよう補う。
    """
    roots = []

    if os.path.exists(MARKETPLACE):
        try:
            with open(MARKETPLACE, encoding="utf-8") as f:
                data = json.load(f)
            for entry in data.get("plugins", []):
                # エントリが文字列などの想定外の型でも bump 全体を止めない
                if not isinstance(entry, dict):
                    continue
                source = entry.get("source")
                # source がオブジェクト形式（git/github 参照）のものは別リポジトリなので対象外
                if not isinstance(source, str):
                    continue
                root = normalize_source(source)
                if root not in roots:
                    roots.append(root)
        except (ValueError, OSError, AttributeError, TypeError):
            pass

    if os.path.isdir("plugins"):
        for name in sorted(os.listdir("plugins")):
            root = f"plugins/{name}"
            if root not in roots and os.path.isfile(
                f"{root}/.claude-plugin/plugin.json"
            ):
                roots.append(root)

    return roots


def touches_plugin(path, root):
    """変更ファイルがそのプラグインの構成要素かどうかを判定する。"""
    if root:
        return path == root or path.startswith(root + "/")

    # プラグインルートがリポジトリルートの場合は構成要素だけを見る
    for component in PLUGIN_COMPONENTS:
        if component.endswith("/"):
            if path.startswith(component):
                return True
        elif path == component:
            return True
    return False


def entry_spans(text):
    """marketplace.json のテキスト上で、plugins 配列の直下要素の範囲を列挙する。

    JSON 全体を組み直さずに済ませることで、既存の整形やキー順を壊さない。
    エントリ内にネストしたオブジェクト（author など）を掴まないよう、
    深さ 0 の `{` だけをエントリの開始として扱い、文字列リテラル内の括弧は無視する。
    """
    m = re.search(r'"plugins"\s*:\s*\[', text)
    if not m:
        return []

    spans = []
    depth = 0
    start = None
    in_string = False
    escaped = False

    for i in range(m.end(), len(text)):
        c = text[i]

        if in_string:
            if escaped:
                escaped = False
            elif c == "\\":
                escaped = True
            elif c == '"':
                in_string = False
            continue

        if c == '"':
            in_string = True
        elif c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                spans.append((start, i + 1))
                start = None
        elif c == "]" and depth == 0:
            break

    return spans


def entry_span(text, root):
    """marketplace.json のテキスト上で、該当プラグインのエントリの範囲を返す。"""
    if root:
        pattern = r'"source"\s*:\s*"(?:\./)?' + re.escape(root) + r'/?"'
    else:
        pattern = r'"source"\s*:\s*"\.(?:/)?"'

    for start, end in entry_spans(text):
        if re.search(pattern, text[start:end]):
            return start, end
    return None


def main():
    top = git("rev-parse", "--show-toplevel")
    if not top:
        return 0
    os.chdir(top.strip())

    message = git("log", "-1", "--pretty=%B")
    if message is None:
        return 0
    kind = bump_kind(message)

    # 直前のコミットで変更されたファイル。root commit でも動くよう --root を付ける
    listing = git("diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "HEAD")
    if not listing:
        return 0
    files = [f for f in listing.splitlines() if f]

    has_parent = git("rev-parse", "-q", "--verify", "HEAD^") is not None

    marketplace_text = None
    if os.path.exists(MARKETPLACE):
        with open(MARKETPLACE, encoding="utf-8") as f:
            marketplace_text = f.read()
    marketplace_changed = False

    written = []

    for root in plugin_roots():
        if not any(touches_plugin(f, root) for f in files):
            continue

        manifest = f"{root}/.claude-plugin/plugin.json" if root else ".claude-plugin/plugin.json"
        if not os.path.exists(manifest):
            # プラグインごと削除された場合など
            continue

        with open(manifest, encoding="utf-8") as f:
            manifest_text = f.read()

        current = read_version(manifest_text)
        if current is None:
            # version 未設定はコミット SHA 運用。触らない
            continue

        if not has_parent:
            # root commit は全ファイルが新規追加。初期バージョンを尊重する
            continue

        previous_text = git("show", f"HEAD^:{manifest}")
        if previous_text is None:
            # このコミットで新規追加されたプラグイン。初期バージョンを尊重する
            continue
        if read_version(previous_text) != current:
            # 既にこのコミットで version が変わっている
            continue

        label = root or os.path.basename(os.getcwd())

        new = next_version(current, kind)
        if new is None:
            print(
                f"[bump] {label}: version '{current}' は semver 形式ではないため据え置き",
                file=sys.stderr,
            )
            continue

        with open(manifest, "w", encoding="utf-8") as f:
            f.write(replace_version(manifest_text, new))
        written.append(manifest)

        # marketplace.json 側にも version があれば同じ値に揃える
        if marketplace_text is not None:
            span = entry_span(marketplace_text, root)
            if span:
                start, end = span
                entry = marketplace_text[start:end]
                if read_version(entry) is not None:
                    marketplace_text = (
                        marketplace_text[:start]
                        + replace_version(entry, new)
                        + marketplace_text[end:]
                    )
                    marketplace_changed = True

        print(f"[bump] {label}: {current} -> {new} ({kind})", file=sys.stderr)

    if marketplace_changed:
        with open(MARKETPLACE, "w", encoding="utf-8") as f:
            f.write(marketplace_text)
        written.append(MARKETPLACE)

    for path in written:
        print(path)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # フックの失敗でコミットを壊さない
        print(f"[bump] スキップしました: {e}", file=sys.stderr)
        sys.exit(0)
