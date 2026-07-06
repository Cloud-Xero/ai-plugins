# サブエージェント カタログ設計

個人事業主（Cloud-Xero）が、大企業に劣らない成果を出すための「顧問チーム／専門部門」を
サブエージェント・スキルとして揃えるためのカタログ。

- 事業モード: **受託開発・制作** ＋ **自社サービス・SaaS** の両輪
- 対象領域: 集客・案件獲得 / 守り（財務・法務・運用） / 戦略・意思決定 / 制作・開発（全方位）

---

## 設計原則：サブエージェント向きの仕事とそうでない仕事

サブエージェントは **「独立した文脈で一気に処理し、成果物を1回返す」** のが得意。
逆に **対話的な壁打ち（戦略相談など）は1往復で終わるため不向き**で、スキルか通常会話が向く。
既存の `excel-analyze`（4エージェントの直列パイプライン）はサブエージェント活用の理想形。

各役割を次の2タイプに分類する。

- **【A】サブエージェント向き** … 調査・レビュー・生成・変換など、委譲して並列に回せる仕事
- **【S】スキル/会話向き** … 戦略・意思決定など、往復しながら詰める仕事

---

## 全体カタログ（4本柱）

### 1. 戦略・意思決定 — 一人だと最も手薄になる司令塔

| 役割 | タイプ | 何をするか | 既存資産 / 状態 |
|---|---|---|---|
| 事業戦略アドバイザー | 【S】 | 注力/撤退、優先順位、価格・方向性の壁打ち | ✅ **作成済み** `skills/biz-strategy/`（opus） |
| 市場・競合リサーチャー | 【A】 | 市場規模・競合・技術動向を調べ切って報告 | ✅ **作成済み** `agents/market-researcher.md`（sonnet） |
| 意思決定レビュアー | 【A】 | ある判断を「反証する側」で叩き、抜けを出す | ✅ **作成済み** `agents/decision-reviewer.md`（opus） |

### 2. 集客・案件獲得 — 大企業と最も差がつく営業機能

| 役割 | タイプ | 何をするか | 既存資産 / 状態 |
|---|---|---|---|
| マーケ戦略家 | 【S】 | ターゲット・ポジショニング・チャネル設計の司令塔 | ✅ **作成済み** `skills/marketing-strategy/`（opus）— `lp-1-strategy` の上位 |
| 提案・見積ライター | 【A】 | 受託の提案書/見積/商談トークを生成 | ✅ **作成済み** `agents/proposal-writer.md`（sonnet） |
| コンテンツ/SEO編集者 | 【A】 | 集客記事の構成・SEO改善を量産 | ✅ **作成済み** `agents/content-seo-editor.md`（sonnet）— `seo-audit` / `note-draft` と連携 |
| SNS運用ライター | 【A】 | SNS投稿の企画・量産・カレンダー設計・型分析 | ✅ **作成済み** `agents/sns-content-writer.md`（sonnet） |
| 広告運用担当 | 【A】 | 広告のキャンペーン設計・広告文量産・成果分析 | ✅ **作成済み** `agents/ad-operations.md`（sonnet） |

### 3. 制作・開発 — 既にスキルが厚い領域（専任化で補強）

| 役割 | タイプ | 何をするか | 既存資産 / 状態 |
|---|---|---|---|
| ソフトウェアアーキテクト | 【A】 | 実装前の設計・トレードオフ整理 | ➖ **既存で充足**（組み込み `Plan` エージェント）。重複定義は作らない |
| コードレビュアー | 【A】 | 差分をバグ/簡潔性で厳格レビュー | ➖ **既存で充足**（`code-review` / `local-review`）。重複定義は作らない |
| QA・テスト設計 | 【A】 | 観点洗い出しとテストケース生成 | ✅ **作成済み** `agents/qa-test-designer.md`（sonnet） |

### 4. 守り — 一人だと後回しにして事故る領域

