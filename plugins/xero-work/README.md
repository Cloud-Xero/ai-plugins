# xero-work

受託実務・解析パイプライン・開発補助のスキル/エージェント群。

## スキル

| スキル | 説明 |
|--------|------|
| `/excel-analyze` | Excelブックの解析パイプライン（4エージェント直列起動） |
| `/harvest` | 現在のセッションから収穫ノートを抽出・保存 |
| `/harvest-docs` | プロジェクト内 docs から収穫ノートを生成 |
| `/ai-news` | AI業界ニュースの収集・日本語解説レポート生成 |
| `/allow-perms` | セッション中の permission prompt を allowlist に追加 |
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
| `ai-news-reporter` | AI業界ニュースの調査・執筆（ai-news から委譲） |

## excel-analyze（Excel解析パイプライン）

複雑なExcelブックをWebアプリ移植に向けて解析するスキル。`/excel-analyze <path>` で呼び出すと、4つの専用エージェントを直列（3・4のみ並列）に起動し、`excel_analysis/<ブック名>/` に成果物を出力する。

| 工程 | エージェント | 出力 |
|---|---|---|
| 1. 構造棚卸し | `excel-inventory` | `01_inventory.json` / `01_inventory.md` |
| 2. 数式依存グラフ | `excel-dep-graph` | `02_dependencies.json` / `02_dependency-graph.md` |
| 3. ロジック仕様書 | `excel-logic-spec` | `03_logic-spec.md` |
| 4. 回帰テスト用スナップショット | `excel-snapshot` | `04_snapshot.json` / `04_test-cases.md` |

エージェント定義は `agents/`、オーケストレーションは `skills/excel-analyze/` にある。

## harvest（セッション収穫）

`/harvest [出力先]` で現在のセッションから「やったこと・設計判断・ハマり→解決・申し送り」を収穫ノート1ファイル（`yyyymmdd_{slug}.md`）に抽出する汎用スキル。出力先は 引数 > プロジェクトCLAUDE.mdの `harvest` 規約 > `./docs/harvest/` の順で解決する。テンプレートは `skills/harvest/note-template.md`。

obsidian-tech では出力先を `input/memo/` に規約化しており、収穫ノートをそのまま記事ネタとして `/capture` の査定に回せる。

## ai-news（AI業界ニュース収集）

`/ai-news [期間や対象の指定]` で Anthropic / OpenAI / Google（Gemini）/ xAI（Grok）の最新ニュースを収集し、日本語解説レポートを生成する。調査・執筆は `ai-news-reporter` エージェント（`agents/ai-news-reporter.md`）に委譲。デフォルトは直近1日・4社。出力先は環境変数 `AI_NEWS_OUTPUT_DIR`（`~/.claude/settings.json` の `env` で設定、未設定なら設定を促して停止）で、ファイル名は `YYYY-MM-DD_ai-news.md`。
