#!/usr/bin/env python3
"""Summarize a raw MX benchmark JSONL run, including screening adoption flags."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def extract_adoption(response: dict) -> tuple[str, str]:
    try:
        text = response["result"]["content"][0]["text"]
        payload = json.loads(text)
    except Exception:
        return "", ""
    for block in payload.get("data", []) or []:
        if not isinstance(block, dict):
            continue
        meta = block.get("meta") or {}
        adoption = meta.get("screeningResultAdoption") or {}
        if adoption:
            return str(adoption.get("adopted") or ""), str(adoption.get("reason") or "")
    return "", ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", default="04_测试结果/benchmarks/mx_benchmark_raw_20261115.jsonl")
    parser.add_argument("--out", default="04_测试结果/benchmarks/mx_benchmark_summary_enriched_20261115.csv")
    parser.add_argument("--stats", default="04_测试结果/benchmarks/mx_benchmark_category_stats_20261115.csv")
    args = parser.parse_args()

    rows = []
    with open(args.raw, encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            adopted, reason = extract_adoption(item.get("response", {}))
            rows.append({
                "case_id": item.get("case_id", ""),
                "category": item.get("category", ""),
                "query": item.get("query", ""),
                "target_metric": item.get("target_metric", ""),
                "item_count": item.get("item_count", 0),
                "adoption": adopted,
                "adoption_reason": reason,
                "required_field_coverage": item.get("required_field_coverage"),
                "required_field_hits": "|".join(item.get("required_field_hits", [])),
                "label_preview": "|".join(item.get("labels", [])[:20]),
                "elapsed_sec": item.get("elapsed_sec", ""),
                "has_error": item.get("has_error", False),
            })

    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    by_category = defaultdict(list)
    for row in rows:
        by_category[row["category"]].append(row)
    stats = []
    for category, group in sorted(by_category.items()):
        adopted = sum(1 for r in group if r["adoption"] == "采用")
        rejected = sum(1 for r in group if r["adoption"] == "不采用")
        no_meta = len(group) - adopted - rejected
        nonempty = sum(1 for r in group if int(r["item_count"] or 0) > 0)
        stats.append({
            "category": category,
            "cases": len(group),
            "adopted": adopted,
            "rejected": rejected,
            "no_meta_or_empty": no_meta,
            "nonempty": nonempty,
            "adoption_rate": round(adopted / len(group), 4),
        })
    with open(args.stats, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(stats[0].keys()))
        writer.writeheader()
        writer.writerows(stats)
    print(f"DONE rows={len(rows)} summary={args.out} stats={args.stats}")


if __name__ == "__main__":
    main()