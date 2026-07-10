---
name: youtube-digest
description: 登録済みYouTubeチャンネルの新着動画(または指定した動画URL)を、字幕取得→要約→レビューを経てObsidianノートとして保存する。「YouTube要約して」「この動画をダイジェストして」などで起動。出力先は環境変数 YOUTUBE_DIGEST_OUTPUT_DIR（~/.claude/settings.json の env で設定）。未設定の場合は設定を促して停止する。
argument-hint: '[動画URL または チャンネル名で絞り込み(省略可)]'
---

@INSTRUCTIONS.md
