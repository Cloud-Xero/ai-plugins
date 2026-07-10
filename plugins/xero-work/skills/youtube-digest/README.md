# youtube-digest

登録したYouTubeチャンネルの新着動画を「字幕取得 → 要約 → レビュー」のパイプラインでObsidianノート化するツール。
起点は Claude Code のスキル `/youtube-digest`。プラグインスキルとして、どのプロジェクトからでも呼び出せる。

## 仕組み

```
config.json（チャンネル定義）
  ↓ scripts/fetch.py         … RSSで新着検知 + 字幕取得（スクリプト）
  ↓ pending.json / transcripts/<id>.txt
  ↓ 要約サブエージェント       … prompts/summary-prompt.md に従いノート生成（1動画1体・並列）
  ↓ レビューサブエージェント   … prompts/review-prompt.md に従い事実確認・文体修正・抽象化の品質チェック
  ↓ $YOUTUBE_DIGEST_OUTPUT_DIR/<folder>/<公開日>_<タイトル>.md
  ↓ scripts/mark_done.py      … state.json に処理済みを記録（スクリプト）
```

## 出力先の設定（初回のみ）

出力先は環境変数 `YOUTUBE_DIGEST_OUTPUT_DIR` で指定する。`~/.claude/settings.json` の `env` に追加する:

```json
{ "env": { "YOUTUBE_DIGEST_OUTPUT_DIR": "/path/to/vault/input/youtube" } }
```

設定後はセッションの再起動が必要。未設定のままスキルを起動すると、実行せず設定を促して停止する。

## セットアップ（初回のみ）

```bash
cd <このスキルのディレクトリ>
python3 -m venv .venv
.venv/bin/pip install youtube-transcript-api defusedxml yt-dlp
```

yt-dlp は backfill（過去動画の一覧取得）にのみ使う。動画のダウンロードはしない。

## チャンネルの登録

`config.json` の `channels` に追加する:

```json
{
  "name": "チャンネル表示名（ノートのfrontmatterに入る）",
  "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxx",
  "folder": "保存先フォルダ名（$YOUTUBE_DIGEST_OUTPUT_DIR 配下・英数字ケバブケース推奨）"
}
```

- `channel_id` はチャンネルページのURL（`youtube.com/channel/UC...`）またはページソースの `channelId` から取得
- `folder` を省略すると `name` をそのまま使う
- `max_total_per_run` は1回の実行で要約する動画の全体上限（既定: 5）。超過分は次回に持ち越し。複数チャンネルはラウンドロビンで公平に選ばれる。URL指定の動画は明示的な依頼なので上限の対象外
- `max_per_channel` は1チャンネルあたりの候補上限（backfillで埋める分を含む）
- `backfill: true` にすると、フィード内に未処理動画が足りないとき、さらに過去へ遡って未要約の直近動画で枠を埋める（チャンネル単位のオプトイン）。遡る範囲は `backfill_scan_depth`（既定: 直近50本）まで

要約の「自分のビジネスへの転用」の質を上げるため、`prompts/summary-prompt.md` の
「自分のビジネス一覧」に各プロジェクトの説明を書いておくこと。

## 実行

Claude Code で `/youtube-digest`（または「YouTube要約して」）。

- `/youtube-digest <チャンネル名 or フォルダ名>` … そのチャンネルの新着だけ処理
- `/youtube-digest <動画URL>` … 特定の動画だけ処理（登録外チャンネルでも可）
  - 登録済みチャンネルの動画なら格納先フォルダを自動解決
  - 未登録チャンネルの動画は、フォルダの新設（+configへのチャンネル登録）をスキルが提案する
  - 処理済みの動画はスキップされる。再要約したい場合は「再要約して」と明示する（`--force` でノート上書き）

スクリプト単体の動作確認（このスキルのディレクトリから）:

```bash
.venv/bin/python scripts/fetch.py --dry-run
.venv/bin/python scripts/fetch.py "https://www.youtube.com/watch?v=..." --dry-run
```

## トピックタグ

各ノートの frontmatter には `youtube-digest` に加え、主題を表すトピックタグ（`mind`, `marketing` など）が1〜3個付く。
語彙は `prompts/summary-prompt.md` の「トピックタグの語彙」セクションで管理する（表記ゆれ防止のため自由記述にしない）。

Obsidianでタグ別一覧を作るには、一覧用ノートに検索埋め込みやDataviewを書く:

````markdown
```query
tag:#marketing tag:#youtube-digest
```
````

## ファイル

| パス | 役割 | git管理 |
|---|---|---|
| `config.json` | チャンネル定義 | ○ |
| `state.json` | 処理済み video_id | ○（複数マシンで整合させるため） |
| `pending.json` | 今回の処理対象（中間ファイル） | ✗ |
| `transcripts/` | 文字起こし（中間ファイル） | ✗ |
| `prompts/` | 要約・レビューのテンプレート | ○ |
| `.venv/` | Python仮想環境 | ✗ |

## 補足

- RSSフィードには最新15件しか載らない。それより古い動画を対象にしたいチャンネルは `backfill: true` を設定する（backfillは通常動画タブを新しい順にスキャンする。ショート・ライブは対象外）
- 字幕が無い動画は次回再試行し、公開から7日を過ぎても取れなければ打ち切る（スキルが判断）
- YouTubeはクラウドIPからの字幕取得をブロックしやすいため、ローカル実行を前提にしている
