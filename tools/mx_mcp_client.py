#!/usr/bin/env python3
"""Minimal MX MCP client for repeatable research tests.

Reads EM_API_KEY from the environment, falling back to ~/.mx-skills/apikey.
Uses only the Python standard library.

Examples:
  python tools/mx_mcp_client.py list
  python tools/mx_mcp_client.py call mx_stocks_screener --query "今日ETF涨幅榜前10"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

URL = "https://mxapi.eastmoney.com/mxds/mcp"
KEY_FILE = Path.home() / ".mx-skills" / "apikey"


def resolve_key() -> str:
    key = os.environ.get("EM_API_KEY", "").strip()
    if key:
        return key
    try:
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        key = ""
    if not key:
        raise SystemExit("ERROR: EM_API_KEY is not set and ~/.mx-skills/apikey is missing")
    return key


def post(headers: dict, payload: dict, timeout: int = 120) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Streamable HTTP can return SSE frames.
        for line in raw.splitlines():
            if line.startswith("data:"):
                data = line[5:].strip()
                if data:
                    return json.loads(data)
        raise


def session_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "em_api_key": resolve_key(),
        "User-Agent": "mx-mcp-research-client/1.0",
    }


def initialize(headers: dict) -> dict:
    result = post(headers, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "mx-mcp-research-client", "version": "1.0"},
        },
    })
    post(headers, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    return result


def list_tools(headers: dict) -> dict:
    return post(headers, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})


def call_tool(headers: dict, name: str, arguments: dict) -> dict:
    return post(headers, {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    })


def normalized_text(response: dict) -> str:
    try:
        content = response.get("result", {}).get("content", [])
        for item in content:
            if item.get("type") == "text":
                return item.get("text", "")
    except Exception:
        pass
    return ""


if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    call = sub.add_parser("call")
    call.add_argument("tool")
    call.add_argument("--query", required=True)
    call.add_argument("--out", help="Write the raw MCP response to this path")
    call.add_argument("--normalized-out", help="Write the normalized text payload to this path")
    args = parser.parse_args()

    headers = session_headers()
    initialize(headers)
    if args.command == "list":
        response = list_tools(headers)
        print(json.dumps(response, ensure_ascii=False, indent=2))
        return

    response = call_tool(headers, args.tool, {"query": args.query})
    if args.out:
        Path(args.out).write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
    text = normalized_text(response)
    if args.normalized_out:
        Path(args.normalized_out).write_text(text, encoding="utf-8")
    try:
        print(json.dumps(json.loads(text), ensure_ascii=False, indent=2))
    except Exception:
        print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()