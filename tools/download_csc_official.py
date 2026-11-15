#!/usr/bin/env python3
"""Download official China Securities SkillHub ZIP packages.

Authentication is read only from SKILLHUB_API_KEY. The key is never written to
disk or printed. Existing packages are skipped unless --force is supplied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

SKILLS = {
    "csc-etf-index-analysis": "ETF 筛选/指数估值",
    "csc-fund-product-info-query": "基金研判/基金产品信息",
    "csc-listed-company-profile-industry-compare": "个股研判/公司行业对比",
    "csc-macro-analysis": "大盘分析",
    "csc-pankou": "盘口异动",
    "csc-stock-analysis": "个股综合分析",
    "csc-stock-financial-query": "财报透视/财务查询",
    "stock-pick": "智能选股",
}
BASE_URL = "https://skillhub.csc108.com/api/h5/skills/{skill_id}/download"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_extract(zip_path: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            resolved = (target / member.filename).resolve()
            root = target.resolve()
            if root not in resolved.parents and resolved != root:
                raise RuntimeError(f"unsafe zip path: {member.filename}")
        zf.extractall(target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="01_竞品Skills/中信建投-官网")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    key = os.environ.get("SKILLHUB_API_KEY", "").strip()
    if not key:
        raise SystemExit("ERROR: SKILLHUB_API_KEY is not configured")

    root = Path(args.root)
    packages = root / "packages"
    extracted = root / "extracted"
    packages.mkdir(parents=True, exist_ok=True)
    extracted.mkdir(parents=True, exist_ok=True)
    manifest = {"source": "中信建投蜻蜓 Skill 广场", "skills": []}

    for skill_id, display_name in SKILLS.items():
        zip_path = packages / f"{skill_id}.zip"
        url = BASE_URL.format(skill_id=skill_id)
        if args.force or not zip_path.exists():
            req = urllib.request.Request(url, headers={
                "X-API-Key": key,
                "User-Agent": "dgzq-skillhub-research/1.0",
            })
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
            if not data.startswith(b"PK\x03\x04"):
                raise RuntimeError(f"{skill_id}: response is not a ZIP")
            zip_path.write_bytes(data)
        else:
            data = zip_path.read_bytes()
            if not data.startswith(b"PK\x03\x04"):
                raise RuntimeError(f"{skill_id}: existing file is not a ZIP")

        target = extracted / skill_id
        if target.exists():
            shutil.rmtree(target)
        safe_extract(zip_path, target)
        files = sorted(p for p in target.rglob("*") if p.is_file())
        entry = {
            "skill_id": skill_id,
            "display_name": display_name,
            "zip": {"bytes": len(data), "sha256": sha256(zip_path)},
            "files": [
                {
                    "path": str(p.relative_to(target)).replace("\\", "/"),
                    "bytes": p.stat().st_size,
                    "sha256": sha256(p),
                }
                for p in files
            ],
        }
        manifest["skills"].append(entry)
        print(f"OK {skill_id} files={len(files)} zip_bytes={len(data)}")

    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()