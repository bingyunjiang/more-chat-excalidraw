#!/usr/bin/env python3
"""Validate a .excalidraw v2 file: structure, field types, and reference integrity.

Usage:
    python3 validate_excalidraw.py <file.excalidraw> [--strict] [--json]

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

# Fields that must be present on every element
REQUIRED_FIELDS = ("id", "type", "x", "y", "width", "height")

# Fields required on specific element types
TYPE_REQUIRED_FIELDS = {
    "text": ("text", "fontSize", "fontFamily"),
    "arrow": ("points",),
    "image": ("fileId",),
    "frame": ("name",),
}


def validate_file(filepath, strict=False):
    """Validate a .excalidraw file. Returns (errors, warnings, stats)."""
    errors, warnings = [], []
    stats = {"total_elements": 0, "by_type": {}}

    try:
        with open(filepath, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        errors.append(f"File not found: {filepath}")
        return errors, warnings, stats
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON: {exc}")
        return errors, warnings, stats

    if data.get("type") != "excalidraw":
        errors.append(f'top-level "type" must be "excalidraw", got {data.get("type")!r}')
    if data.get("version") != 2:
        errors.append(f'top-level "version" must be 2, got {data.get("version")!r}')

    elements = data.get("elements")
    if not isinstance(elements, list):
        errors.append('"elements" must be an array')
        return errors, warnings, stats

    stats["total_elements"] = len(elements)

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
        else:
            stats["by_type"][el_type] = stats["by_type"].get(el_type, 0) + 1

        # Required numeric fields
        for field in REQUIRED_NUMERIC:
            value = el.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(f"{label}: {field!r} must be a number, got {value!r}")
            elif field in ("width", "height") and value < 0:
                errors.append(f"{label}: {field} must be >= 0, got {value}")

        # Type-specific required fields
        if el_type in TYPE_REQUIRED_FIELDS:
            for field in TYPE_REQUIRED_FIELDS[el_type]:
                if el.get(field) is None:
                    errors.append(f"{label}: {el_type} element missing required field {field!r}")

        # Text element must have non-empty text
        if el_type == "text" and not isinstance(el.get("text"), str):
            errors.append(f'{label}: text element missing string field "text"')

        # Image fileId must reference top-level files
        if el_type == "image":
            file_id = el.get("fileId")
            if file_id and file_id not in (data.get("files") or {}):
                errors.append(f'{label}: fileId {file_id!r} has no entry in top-level "files"')

        # Arrow must have points array
        if el_type == "arrow":
            points = el.get("points")
            if not isinstance(points, list) or len(points) < 2:
                errors.append(f"{label}: arrow must have at least 2 points")

        # Arrow binding consistency
        if el_type == "arrow":
            for key in ("startBinding", "endBinding"):
                binding = el.get(key)
                if isinstance(binding, dict):
                    eid = binding.get("elementId")
                    if eid and eid not in element_index:
                        # Binding might reference an element not yet seen
                        pass  # Will be checked in second pass

        # groupIds consistency
        group_ids = el.get("groupIds", [])
        if not isinstance(group_ids, list):
            warnings.append(f"{label}: groupIds should be an array")

    # Second pass: reference integrity
    for el in elements:
        if not isinstance(el, dict):
            continue
        label = f"element[{el.get('id')!r}]"

        # boundElements references
        for ref in el.get("boundElements") or []:
            if isinstance(ref, dict) and ref.get("id") not in element_index:
                errors.append(f"{label}: boundElements references missing element {ref.get('id')!r}")

        # containerId reference
        container_id = el.get("containerId")
        if container_id:
            if container_id not in element_index:
                errors.append(f"{label}: containerId references missing element {container_id!r}")
            else:
                # Verify the container has a matching boundElements entry
                container = element_index[container_id]
                bound = container.get("boundElements") or []
                if not any(b.get("id") == el.get("id") for b in bound if isinstance(b, dict)):
                    warnings.append(
                        f"{label}: containerId points to {container_id!r} but that element's "
                        f"boundElements does not include this text element"
                    )

        # frameId reference
        frame_id = el.get("frameId")
        if frame_id and frame_id not in element_index:
            errors.append(f"{label}: frameId references missing element {frame_id!r}")

        # Arrow binding references
        for binding_key in ("startBinding", "endBinding"):
            binding = el.get(binding_key)
            if isinstance(binding, dict) and binding.get("elementId") not in element_index:
                errors.append(
                    f"{label}: {binding_key} references missing element {binding.get('elementId')!r}"
                )

        # Arrow binding should have matching boundElements on target
        if el.get("type") == "arrow":
            for binding_key in ("startBinding", "endBinding"):
                binding = el.get(binding_key)
                if isinstance(binding, dict):
                    target_id = binding.get("elementId")
                    if target_id and target_id in element_index:
                        target = element_index[target_id]
                        bound = target.get("boundElements") or []
                        if not any(b.get("id") == el.get("id") for b in bound if isinstance(b, dict)):
                            warnings.append(
                                f"{label}: {binding_key} targets {target_id!r} but that element's "
                                f"boundElements does not include this arrow"
                            )

        # Text overflow estimation
        if el.get("type") == "text":
            text = el.get("text") or ""
            font_size = el.get("fontSize") or 20
            est = sum(1.0 if ord(ch) > 0x2E80 else 0.6 for ch in text) * font_size
            if el.get("containerId") is None and est > (el.get("width") or 0) * 1.2:
                warnings.append(
                    f"{label}: text may overflow (estimated width {est:.0f}px > box {el.get('width')}px)"
                )

    return errors, warnings, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Path to .excalidraw file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    errors, warnings, stats = validate_file(args.file, args.strict)

    if args.json:
        result = {
            "file": args.file,
            "ok": len(errors) == 0 and not (args.strict and warnings),
            "errors": errors,
            "warnings": warnings,
            "stats": stats,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for line in errors:
            print(f"[ERROR] {line}")
        for line in warnings:
            print(f"[WARN]  {line}")
        if not errors and not warnings:
            print(f"[OK] {args.file}: {stats['total_elements']} elements")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
