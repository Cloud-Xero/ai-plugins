# ai-plugins

Cloud-Xero 個人用の Claude Code プラグイン（スキル）カタログです。スキルとエージェントをドメインごとに 3 つのプラグインへ分けて管理します。

| プラグイン | ドメイン | 中身 |
|--------|------|------|
| [xero-biz](./plugins/xero-biz/) | 経営・事業判断 | 事業戦略・財務・サービス設計・判断の反証・契約チェック・市場調査 |
| [xero-marketing](./plugins/xero-marketing/) | 集客・販促 | マーケ戦略・CS設計・広告運用・SEOコンテンツ・SNS運用 |
| [xero-work](./plugins/xero-work/) | 受託実務・開発補助 | Excel解析・提案書・工数見積・QA・収穫ノート・AIニュース |

## セットアップ

```bash
git clone https://github.com/Cloud-Xero/ai-plugins.git
cd ai-plugins

# マーケットプレイスを登録してプラグインをインストール（必要なものだけでも可）
claude plugin marketplace add "$(pwd)"
claude plugin install xero-biz@cloud-xero-plugins
claude plugin install xero-marketing@cloud-xero-plugins
claude plugin install xero-work@cloud-xero-plugins
```

## 更新

```bash
git pull
claude plugin install xero-biz@cloud-xero-plugins
claude plugin install xero-marketing@cloud-xero-plugins
claude plugin install xero-work@cloud-xero-plugins
```

> Claude Code はスキルをキャッシュにコピーして管理するため、`git pull` だけでは反映されません。

## スキルの呼び出し方

```
/<plugin-name>:<skill-name>
```

例: `/xero-work:harvest`、`/xero-biz:biz-strategy`

## スキルを追加する

追加先のドメインプラグインを選び、`plugins/<plugin-name>/skills/<skill-name>/` に 2 ファイルを作成します（apsis 由来の二層構造）。

- `SKILL.md` — frontmatter（`name`＝ディレクトリ名 / `description`＝どんなときに使うかを具体的に）＋ `INSTRUCTIONS.md` への参照 1 行
- `INSTRUCTIONS.md` — 実際の手順・知識

雛形は [example-skill](./plugins/xero-work/skills/example-skill/) をコピーして使ってください。

スキルから委譲されるエージェントは、そのスキルと**同じプラグイン**の `agents/` に置きます。

## 構成

```
ai-plugins/
├── .claude-plugin/
│   └── marketplace.json          # マーケットプレイス定義
├── plugins/
│   ├── xero-biz/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/<skill-name>/
│   │   │   ├── SKILL.md          # frontmatter + INSTRUCTIONS.md への参照
│   │   │   └── INSTRUCTIONS.md   # 実際の手順・知識
│   │   └── agents/<agent-name>.md
│   ├── xero-marketing/           # 同上
│   └── xero-work/                # 同上
├── CLAUDE.md
└── README.md
```

各プラグインのスキル/エージェント一覧は、それぞれの README を参照してください。
