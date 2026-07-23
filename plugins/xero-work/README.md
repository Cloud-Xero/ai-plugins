# xero-work

受託実務・解析パイプライン・開発補助のスキル/エージェント群。

## スキル

| スキル | 説明 |
|--------|------|
| `/excel-analyze` | Excelブックの解析パイプライン（4エージェント直列起動） |
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

## excel-analyze（Excel解析パイプライン）

複雑なExcelブックをWebアプリ移植に向けて解析するスキル。`/excel-analyze <path>` で呼び出すと、4つの専用エージェントを直列（3・4のみ並列）に起動し、`excel_analysis/<ブック名>/` に成果物を出力する。

| 工程 | エージェント | 出力 |
|---|---|---|
| 1. 構造棚卸し | `excel-inventory` | `01_inventory.json` / `01_inventory.md` |
| 2. 数式依存グラフ | `excel-dep-graph` | `02_dependencies.json` / `02_dependency-graph.md` |
| 3. ロジック仕様書 | `excel-logic-spec` | `03_logic-spec.md` |
| 4. 回帰テスト用スナップショット | `excel-snapshot` | `04_snapshot.json` / `04_test-cases.md` |

エージェント定義は `agents/`、オーケストレーションは `skills/excel-analyze/` にある。
