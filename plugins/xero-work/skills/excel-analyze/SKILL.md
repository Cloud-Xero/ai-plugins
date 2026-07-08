---
name: excel-analyze
description: 複雑なExcelファイル（数式・他シート参照が多いブック）をWebアプリ移植に向けて解析するスキル。構造棚卸し→数式依存グラフ→ロジック仕様書→回帰テスト用スナップショットの4工程を、専用エージェント（excel-inventory / excel-dep-graph / excel-logic-spec / excel-snapshot）に順に委譲して excel_analysis/<ブック名>/ に成果物を出力する。「このExcelを解析して」「ExcelをWebアプリ化したい」「数式の依存関係を調べて」と言われたとき、または /excel-analyze <path> で呼び出されたときに使用。
---

@INSTRUCTIONS.md
