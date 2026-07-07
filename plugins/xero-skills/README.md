# xero-skills

個人用スキルコレクション。現在の中心は **pj-系スキル群**（新規サービス開発ワークフロー）。

## pj-系スキル群

サービス開発を段階的に進めるためのスキルセット。
命名規則は **`pj-<工程番号>-<工程名>`**（例: `/pj-1-service-design`）。番号が工程の順序を表す。

### ワークフローと実装状況

| 工程 | スキル | 出力 | 状況 |
|---|---|---|---|
| 1. サービス設計 | `/pj-1-service-design` | `pj_<name>/01_service-definition.md` | ✅ |
| 2. ビジネスモデル | `/pj-2-business-model` | `pj_<name>/02_business-model.md` | ✅ |
| 3. MVP定義 | `/pj-3-mvp` | `pj_<name>/03_mvp-definition.md` | 未実装 |
| 4. ユーザーストーリー | `/pj-4-user-story` | `pj_<name>/04_user-story.md` | 未実装 |
| 5. 技術設計 | `/pj-5-tech-stack` | `pj_<name>/05_tech-stack.md` | 未実装 |
| 8. マーケティング | `/pj-7-marketing` | （未定） | 未実装 |

工程6〜9（開発・検証・ローンチ・改善）は汎用スキル（`/commit` 等）やClaude Code本体で対応し、専用スキルは必要になったら追加する。

### 出力先の規約

- 出力は**実行時のカレントプロジェクト**（例: obsidian-business vault）に作られる
- プロジェクトディレクトリ: `pj_` プレフィックス + 英語ケバブケース（例: `pj_ai-writing-tool`）
- 各工程の出力ファイルは `<工程番号2桁>_<内容>.md` で番号順に揃える

### セットとしての設計

- 各スキルのdescriptionに前後工程への参照を明記する（例: pj-1は「後工程は /pj-2-business-model」）
- 新しい工程スキルを追加するときは、この表と前後スキルのdescriptionを更新すること

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

## 将来のアイデア

- **pj-0ナビゲーター**: `pj_*` フォルダ内の成果物を見て「完了済み工程と次にやる工程」を診断するスキル。pj-3以降が揃ってから作る
