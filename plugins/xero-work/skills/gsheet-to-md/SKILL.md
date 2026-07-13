---
name: gsheet-to-md
description: 公開Googleスプレッドシートを全シート漏れなくダウンロードし、シートごとのMarkdownテーブルとして保存する。htmlviewから全シート（gid＋シート名）を列挙し、シートごとにCSVで取得（表示値そのまま）→md変換する2段構え。生CSVも csv/ に一次データとして保存し、各mdのfrontmatterに取得元URL・シート名・gid・取得日時を記録する。「このスプレッドシートをmdで保存して」「シートをダウンロードして」と言われたとき、または /gsheet-to-md <URL> [出力先] で呼び出されたときに使う。認証が必要な非公開シートは対象外。
argument-hint: '<スプレッドシートURL> [出力先ディレクトリ(省略時は確認)]'
---

@INSTRUCTIONS.md
