#!/usr/bin/env python3
"""Compatibility wrapper for Guosen economy query.

The packaged script falls back to curl but does not unwrap STREAM_MESSAGE on that
path. This wrapper calls the packaged function and normalizes both response forms.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_竞品Skills" / "国信证券" / "extracted" / "gs-economy-query" / "scripts"))
import get_data  # type: ignore  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: guosen_economy_wrapper.py <query>")
    result = get_data.query_macro_data(sys.argv[1])
    if "content" in result:
        print(result["content"])
        return
    data = result.get("data") if isinstance(result, dict) else None
    if isinstance(data, list):
        parts = [x.get("content", "") for x in data if isinstance(x, dict) and x.get("type") == "STREAM_MESSAGE"]
        if any(parts):
            print("".join(parts))
            return
    print(result.get("error") or "未返回可用内容", file=sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()