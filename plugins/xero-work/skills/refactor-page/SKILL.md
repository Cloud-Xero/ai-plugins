---
name: refactor-page
description: docs/refactoring/ のリファクタリング計画（refactor-plan スキルが生成する形式）を 1 ファイル読み、コードベースの現状から未実施の PR ステップを洗い出し、サブエージェント（refactor-implementer → refactor-verifier）に git worktree 隔離で実装・検証させて、残り全ステップぶんの PR を一気通貫で作成するオーケストレータ。1 PR ステップ = 1 PR の粒度は維持し、依存する PR は stacked（PR N の base = PR N-1 のブランチ）で積む。ステップ番号を明示すればそのステップだけの単発実行も可能。計画の最終ステップの PR には計画 md 自体の削除を含め、最終的に refactoring フォルダを空にする。スキル自身はコードを書かない。検証コマンドやプロジェクト規約はリポジトリごとに実測・収集してエージェントに渡す（特定プロジェクトに依存しない）。「リファクタリングを進めて」「〜のリファクタ計画を実行して」と言われたとき、または /refactor-page [計画名] で呼び出されたときに使用。計画書の作成は refactor-plan の領分。
---

@INSTRUCTIONS.md
