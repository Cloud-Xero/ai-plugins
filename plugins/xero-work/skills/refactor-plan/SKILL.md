---
name: refactor-plan
description: 肥大化したページ・モジュールのリファクタリング計画書を docs/refactoring/<対象>.md として作成するスキル。対象ごとに refactor-plan-analyzer エージェントを並列起動して実測（wc -l / grep / 依存・重複の洗い出し）させ、その分析を refactor-plan-writer に渡して「現状分析→問題点→目標構造→PR 単位の実行ステップ→テスト戦略→リスク」構成の計画書に仕上げる。全 PR 挙動不変・1 PR = 1 構造変更・独立マージ可能を原則とする。「リファクタ計画を作って」「この god-component を分割する計画が欲しい」「docs/refactoring に計画書を追加して」と言われたとき、または /refactor-plan [対象] で呼び出されたときに使用。計画の実行（PR 作成）は別スキル（refactor-page 等）の領分。
---

@INSTRUCTIONS.md
