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

## 将来のアイデア

- **pj-0ナビゲーター**: `pj_*` フォルダ内の成果物を見て「完了済み工程と次にやる工程」を診断するスキル。pj-3以降が揃ってから作る
