#!/usr/bin/env python3
"""Compatibility wrapper for Guosen smart stock picking on Python 3.13+."""
from __future__ import annotations

import runpy
import ssl
import sys
from pathlib import Path

if not hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
    ssl.OP_LEGACY_SERVER_CONNECT = 0x4  # type: ignore[attr-defined]

target = Path(__file__).resolve().parents[1] / "01_竞品Skills" / "国信证券" / "extracted" / "gs-smart-stock-picking" / "scripts" / "gs_stock_picking.py"
sys.argv[0] = str(target)
runpy.run_path(str(target), run_name="__main__")