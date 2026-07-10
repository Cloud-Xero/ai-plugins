#!/usr/bin/env python3
"""処理が完了した video_id を state.json に記録し、pending.json から除去する。

使い方(スキルのベースディレクトリから):
  .venv/bin/python scripts/mark_done.py VIDEO_ID [VIDEO_ID ...]
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STATE_PATH = BASE / "state.json"
PENDING_PATH = BASE / "pending.json"


def main() -> None:
    ids = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not ids:
        print("video_id を1つ以上指定してください", file=sys.stderr)
        sys.exit(1)

    state = {"processed": []}
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    added = [vid for vid in ids if vid not in state["processed"]]
    state["processed"].extend(added)
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if PENDING_PATH.exists():
        pending = json.loads(PENDING_PATH.read_text(encoding="utf-8"))
        remaining = [e for e in pending if e["video_id"] not in ids]
        PENDING_PATH.write_text(
            json.dumps(remaining, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"pending: {len(pending)} → {len(remaining)} 件")

    print(f"処理済みに記録: {len(added)} 件 (合計 {len(state['processed'])} 件)")


if __name__ == "__main__":
    main()
