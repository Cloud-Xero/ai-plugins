# xero-work

受託実務・解析パイプライン・開発補助のスキル/エージェント群。

## スキル

| スキル | 説明 |
|--------|------|
| `/excel-analyze` | Excelブックの解析パイプライン（4エージェント直列起動） |
| `/refactor-plan` | リファクタリング計画書の作成パイプライン（実測→計画書執筆） |
| `/refactor-page` | リファクタリング計画の実行オーケストレータ（worktree 隔離で実装・検証 → stacked PR 作成） |
| `/doctor` | 「Macが重い」の原因を実測で特定する診断スキル |
| `/example-skill` | 新スキル作成用の雛形サンプル |

## エージェント

| エージェント | 役割 |
|--------|------|
| `excel-inventory` | Excel構造棚卸し（excel-analyze 第1工程） |
| `excel-dep-graph` | 数式依存グラフ構築（第2工程） |
| `excel-logic-spec` | 計算ロジック仕様書化（第3工程） |
| `excel-snapshot` | 回帰テスト用スナップショット採取（第4工程） |
| `proposal-writer` | 受託案件の提案書・見積ドラフト作成 |
| `pm-estimator` | 工数見積・WBS・スケジュール・リスク分解 |
| `qa-test-designer` | テスト観点洗い出し・テストケース設計 |
| `refactor-plan-analyzer` | リファクタ対象の実測・構造分析（refactor-plan 第1工程） |
| `refactor-plan-writer` | 実測をもとに計画書を執筆（第2工程） |
| `refactor-implementer` | 計画の PR ステップ 1 つを worktree 隔離で実装→検証→push（refactor-page から呼ばれる） |
| `refactor-verifier` | push 済みブランチを挙動不変の観点で検証し PASS/FAIL を返す（同上） |

## excel-analyze（Excel解析パイプライン）

複雑なExcelブックをWebアプリ移植に向けて解析するスキル。`/excel-analyze <path>` で呼び出すと、4つの専用エージェントを直列（3・4のみ並列）に起動し、`excel_analysis/<ブック名>/` に成果物を出力する。

| 工程 | エージェント | 出力 |
|---|---|---|
| 1. 構造棚卸し | `excel-inventory` | `01_inventory.json` / `01_inventory.md` |
| 2. 数式依存グラフ | `excel-dep-graph` | `02_dependencies.json` / `02_dependency-graph.md` |
| 3. ロジック仕様書 | `excel-logic-spec` | `03_logic-spec.md` |
| 4. 回帰テスト用スナップショット | `excel-snapshot` | `04_snapshot.json` / `04_test-cases.md` |

エージェント定義は `agents/`、オーケストレーションは `skills/excel-analyze/` にある。

## refactor-plan（リファクタリング計画書の作成）

肥大化したページ・feature・モジュールを**挙動不変のまま**段階的に解体する計画書を `docs/refactoring/<対象>.md` として作るスキル。`/refactor-plan [対象]` で呼び出す。対象を省略すると行数ランキングから候補を提示する。

| 工程 | 担当 | 出力 |
|---|---|---|
| 0. 対象決定・前提収集 | スキル本体 | 対象リスト・制約リスト（CLAUDE.md / メモリ / テスト基盤の現状） |
| 1. 実測と構造分析 | `refactor-plan-analyzer`（対象ごとに並列） | `<一時ディレクトリ>/<対象>-analysis.md`（中間物、repo 外） |
| 2. 計画書の執筆 | `refactor-plan-writer` | `docs/refactoring/<対象>.md` |
| 3. 索引の更新 | スキル本体 | `docs/refactoring/README.md` |

計画書の雛形は `skills/refactor-plan/plan-template.md`。原則は「全 PR 挙動不変」「1 PR = 1 構造変更・独立マージ可能」「抽出順序は 型 → 純関数 → フック → 表示部品」「PR1 は必ず安全網（characterization テスト）」。**このスキルはコードを変更しない**（計画の実行は refactor-page の領分）。

## refactor-page（リファクタリング計画の実行）

refactor-plan が生成した計画（`docs/refactoring/<対象>.md`）を読み、未実施の PR ステップを洗い出して、サブエージェント（`refactor-implementer` → `refactor-verifier`）に git worktree 隔離で実装・検証させ、残り全ステップぶんの **stacked PR** を一気通貫で作成するオーケストレータ。`/refactor-page [計画名]` で呼び出す（`lists PR 3` で単発、`lists from 3` で途中から）。

- 1 PR ステップ = 1 PR。PR N の base = PR N-1 のブランチ（ユーザーは番号順にマージするだけ）
- verifier が FAIL → implementer に fix で差し戻し（最大 2 往復）。通らなければそこで打ち切る
- 最終ステップの PR に計画 md 自体の削除を含め、refactoring フォルダを最終的に空にする
- **特定プロジェクトに依存しない**: 検証コマンド・規約・PR テンプレート等は工程 0 でリポジトリから実測・収集し、「リポジトリ事実」としてエージェントに毎回渡す
- スキル自身はコードを書かない。マージもしない
