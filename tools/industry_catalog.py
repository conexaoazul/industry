#!/usr/bin/env python3
"""Generate a deterministic public catalog from Odoo Industry manifests.

The catalog is intentionally derived from repository metadata. It does not
rewrite upstream Odoo URLs; instead it exposes Conexao Azul canonical paths
alongside source references so downstream consumers can keep provenance.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT = Path("catalog/industries.json")


def _read_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = ast.literal_eval(handle.read())
    if not isinstance(data, dict):
        raise ValueError(f"Manifest must be a dict: {path}")
    return data


def _catalog_entry(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _read_manifest(manifest_path)
    slug = manifest_path.parent.name
    images = manifest.get("images") or []
    return {
        "slug": slug,
        "name": manifest.get("name") or slug.replace("_", " ").title(),
        "category": manifest.get("category") or "Other",
        "version": manifest.get("version"),
        "license": manifest.get("license"),
        "author": manifest.get("author"),
        "application": bool(manifest.get("application")),
        "depends": sorted(set(manifest.get("depends") or [])),
        "image": images[0] if images else None,
        "source_url": manifest.get("url"),
        "source_website": manifest.get("website"),
        "repo_path": manifest_path.parent.relative_to(root).as_posix(),
        "canonical_path": f"/segmentos/{slug}",
        "trial_path": f"/go/industry/{slug}",
    }


def build_catalog(root: Path, *, include_support: bool = False) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for manifest_path in sorted(root.glob("*/__manifest__.py")):
        entry = _catalog_entry(root, manifest_path)
        if include_support or entry["application"]:
            entries.append(entry)
    return sorted(entries, key=lambda item: (item["name"].casefold(), item["slug"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--include-support",
        action="store_true",
        help="Include non-application support modules in addition to public templates.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    catalog = build_catalog(root, include_support=args.include_support)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_repo": "conexaoazul/industry",
                "source_branch": "19.0",
                "count": len(catalog),
                "industries": catalog,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(catalog)} industries to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
