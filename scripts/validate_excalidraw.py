#!/usr/bin/env python3
"""Validate a .excalidraw v2 file: structure, field types, and reference integrity.

Usage:
    python3 validate_excalidraw.py <file.excalidraw> [--strict]

Exit code 0 = OK; 1 = errors found. Warnings never fail unless --strict.
"""

import argparse
import json
import sys


KNOWN_TYPES = {
    "rectangle", "ellipse", "diamond", "line", "arrow", "text",
    "freedraw", "image", "frame", "embeddable",
}

REQUIRED_NUMERIC = ("x", "y", "width", "height")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Path to .excalidraw file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    errors, warnings = [], []

    try:
        with open(args.file, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {args.file}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Invalid JSON: {exc}")
        return 1

    if data.get("type") != "excalidraw":
        errors.append(f'top-level "type" must be "excalidraw", got {data.get("type")!r}')
    if data.get("version") != 2:
        errors.append(f'top-level "version" must be 2, got {data.get("version")!r}')

    elements = data.get("elements")
    if not isinstance(elements, list):
        errors.append('"elements" must be an array')
        elements = []

    seen_ids = set()
    element_index = {}
    for i, el in enumerate(elements):
        label = f"element[{i}]"
        if not isinstance(el, dict):
            errors.append(f"{label}: must be an object")
            continue

        el_id = el.get("id")
        if not isinstance(el_id, str) or not el_id:
            errors.append(f'{label}: missing string field "id"')
        elif el_id in seen_ids:
            errors.append(f"{label}: duplicate id {el_id!r}")
        else:
            seen_ids.add(el_id)
            element_index[el_id] = el

        el_type = el.get("type")
        if el_type not in KNOWN_TYPES:
            errors.append(f"{label}: unknown type {el_type!r}")

        for field in REQUIRED_NUMERIC:
            value = el.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{label}: {field!r} must be a number, got {value!r}")
            elif field in ("width", "height") and value < 0:
                errors.append(f"{label}: {field} must be >= 0, got {value}")

        if el_type == "text" and not isinstance(el.get("text"), str):
            errors.append(f'{label}: text element missing string field "text"')

        if el_type == "image":
            file_id = el.get("fileId")
            if file_id and file_id not in (data.get("files") or {}):
                errors.append(f'{label}: fileId {file_id!r} has no entry in top-level "files"')

    for el in elements:
        if not isinstance(el, dict):
            continue
        label = f"element[{el.get('id')!r}]"

        for ref in el.get("boundElements") or []:
            if isinstance(ref, dict) and ref.get("id") not in element_index:
                errors.append(f"{label}: boundElements references missing element {ref.get('id')!r}")

        for key in ("containerId", "frameId"):
            ref = el.get(key)
            if ref and ref not in element_index:
                errors.append(f"{label}: {key} references missing element {ref!r}")

        for binding_key in ("startBinding", "endBinding"):
            binding = el.get(binding_key)
            if isinstance(binding, dict) and binding.get("elementId") not in element_index:
                errors.append(
                    f"{label}: {binding_key} references missing element {binding.get('elementId')!r}"
                )

        if el.get("type") == "text":
            text = el.get("text") or ""
            font_size = el.get("fontSize") or 20
            est = sum(1.0 if ord(ch) > 0x2E80 else 0.6 for ch in text) * font_size
            if el.get("containerId") is None and est > (el.get("width") or 0) * 1.2:
                warnings.append(
                    f"{label}: text may overflow (estimated width {est:.0f}px > box {el.get('width')}px)"
                )

    for line in errors:
        print(f"[ERROR] {line}")
    for line in warnings:
        print(f"[WARN]  {line}")

    if not errors and not warnings:
        print(f"[OK] {args.file}: {len(elements)} elements")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
