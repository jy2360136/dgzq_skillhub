#!/usr/bin/env python3
"""Run the ETF benchmark CSV against the MX MCP screener.

This tool keeps raw evidence in JSONL and emits a compact summary CSV. It does
not score semantic correctness by itself; required-field hits are a first-pass
coverage signal that must be reviewed for unsupported or implicitly ignored
conditions.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

URL = "https://mxapi.eastmoney.com/mxds/mcp"
KEY_FILE = Path.home() / ".mx-skills" / "apikey"


def key() -> str:
    value = os.environ.get("EM_API_KEY", "").strip()
    if not value and KEY_FILE.exists():
        value = KEY_FILE.read_text(encoding="utf-8").strip()
    if not value:
        raise SystemExit("ERROR: EM_API_KEY is not configured")
    return value


def post(payload: dict, timeout: int = 90) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "em_api_key": key(),
        "User-Agent": "mx-etf-benchmark/1.0",
    }
    req = urllib.request.Request(URL, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        raise


def init() -> None:
    post({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "mx-etf-benchmark", "version": "1.0"},
        },
    })
    post({"jsonrpc": "2.0", "method": "notifications/initialized"})


def call(query: str) -> dict:
    return post({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "mx_stocks_screener",
            "arguments": {"query": query},
        },
    })


def payload_text(response: dict) -> str:
    result = response.get("result", {})
    for item in result.get("content", []):
        if item.get("type") == "text":
            return item.get("text", "")
    return ""


def parse_payload(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def flatten_labels(obj) -> list[str]:
    labels = []
    if not isinstance(obj, dict):
        return labels
    for block in obj.get("data", []) or []:
        for value in block.get("columns", []) or []:
            labels.append(str(value))
        for row in block.get("items", []) or []:
            if isinstance(row, list) and row:
                labels.append(str(row[0]))
    return labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="04_测试结果/benchmarks/ETF筛选_200问.csv")
    parser.add_argument("--out-jsonl", default="04_测试结果/benchmarks/mx_benchmark_raw_20261115.jsonl")
    parser.add_argument("--out-csv", default="04_测试结果/benchmarks/mx_benchmark_summary_20261115.csv")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()

    with open(args.csv, encoding="utf-8-sig", newline="") as f:
        cases = list(csv.DictReader(f))
    if args.limit:
        cases = cases[:args.limit]

    init()
    out_jsonl = Path(args.out_jsonl)
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    summary = []
    with out_jsonl.open("w", encoding="utf-8") as raw_file:
        for idx, case in enumerate(cases, start=1):
            started = time.time()
            error = ""
            response = {}
            try:
                response = call(case["query"])
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
            elapsed = round(time.time() - started, 3)
            text = payload_text(response)
            parsed = parse_payload(text)
            labels = flatten_labels(parsed)
            required = [x.strip() for x in case.get("required_fields", "").split(",") if x.strip()]
            hits = [field for field in required if any(field in label for label in labels)]
            data_blocks = parsed.get("data", []) if isinstance(parsed, dict) else []
            item_count = sum(len(block.get("items", []) or []) for block in data_blocks if isinstance(block, dict))
            has_error = bool(error or response.get("error") or response.get("result", {}).get("isError"))
            record = {
                "case_id": case["case_id"],
                "category": case["category"],
                "query": case["query"],
                "target_metric": case.get("target_metric", ""),
                "elapsed_sec": elapsed,
                "error": error,
                "has_error": has_error,
                "parse_ok": parsed is not None,
                "item_count": item_count,
                "required_fields": required,
                "required_field_hits": hits,
                "required_field_coverage": round(len(hits) / len(required), 4) if required else None,
                "labels": labels[:80],
                "response": response,
            }
            raw_file.write(json.dumps(record, ensure_ascii=False) + "\n")
            raw_file.flush()
            summary.append({
                "case_id": case["case_id"],
                "category": case["category"],
                "query": case["query"],
                "target_metric": case.get("target_metric", ""),
                "elapsed_sec": elapsed,
                "has_error": has_error,
                "parse_ok": parsed is not None,
                "item_count": item_count,
                "required_field_hits": "|".join(hits),
                "required_field_coverage": record["required_field_coverage"],
                "label_preview": "|".join(labels[:20]),
                "error": error,
            })
            print(f"[{idx}/{len(cases)}] {case['case_id']} items={item_count} adoption={adoption or '-'} fields={len(hits)}/{len(required)} {elapsed}s", flush=True)
            if args.delay:
                time.sleep(args.delay)

    with open(args.out_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    print(f"DONE cases={len(summary)} raw={out_jsonl} summary={args.out_csv}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()