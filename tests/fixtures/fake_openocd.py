#!/usr/bin/env python3
from __future__ import annotations

import sys


def main() -> int:
    args = sys.argv[1:]
    if "--version" in args:
        print("Open On-Chip Debugger 0.12.0")
        return 0
    text = " ".join(args)
    if "adapter serial" in text:
        print(text)
    if "probe_target" in text:
        print("HARDCI_RESULT:probe_target:ok")
    if "flash_firmware" in text or "program" in text:
        print("HARDCI_RESULT:flash_firmware:ok")
    if "reset_target" in text or "reset" in text:
        print("HARDCI_RESULT:reset_target:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
