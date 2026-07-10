# youtube-digest

登録チャンネル（`config.json`）の新着動画、または引数で指定された動画を要約ノート化するパイプラインを実行する。

役割分担の原則: 機械的な処理（検知・字幕取得・記録）はスクリプト、判断が必要な処理（要約・レビュー）はサブエージェントに任せる。文字起こしは長大なので、**メイン会話では絶対に読まない**こと。

このスキルのベースディレクトリはシステムから `Base directory for this skill:` として提供される。以下 `{skill_base_dir}` はそのパスに読み替えて実行すること。

## 出力先の解決

出力先は環境変数 `YOUTUBE_DIGEST_OUTPUT_DIR` のみを見る（`~/.claude/settings.json` の `env` で設定される）。

- 設定されていればそのディレクトリ配下にノートを保存する
- **未設定なら実行せず停止し**、`~/.claude/settings.json` の `env` に `YOUTUBE_DIGEST_OUTPUT_DIR` を設定するようユーザーに促す。設定例:

  ```json
  { "env": { "YOUTUBE_DIGEST_OUTPUT_DIR": "/path/to/vault/input/youtube" } }
  ```

  設定後はセッションの再起動が必要な旨も伝える。

---

## 実行手順

### 0. 出力先の確認（最初に必ず行う）

`YOUTUBE_DIGEST_OUTPUT_DIR` を確認する。未設定なら上記の案内をして停止する。以降の手順ではこの値を `$OUTPUT_DIR` と表記する。

### 1. 新着検知 + 字幕取得（スクリプト）

`$ARGUMENTS` の内容で分岐する:

- **YouTube URL または 11文字のvideo_id を含む** → その動画だけを処理:
  ```bash
  {skill_base_dir}/.venv/bin/python {skill_base_dir}/scripts/fetch.py <URL...>
  ```
  処理済みの動画はスクリプトがスキップする(重複要約の防止)。スキップされた場合はその旨を報告する。
  ユーザーが「再要約したい」「やり直したい」と明示している場合のみ `--force` を付けて実行する(ノートは上書きされる)
- **それ以外の文字列** → 全チャンネルを巡回後、pending.json から channel / folder が一致するエントリだけを処理対象にする（残りは pending に残し、手順5で記録しない）
- **引数なし** → 全チャンネル巡回:
  ```bash
  {skill_base_dir}/.venv/bin/python {skill_base_dir}/scripts/fetch.py
  ```

venv が無い場合は `{skill_base_dir}/README.md` のセットアップ手順を先に実行する。
結果は `{skill_base_dir}/pending.json`。処理対象が0件なら「新着なし」と報告して終了。

### 2. 格納先フォルダの確認

処理対象エントリの `folder` を確認し、必要なら **AskUserQuestion で提案**する（勝手に決めない）:

- **`folder` が null**（未登録チャンネルの動画をURL指定した場合）:
  チャンネル名から英数字ケバブケースのフォルダ名を提案し、以下の選択肢で確認する
  1. 提案フォルダを新設し、チャンネルも config.json に登録する（推奨）
  2. 提案フォルダを新設する（今回だけ）
  3. 既存フォルダ（`$OUTPUT_DIR` 配下の一覧を description に示す）に入れる
- **`folder` はあるが `$OUTPUT_DIR/<folder>/` が存在しない**:
  「フォルダ <folder> を新設してよいか」を確認する（選択肢: 新設する / 別名にする / 既存フォルダに入れる）

確定した folder を以降の手順で使う。選択肢1が選ばれたら `{skill_base_dir}/config.json` の `channels` に `{name, channel_id, folder}` を追記する（channel_id は pending.json のエントリにある）。

### 3. 要約（サブエージェント: 1動画 = 1体、並列起動）

`transcript_path` があるエントリごとに、Agentツールでサブエージェントを起動する。複数動画は**1つのメッセージで並列に**起動すること。プロンプト:

```
{skill_base_dir}/prompts/summary-prompt.md を読み、その指示に従って以下の動画の要約ノートを作成せよ。

- video_id: <video_id>
- title: <title>
- channel: <channel>
- folder: <手順2で確定した folder>
- published: <published>
- url: <url>
- transcript_path: <transcript_path>
- output_dir: <$OUTPUT_DIR>

完了したら、作成したノートの絶対パスだけを返すこと。
```

### 4. レビュー（サブエージェント: 要約が完了した動画ごとに起動）

各要約エージェントが返したノートパスに対し、レビューエージェントを起動する。プロンプト:

```
{skill_base_dir}/prompts/review-prompt.md を読み、その指示に従って以下のノートをレビュー・修正せよ。

- ノート: <要約エージェントが返したパス>
- 文字起こし: <transcript_path>
- skill_base_dir: <skill_base_dirの実パス>

完了したら修正点の要約を返すこと。
```

要約が失敗した動画はレビューをスキップし、失敗として記録する（pending には残す）。

### 5. 処理済みの記録（スクリプト）

レビューまで完了した動画の video_id をまとめて記録:

```bash
{skill_base_dir}/.venv/bin/python {skill_base_dir}/scripts/mark_done.py <video_id> [<video_id> ...]
```

- URL指定の動画（`adhoc: true`）も同様に記録する（チャンネル巡回での二重処理を防ぐ）
- 字幕が取得できなかった動画（`error` あり）の扱い:
  - 公開から7日以上経過(または公開日不明) → 今後も字幕が付く見込みが薄いため mark_done して打ち切る（報告に明記）
  - 公開から7日未満 → 記録せず次回に再試行
- チャンネル名で絞り込んだ場合、対象外のエントリは記録しない

### 6. 結果報告

以下をテーブルで報告する:

| タイトル | チャンネル | ノート | タグ | レビューでの主な修正 |

- 字幕なしでスキップ/打ち切った動画も別途列挙する
- 要約・レビューエージェントが「新タグ: xxx」を報告した場合はユーザーに伝え、語彙リスト（prompts/summary-prompt.md）への追加を提案する
- **コミットは行わない**（呼び出し元プロジェクトの運用に任せる）
