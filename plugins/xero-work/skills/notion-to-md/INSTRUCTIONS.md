# notion-to-md

公開Notionページ（`*.notion.site`）を、子ページ・データベース（コレクション）も含めて再帰的にMarkdownへエクスポートする。処理の実体は `scripts/export.py`（Python 3 標準ライブラリのみ、venv不要）。

このスキルのベースディレクトリはシステムから `Base directory for this skill:` として提供される。以下 `{skill_base_dir}` はそのパスに読み替えること。

## 前提と制限

- **公開ページ専用**。認証が必要な非公開ページはエラーになる。その場合はユーザーにページを「Webで公開」してもらうか、Notion MCP連携を案内する
- Notionの非公式API（`/api/v3/loadPageChunk`, `/api/v3/queryCollection`）を利用しているため、Notion側の仕様変更で動かなくなる可能性がある。失敗時はエラー内容をそのまま報告する

## 実行手順

### 1. 引数の確認

`$ARGUMENTS` から以下を読み取る:

- **NotionページURL**（必須）: `https://xxx.notion.site/...` 形式。URLが無ければユーザーに確認して停止する
- **出力先ディレクトリ**（任意）: 未指定なら AskUserQuestion で確認する。既存ディレクトリを指定された場合は上書きの可能性がある旨を伝える

### 2. 疎通確認（1ページだけ試す）

いきなり全件を走らせず、まずトップページ1件だけAPIが通るか確認する:

```bash
curl -s -X POST '<base>/api/v3/loadPageChunk' \
  -H 'Content-Type: application/json' \
  --data '{"pageId":"<UUID形式のページID>","limit":10,"cursor":{"stack":[]},"chunkNumber":0,"verticalColumns":false}' | head -c 500
```

- ページIDはURL末尾の32桁hexを `8-4-4-4-12` のUUID形式に変換したもの
- タイトルが返ればOK。エラーや空なら非公開ページの可能性が高いので停止して報告する

### 3. 本実行（バックグラウンド）

ページ数が多いと数分かかるため、`run_in_background: true` で実行する:

```bash
python3 {skill_base_dir}/scripts/export.py "<NotionURL>" "<出力先ディレクトリ>"
```

進捗は出力ファイルを Monitor で監視する（10件ごと・失敗・完了行を通知）。実行中はユーザーに進捗を報告する。

### 4. 結果の検証

完了後、以下を確認して報告する:

1. 最終行の `完了: ページ 成功 N / 失敗 M, 画像 成功 X / 失敗 Y`
2. 失敗があれば出力ログから対象を特定して報告する
3. 「無題_xxxxxxxx.md」ファイルが無いか確認する。あれば中身を見て、本文からタイトルが判別できるならリネーム（本文冒頭の見出しや太字を使う）、完全に空なら削除を**ユーザーに提案**する（勝手に消さない）
4. サンプルとして1記事の冒頭をユーザーに提示し、品質を確認してもらう

## 出力仕様（スクリプトが保証する内容）

- **各ページのfrontmatter**（必須）:

  ```yaml
  ---
  source: https://xxx.notion.site/<ページID>
  notion_created: YYYY-MM-DD HH:MM   # Notion上の作成日時(JST)
  notion_updated: YYYY-MM-DD HH:MM   # Notion上の最終更新日時(JST)
  exported: YYYY-MM-DD HH:MM         # 取得日時(JST)
  ---
  ```

- **トップページ**: frontmatterに加え、本文冒頭に `> 取得元: <URL>` と `> 取得日時: <日時> JST` を記載
- **階層構造**: 子ページを持つページは同名フォルダを作り、子ページのmdをその中に保存（Notionの階層をミラー）
- **子ページへのリンク**: Obsidianの `[[ページ名]]` 形式（ファイル名で解決されるためフォルダ階層に依存しない）
- **画像**: 出力先直下の `attachments/` にダウンロードし、各mdから相対パスで参照。ダウンロード失敗時は元URLのまま残す
- **データベース**: ビューの全アイテムをリンク一覧として展開し、各アイテムページも再帰的にエクスポートする
- **重複訪問防止**: 同一ページは1回だけ処理（循環参照対策）

## 追加の整理（ユーザーの要望があれば）

- 章・カテゴリごとのフォルダ分け（データベースのselectプロパティ等に基づく）はスクリプトの対象外。要望があればエクスポート後にファイル移動＋画像相対パス修正（`](attachments/` → `](../attachments/`）で対応する
