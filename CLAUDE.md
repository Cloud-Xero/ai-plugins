# CLAUDE.md

## 絶対に守るルール

- **コミット・プッシュ・PR作成は、ユーザーから明示的に依頼された場合のみ実行する**
- タスク完了後に、依頼されていないコミット・プッシュ・PR作成を勝手に行わない
- **ただし `/commit` `/pr` `/br` `/merge` などスキルが明示的に呼び出された場合は、それ自体が「明示的な依頼」である。聞き返さず、確認も求めず、ただちにスキルの手順を実行する**

## 概要

Cloud-Xero 個人用の Claude Code プラグイン（スキル）カタログ。スキルとエージェントをドメインごとに 3 プラグインに分けて管理する。

- `xero-biz` — 経営・事業判断（戦略壁打ち・財務・pj-系サービス設計 / decision-reviewer・contract-reviewer・market-researcher）
- `xero-marketing` — 集客・販促（マーケ戦略・CS設計 / ad-operations・content-seo-editor・sns-content-writer）
- `xero-work` — 受託実務・開発補助（excel-analyze 一式 / proposal-writer・pm-estimator・qa-test-designer）

## リポジトリ構成

```
ai-plugins/
├── .claude-plugin/marketplace.json   # マーケットプレイス定義（3 プラグインを登録）
└── plugins/
    ├── xero-biz/
    ├── xero-marketing/
    └── xero-work/                    # 3 つとも同じ構成
        ├── .claude-plugin/plugin.json
        ├── skills/
        │   └── <skill-name>/
        │       ├── SKILL.md        # frontmatter + INSTRUCTIONS.md への参照
        │       └── INSTRUCTIONS.md # 実際の手順・知識
        └── agents/<agent-name>.md
```

## スキルを追加する

追加先のドメインプラグインを選び、`plugins/<plugin-name>/skills/<skill-name>/` に `SKILL.md` と `INSTRUCTIONS.md` を作成する（apsis 由来の二層構造）。`SKILL.md` は frontmatter（`name`＝ディレクトリ名 / `description`＝発火条件を具体的に）＋ `INSTRUCTIONS.md` への参照 1 行に留め、手順は `INSTRUCTIONS.md` に書く。雛形は `xero-work` の `example-skill` を参照・コピーする。

スキルから委譲されるエージェントは、必ずそのスキルと同じプラグインの `agents/` に置く（プラグインをまたぐと名前空間が変わり参照が壊れやすいため）。

## 反映方法

Claude Code はスキルをキャッシュにコピーするため、`git pull` だけでは反映されない。変更後は再インストールが必要。

```bash
claude plugin marketplace add "$(pwd)"
claude plugin install xero-biz@cloud-xero-plugins
claude plugin install xero-marketing@cloud-xero-plugins
claude plugin install xero-work@cloud-xero-plugins
```

さらに、Claude Code は **`version` の文字列をキャッシュキーにしている**。`plugin.json` の `version` を上げない限り、コミットを push しても利用者には変更が届かない（`/plugin update` は "already at the latest version" を返す）。

## バージョンの自動 bump

`version` の上げ忘れを防ぐため、`plugins/` 配下に変更があったプラグインの `version` をコミット時に自動で上げる git フックを用意している。clone 後に一度だけ設定する。

```bash
git config core.hooksPath .githooks
```

bump 種別はコミットメッセージのプレフィックスで決まる。

| メッセージ | bump |
|---|---|
| `feat!:` / `fix(scope)!:` / 本文に `BREAKING CHANGE:` | major |
| `feat:` | minor |
| その他（`fix:` `docs:` `chore:` `refactor:` …） | patch |

変更のあったプラグインだけが対象で、`plugin.json` と `.claude-plugin/marketplace.json` の両方が同じ値に更新され、直前のコミットに `--amend` で同梱される。次の場合は自動 bump をスキップする。

- そのコミットで既に `version` を手で変更している（minor / major を明示したいときはこれを使う）
- `plugin.json` がそのコミットで新規追加された（初期バージョンを尊重する）
- merge / rebase / cherry-pick の途中
- ステージに他の変更が残っている（`git commit -- <path>` のようなパス指定コミット）。`--amend` すると残りの変更まで巻き込むため、`version` の更新は作業ツリーに残して中止する

一時的に無効化したいときは `SKIP_PLUGIN_BUMP=1 git commit ...` とする。
