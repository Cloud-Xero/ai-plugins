# ai-plugins

Cloud-Xero 個人用の Claude Code プラグイン（スキル）カタログです。自分専用のスキルを 1 つのプラグイン `xero-skills` にまとめて管理します。

## セットアップ

```bash
git clone https://github.com/Cloud-Xero/ai-plugins.git
cd ai-plugins

# マーケットプレイスを登録してプラグインをインストール
claude plugin marketplace add "$(pwd)"
claude plugin install xero-skills@cloud-xero-plugins
```

## 更新

```bash
git pull
claude plugin install xero-skills@cloud-xero-plugins
```

> Claude Code はスキルをキャッシュにコピーして管理するため、`git pull` だけでは反映されません。

## スキルの呼び出し方

```
/xero-skills:<skill-name>
```

## スキルを追加する

`plugins/xero-skills/skills/<skill-name>/` に 2 ファイルを作成します（apsis 由来の二層構造）。

- `SKILL.md` — frontmatter（`name`＝ディレクトリ名 / `description`＝どんなときに使うかを具体的に）＋ `INSTRUCTIONS.md` への参照 1 行
- `INSTRUCTIONS.md` — 実際の手順・知識

雛形は [example-skill](./plugins/xero-skills/skills/example-skill/) をコピーして使ってください。

## スキル一覧

| スキル | 説明 |
|--------|------|
| `example-skill` | 新しいスキルを作るときの雛形となるサンプル |

## 構成

```
ai-plugins/
├── .claude-plugin/
│   └── marketplace.json          # マーケットプレイス定義
├── plugins/
│   └── xero-skills/
│       ├── .claude-plugin/plugin.json
│       └── skills/
│           └── example-skill/
│               ├── SKILL.md          # frontmatter + INSTRUCTIONS.md への参照
│               └── INSTRUCTIONS.md   # 実際の手順・知識
├── CLAUDE.md
└── README.md
```
