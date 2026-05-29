# example-skill

これは `xero-skills` プラグインの動作確認とスキル雛形を兼ねたサンプルです。
新しいスキルを追加するときは、このディレクトリをコピーして編集してください。

## スキルの構成（二層構造）

スキルは 2 ファイルに分けます。

- `SKILL.md` — frontmatter（`name`・`description`、必要なら `allowed-tools`）と、`INSTRUCTIONS.md` への参照 1 行のみ。Claude は最初にこの薄い説明だけを読み、発火するかを判断する
- `INSTRUCTIONS.md` — 実際の手順・知識。スキルが起動されたときに読み込まれる

長い手順やデータはさらに `references/` や `scripts/` に分割してもかまいません。

## スキルの作り方

1. `plugins/xero-skills/skills/<skill-name>/` ディレクトリを作る
2. `SKILL.md` に frontmatter を書く
   - `name`: スキルの識別子（ディレクトリ名と一致させる）
   - `description`: **いつこのスキルを使うか** を具体的に書く。Claude はこの一文だけを見て発火を判断するため、トリガーとなる状況・キーワードを明記する
   - 本文は `See [INSTRUCTIONS.md](./INSTRUCTIONS.md) for detailed instructions.` の 1 行に留める
3. `INSTRUCTIONS.md` に実際の手順・知識を書く
4. `README.md` のスキル一覧を更新する

## 呼び出し方

```
/xero-skills:example-skill
```

プラグイン名（`xero-skills`）がスキルの名前空間になります。
