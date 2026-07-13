---
name: notion-to-md
description: 公開Notionページ（notion.site）を子ページ・データベースも含めて再帰的にMarkdownエクスポートする。各ページのfrontmatterにNotion上の作成/更新日時と元ページURLを記録し、トップページには取得元URLと取得日時を記載、画像はattachments/へローカル保存する。「このNotionページをmdで保存して」「Notionをエクスポートして」と言われたとき、または /notion-to-md <URL> [出力先] で呼び出されたときに使う。認証が必要な非公開ページは対象外。
argument-hint: '<NotionページURL> [出力先ディレクトリ(省略時は確認)]'
---

@INSTRUCTIONS.md
