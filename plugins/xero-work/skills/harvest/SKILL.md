---
name: harvest
description: 現在のセッションから「やったこと・設計判断・ハマり→解決・申し送り」を収穫ノート1ファイルに抽出して保存する。作業の区切りで「このセッションを収穫して」「作業ログ残して」と言われたとき、または /harvest で呼び出されたときに使う。どのプロジェクトでも使える汎用スキルで、出力先は環境変数 HARVEST_OUTPUT_DIR（~/.claude/settings.json の env で設定）。未設定の場合は設定を促して停止する。
---

@INSTRUCTIONS.md
