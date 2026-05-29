# CLAUDE.md

## 絶対に守るルール

- **コミット・プッシュ・PR作成は、ユーザーから明示的に依頼された場合のみ実行する**
- タスク完了後に、依頼されていないコミット・プッシュ・PR作成を勝手に行わない
- **ただし `/commit` `/pr` `/br` `/merge` などスキルが明示的に呼び出された場合は、それ自体が「明示的な依頼」である。聞き返さず、確認も求めず、ただちにスキルの手順を実行する**

## 概要

Cloud-Xero 個人用の Claude Code プラグイン（スキル）カタログ。自分専用のスキルを 1 つのプラグイン `xero-skills` にまとめて管理する。

## リポジトリ構成

```
ai-plugins/
├── .claude-plugin/marketplace.json   # マーケットプレイス定義
└── plugins/
    └── xero-skills/
        ├── .claude-plugin/plugin.json
        └── skills/
            └── <skill-name>/
                ├── SKILL.md        # frontmatter + INSTRUCTIONS.md への参照
                └── INSTRUCTIONS.md # 実際の手順・知識
```

## スキルを追加する

`plugins/xero-skills/skills/<skill-name>/` に `SKILL.md` と `INSTRUCTIONS.md` を作成する（apsis 由来の二層構造）。`SKILL.md` は frontmatter（`name`＝ディレクトリ名 / `description`＝発火条件を具体的に）＋ `INSTRUCTIONS.md` への参照 1 行に留め、手順は `INSTRUCTIONS.md` に書く。雛形は `example-skill` を参照・コピーする。

## 反映方法

Claude Code はスキルをキャッシュにコピーするため、`git pull` だけでは反映されない。変更後は再インストールが必要。

```bash
claude plugin marketplace add "$(pwd)"
claude plugin install xero-skills@cloud-xero-plugins
```
