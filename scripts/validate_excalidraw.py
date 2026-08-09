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


def _bbox(el):
    """Bounding box of an element as (x, y, x2, y2) or None."""
    if not isinstance(el, dict):
        return None
    x, y = el.get("x"), el.get("y")
    w, h = el.get("width"), el.get("height")
    if not all(isinstance(v, (int, float)) for v in (x, y, w, h)):
        return None
    return (x, y, x + w, y + h)


def _rects_overlap(a, b):
    """Return overlap area (px^2) between two bboxes, or 0 if none."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ox = max(0, min(ax2, bx2) - max(ax1, bx1))
    oy = max(0, min(ay2, by2) - max(ay1, by1))
    return ox * oy


def _visual_checks(elements, warnings, visual_contract=None, sketch=False):
    """Layout quality heuristics: overlaps, dangling arrows, density."""
    # Skip connector elements and tiny markers when computing overlaps
    shapes = []
    for i, el in enumerate(elements):
        if not isinstance(el, dict):
            continue
        etype = el.get("type")
        if etype not in ("rectangle", "ellipse", "diamond", "text"):
            continue
        # Invisible anchor overlays are intentional for library components and
        # should not be reported as visual overlaps with their artwork.
        if el.get("opacity", 100) == 0:
            continue
        # Skip zero-size markers (timeline dots etc.)
        w, h = el.get("width", 0), el.get("height", 0)
        if w < 10 or h < 10:
            continue
        bb = _bbox(el)
        if bb:
            shapes.append((i, el, bb))

    # Overlap detection (only for containers, not free text)
    containers = [s for s in shapes if s[1].get("type") in ("rectangle", "ellipse", "diamond")]
    for i in range(len(containers)):
        for j in range(i + 1, len(containers)):
            (ia, ea, ba), (ib, eb, bb) = containers[i], containers[j]
            if set(ea.get("groupIds") or ()) & set(eb.get("groupIds") or ()):
                continue
            area = _rects_overlap(ba, bb)
            if area <= 0:
                continue
            small = min((ba[2] - ba[0]) * (ba[3] - ba[1]), (bb[2] - bb[0]) * (bb[3] - bb[1]))
            ratio = area / small if small > 0 else 0
            if ratio > 0.35:
                warnings.append(
                    f"visual: element {ea.get('id')!r} overlaps {eb.get('id')!r} "
                    f"({area:.0f}px^2, {ratio:.0%} of smaller)"
                )

    # Dangling arrows (no binding at all)
    for el in elements:
        if not isinstance(el, dict) or el.get("type") != "arrow":
            continue
        start = el.get("startBinding") or {}
        end = el.get("endBinding") or {}
        if not start.get("elementId") and not end.get("elementId"):
            warnings.append(
                f"visual: arrow {el.get('id')!r} is not bound to any node (dangling)"
            )

    # Sketch readability contract: labels stay legible and bilingual text is
    # split into separate lines/fonts by the generator.
    for el in elements:
        if not isinstance(el, dict) or el.get("type") != "text":
            continue
        text = str(el.get("text", ""))
        if sketch and any(ord(ch) >= 0x2E80 for ch in text) and el.get("fontFamily") in (1, 2, 3):
            warnings.append(f"visual: CJK text {el.get('id')!r} uses a non-CJK font family")
        if sketch and not any(ord(ch) >= 0x2E80 for ch in text) and el.get("fontFamily") == 11:
            warnings.append(f"visual: English text {el.get('id')!r} uses Ma Shan Zheng")
        if sketch and str(el.get("id", "")).startswith("elbl-") and float(el.get("fontSize", 0) or 0) < 32:
            warnings.append(f"visual: edge label {el.get('id')!r} is below 32px")
        if el.get("containerId") and el.get("width", 0) < 24:
            warnings.append(f"visual: text {el.get('id')!r} has insufficient node padding")

    # Title safety zone: titles should not touch the top canvas edge.
    for el in elements:
        if isinstance(el, dict) and el.get("type") == "text" and str(el.get("id", "")).startswith("title-"):
            if sketch and float(el.get("y", 0) or 0) < 10:
                warnings.append(f"visual: title {el.get('id')!r} is inside the top safety zone")

    titles = [el for el in elements if isinstance(el, dict) and el.get("type") == "text" and str(el.get("id", "")).startswith("title-")]
    edge_labels = [el for el in elements if isinstance(el, dict) and el.get("type") == "text" and str(el.get("id", "")).startswith("elbl-")]
    for title in titles:
        tb = _bbox(title)
        if not tb:
            continue
        for label in edge_labels:
            lb = _bbox(label)
            if lb and _rects_overlap(tb, lb) > 0:
                warnings.append(f"visual: title {title.get('id')!r} overlaps edge label {label.get('id')!r}")

    # Layout density: minimum spacing between containers
    for i in range(len(containers)):
        for j in range(i + 1, len(containers)):
            (ia, ea, ba), (ib, eb, bb) = containers[i], containers[j]
            if set(ea.get("groupIds") or ()) & set(eb.get("groupIds") or ()):
                continue
            ax1, ay1, ax2, ay2 = ba
            bx1, by1, bx2, by2 = bb
            gap_x = max(bx1 - ax2, ax1 - bx2, 0)
            gap_y = max(by1 - ay2, ay1 - by2, 0)
            if gap_x == 0 and gap_y == 0:
                continue
            distance = (gap_x**2 + gap_y**2) ** 0.5
            if distance < 20:
                warnings.append(
                    f"visual: {ea.get('id')!r} and {eb.get('id')!r} are too close "
                    f"(gap {distance:.0f}px < 20px)"
                )

    if visual_contract is not None:
        # A contract makes visible shapes accountable. Frames and text labels
        # are structural; all other visible drawing elements need a mapping.
        for el in elements:
            if not isinstance(el, dict) or el.get("type") in ("frame", "text"):
                continue
            if el.get("opacity", 100) == 0 or el.get("type") not in (
                "rectangle", "ellipse", "diamond", "arrow", "line", "image"
            ):
                continue
            custom = el.get("customData") or {}
            if not custom.get("semanticRole") or not custom.get("visualFactIds"):
                warnings.append(
                    f"visual-contract: element {el.get('id')!r} has no semanticRole/visualFactIds mapping"
                )

        families = visual_contract.get("visual_families", {})
        declared = {families.get("primary")} | set(families.get("supporting") or [])
        actual = {
            (el.get("customData") or {}).get("visualFamily")
            for el in elements if (el.get("customData") or {}).get("visualFamily")
        }
        for family in sorted(actual - declared):
            warnings.append(f"visual-contract: undeclared visual family {family!r}")
        if len(actual) > len(declared):
            warnings.append(
                f"visual-contract: {len(actual)} visual families used, maximum declared is {len(declared)}"
            )

        allowed_colors = ((visual_contract.get("layout_signals") or {}).get("allowed_colors") or [])
        if allowed_colors:
            allowed = {str(color).lower() for color in allowed_colors}
            for el in elements:
                for field in ("strokeColor", "backgroundColor"):
                    color = el.get(field)
                    if isinstance(color, str) and color.lower() not in allowed and color.lower() not in ("transparent", "none"):
                        warnings.append(
                            f"visual-contract: element {el.get('id')!r} uses undeclared {field} {color!r}"
                        )


def validate_file(filepath, strict=False, visual=False):
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
            elif all(
                isinstance(point, list)
                and len(point) == 2
                and all(isinstance(value, (int, float)) for value in point)
                for point in points
            ):
                span_x = max(point[0] for point in points) - min(point[0] for point in points)
                span_y = max(point[1] for point in points) - min(point[1] for point in points)
                if abs(el.get("width", 0) - span_x) > 0.01 or abs(el.get("height", 0) - span_y) > 0.01:
                    warnings.append(
                        f"{label}: arrow width/height must match point extents "
                        f"({span_x:g} x {span_y:g})"
                    )

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

    if visual:
        app_state = data.get("appState") or {}
        sketch = bool(app_state.get("sketchStyle") or app_state.get("sketchTemplate") or app_state.get("cjkFontFamily"))
        _visual_checks(elements, warnings, data.get("visual_contract"), sketch=sketch)

    return errors, warnings, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Path to .excalidraw file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--fail-on-warning", action="store_true", help="Fail when any warning is emitted (alias for strict)")
    parser.add_argument("--visual", action="store_true", help="Run layout quality heuristics (overlap/dangling/density)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    strict = args.strict or args.fail_on_warning
    errors, warnings, stats = validate_file(args.file, strict, args.visual)

    if args.json:
        result = {
            "file": args.file,
            "ok": len(errors) == 0 and not (strict and warnings),
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

    if errors or (strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
