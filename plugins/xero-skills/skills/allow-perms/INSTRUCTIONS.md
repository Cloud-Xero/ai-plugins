# allow-perms

現在のセッションで許可確認を求められたコマンド・ツールを、ユーザースコープ（`~/.claude/settings.json`）の `permissions.allow` に追加し、今後どのプロジェクトでも確認プロンプトが出ないようにするスキル。

## 手順

### 1. セッション内の候補を洗い出す

現在の会話を振り返り、許可確認の対象になったと思われるツール呼び出しを列挙する。

- 自分（Claude）が実行した Bash コマンドのうち、読み取り専用でない・標準の自動許可対象でないもの
- ユーザーに一度拒否されて言い換えたコマンド、承認待ちで止まったコマンド
- MCP ツール（`mcp__server__tool` 形式）や WebFetch など、Bash 以外で確認が入ったもの

引数でコマンドが直接指定された場合（例: `/allow-perms npm run build`）は、そのコマンドだけを対象にする。

### 2. 既存の許可ルールと突き合わせる

以下のファイルを読み、すでに許可済みのものを候補から除外する。

- `~/.claude/settings.json`（ユーザースコープ・今回の追加先）
- プロジェクトの `.claude/settings.json` / `.claude/settings.local.json`（あれば参考として）

### 3. 許可ルールを設計する

各候補を permission rule 構文に変換する。**個別コマンドをそのまま登録するのではなく、適切な粒度のプレフィックスマッチにする**のが原則。

| 種類 | ルール構文の例 |
|---|---|
| Bash（完全一致） | `Bash(npm run build)` |
| Bash（プレフィックス一致） | `Bash(npm run:*)`、`Bash(gh pr view:*)` |
| MCP ツール | `mcp__server__tool_name`（引数マッチ不可、ツール単位） |
| WebFetch | `WebFetch(domain:example.com)` |
| Read / Edit | `Read(~/.zshrc)`、`Edit(//tmp/**)`（gitignore 形式パス） |

粒度の指針:

- サブコマンド単位で許可する（`Bash(git:*)` のような広すぎるルールは避け、`Bash(git fetch:*)` のようにする）
- 破壊的コマンド（`rm`、`git push --force`、`sudo` 等）は範囲を含むプレフィックスにしない。必要なら完全一致で登録する
- 秘密情報を引数に含むコマンドはルール化しない

### 4. ユーザーに確認する

追加候補のルール一覧（ルール・元になったコマンド・粒度の理由）を提示し、AskUserQuestion（multiSelect）でどれを追加するか選んでもらう。候補が 1 件だけで文脈上明らかな場合も、ルールの粒度（完全一致かプレフィックスか）は提示して確認する。

### 5. ~/.claude/settings.json を更新する

1. `~/.claude/settings.json` を読む（存在しなければ `{}` から作る）
2. `permissions.allow` 配列に選択されたルールを追加する（重複は追加しない、既存の順序・他のキー・インデントは保持する）
3. 書き込み後、`python3 -m json.tool ~/.claude/settings.json > /dev/null` などで JSON として妥当なことを検証する

例:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run:*)",
      "Bash(gh pr view:*)"
    ]
  }
}
```

### 6. 結果を報告する

追加したルールの一覧と、「ユーザースコープなので全プロジェクトに適用される」「新しい設定は次のツール呼び出しから有効（反映されない場合はセッション再起動）」を伝える。

## 注意

- 追加先は必ずユーザースコープ `~/.claude/settings.json`。プロジェクトの `.claude/settings.json` や `settings.local.json` には書かない
- `permissions.deny` や既存の `ask` ルールがある場合、deny が allow より優先されることを踏まえて矛盾するルールを追加しない
- settings.json に `permissions` 以外のキー（hooks、env 等）があっても壊さないこと
