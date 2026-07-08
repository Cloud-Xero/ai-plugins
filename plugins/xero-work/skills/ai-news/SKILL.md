---
name: ai-news
description: Anthropic・OpenAI・Google（Gemini）・xAI（Grok）など主要AI企業の最新ニュースを収集し、日本語解説レポートとして保存する。「AIの最新情報をまとめて」「今週のAIニュースを教えて」と言われたとき、または /ai-news で呼び出されたときに使う。実際の調査・執筆は ai-news-reporter エージェントに委譲する。出力先は環境変数 AI_NEWS_OUTPUT_DIR（~/.claude/settings.json の env で設定）。未設定の場合は設定を促して停止する。
---

@INSTRUCTIONS.md
