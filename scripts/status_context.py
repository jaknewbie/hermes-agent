#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
อ่าน context/session token ของ Hermes session ปัจจุบัน เพื่อต่อท้ายข้อความแชท
ค่า Context อ่านจากไฟล์ ~/.hermes/context_status.json ซึ่ง Hermes เขียนทุกเทิร์น
(แก้แหล่งที่มาใน agent/turn_finalizer.py + gateway/slash_commands.py)
ถ้ายังไม่มีไฟล์ (gateway ยังไม่รันเทิร์น) จะ fallback เป็น N/A ไม่เดาค่า
"""
import os
import json
import time

HERMES = os.path.expanduser("~/.hermes")
CONTEXT_FILE = os.path.join(HERMES, "context_status.json")


def _read_context_file():
    """อ่านค่า Context จริงที่ gateway เขียนทุกเทิร์น"""
    try:
        if not os.path.exists(CONTEXT_FILE):
            return None
        with open(CONTEXT_FILE, encoding="utf-8") as f:
            d = json.load(f)
        # ถ้าไฟล์เก่ากว่า 1 ชั่วโมง เตือนว่าเป็นค่าเก่า
        age = time.time() - float(d.get("updated_at", 0))
        stale = age > 3600
        return {
            "used": int(d.get("context_used", 0) or 0),
            "max": int(d.get("context_max", 0) or 0),
            "pct": float(d.get("context_percent", 0) or 0),
            "model": d.get("model") or "",
            "provider": d.get("provider") or "",
            "total_tokens": int(d.get("total_tokens", 0) or 0),
            "stale": stale,
        }
    except Exception:
        return None


def main():
    ctx = _read_context_file()
    if not ctx:
        print("Context: N/A (gateway ยังไม่เขียนค่า — รอเทิร์นแรก หรือรัน /usage)")
        print("Model: tencent/hy3:free (nous)")
        return
    used = ctx["used"]
    mx = ctx["max"] or 262_144
    pct = ctx["pct"] or round((used / mx) * 100, 1) if mx else 0
    stale_tag = " [ค่าเก่า>1ชม]" if ctx["stale"] else ""
    print(f"Context: {used:,} / {mx:,} ({pct:.0f}%){stale_tag}")
    print(f"Model: {ctx['model']} ({ctx['provider']})")


if __name__ == "__main__":
    main()