| 役割 | タイプ | 何をするか | 既存資産 / 状態 |
|---|---|---|---|
| 財務・会計アドバイザー | 【S】 | 資金繰り・価格戦略・税務観点の相談 | ✅ **作成済み** `skills/finance-advisor/`（opus） |
| 法務・契約チェッカー | 【A】 | 契約書/利用規約/下請法のリスク検知 | ✅ **作成済み** `agents/contract-reviewer.md`（opus） |
| PM・工数見積 | 【A】 | 受託の工数見積・スケジュール・リスク分解 | ✅ **作成済み** `agents/pm-estimator.md`（sonnet） |
| カスタマーサクセス設計 | 【S】 | SaaSの解約防止・LTV向上・オンボ設計 | ✅ **作成済み** `skills/cs-design/`（sonnet） |

---

## 実装ロードマップ

### フェーズ1：最初に作る3体（費用対効果最大） ✅ 完了

「受託の受注力」と「守りの穴」を同時に埋める。いずれも【A】でありすぐ実装できる。

1. ✅ **提案・見積ライター** — `agents/proposal-writer.md`（sonnet）。要件メモ → 提案書＋見積を生成
2. ✅ **法務・契約チェッカー** — `agents/contract-reviewer.md`（opus）。受託契約・SaaS利用規約のリスクを検知
3. ✅ **市場・競合リサーチャー** — `agents/market-researcher.md`（sonnet）。新サービス判断も受託提案の裏付けも支える調査専任

> 反映には再インストールが必要（`claude plugin marketplace add "$(pwd)"` → `claude plugin install xero-skills@cloud-xero-plugins`）

### フェーズ2：制作・開発の専任化 ✅ 完了

- ✅ QA・テスト設計 — `agents/qa-test-designer.md`（sonnet）
- ✅ 意思決定レビュアー — `agents/decision-reviewer.md`（opus）
- ✅ PM・工数見積 — `agents/pm-estimator.md`（sonnet）
- ✅ コンテンツ/SEO編集者 — `agents/content-seo-editor.md`（sonnet）
- ➖ ソフトウェアアーキテクト / コードレビュアーは既存（`Plan` / `code-review`）で充足と判断し、重複定義は作らない

### フェーズ3：戦略・守りの【S】系 ✅ 完了

戦略・財務・CS系はサブエージェントより **スキル**（一層構造・対話型）として実装した。

- ✅ 事業戦略アドバイザー — `skills/biz-strategy/`（opus）
- ✅ マーケ戦略家 — `skills/marketing-strategy/`（opus）
- ✅ 財務・会計アドバイザー — `skills/finance-advisor/`（opus）
- ✅ カスタマーサクセス設計 — `skills/cs-design/`（sonnet）

## エキスパートチーム間の連携マップ

- `/biz-strategy`（司令塔）→ 反証は `decision-reviewer`、事実確認は `market-researcher`
- `/marketing-strategy` → LP は `/lp-1〜4`、記事量産は `content-seo-editor`、SNS投稿は `sns-content-writer`、広告は `ad-operations`、競合調査は `market-researcher`
- 広告の流れ: `/marketing-strategy`（出稿判断）→ `/lp-1〜4`（受け皿）→ `ad-operations`（設計・文案・分析）。経済性は `/finance-advisor` と整合させる
- コンテンツ再利用の流れ: `/harvest`（セッション収穫）や記事 → `sns-content-writer` で投稿に分解
- 受託案件: `market-researcher`（裏付け）→ `proposal-writer`（提案）→ `pm-estimator`（工数・計画）→ `contract-reviewer`（契約）→ `qa-test-designer`（品質）
- `/finance-advisor` → 相場調査は `market-researcher`。税務の最終判断は税理士へ
- `/cs-design` → SaaS運用の仕組み化。改善はプロダクト開発フローへ

---

## 実装メモ

- サブエージェントは `apsis-common:add-agent` で scaffold する
- スキルは `plugins/xero-skills/skills/<name>/` に SKILL.md + INSTRUCTIONS.md（二層構造）
- 反映には再インストールが必要（`claude plugin marketplace add` → `claude plugin install`）
