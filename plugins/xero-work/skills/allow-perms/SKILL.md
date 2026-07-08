---
name: allow-perms
description: 現在のセッション中に許可確認（permission prompt）を求められたコマンド・ツールを抽出し、ユーザースコープ（~/.claude/settings.json）かプロジェクトスコープ（<project>/.claude/settings.json）かを選ばせた上で permissions.allow に追加して今後の確認を不要にする。「このコマンドを許可して」「permission を追加して」「毎回聞かれないようにして」と言われたとき、または /allow-perms で呼び出されたときに使用。
---

@INSTRUCTIONS.md
