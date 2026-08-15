#!/usr/bin/env python3
"""Validate a .excalidraw v2 file: structure, field types, and reference integrity.

Usage:
    python3 validate_excalidraw.py <file.excalidraw> [--strict] [--json]

Exit code 0 = OK; 1 = errors found. Warnings never fail unless --strict.
"""

import argparse
import json
import math
import sys
from pathlib import Path


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


def normalize_arrow_geometry(data):
    """Set arrow width/height to the exact extents of its local points."""
    changed = []
    for el in data.get("elements") or []:
        if not isinstance(el, dict) or el.get("type") != "arrow":
            continue
        points = el.get("points")
        if not isinstance(points, list) or len(points) < 2 or not all(
            isinstance(point, list)
            and len(point) == 2
            and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in point)
            for point in points
        ):
            continue
        span_x = max(point[0] for point in points) - min(point[0] for point in points)
        span_y = max(point[1] for point in points) - min(point[1] for point in points)
        if abs(float(el.get("width", 0) or 0) - span_x) <= 0.01 and abs(float(el.get("height", 0) or 0) - span_y) <= 0.01:
            continue
        el["width"] = span_x
        el["height"] = span_y
        changed.append(el.get("id", ""))
    return changed


def fix_arrow_geometry_file(filepath):
    """Normalize a scene in place; invalid JSON remains untouched for validation."""
    path = Path(filepath)
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = normalize_arrow_geometry(data)
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


def _bbox(el):
    """Return the axis-aligned box, including Excalidraw rotation."""
    if not isinstance(el, dict):
        return None
    x, y = el.get("x"), el.get("y")
    w, h = el.get("width"), el.get("height")
    if not all(isinstance(v, (int, float)) for v in (x, y, w, h)):
        return None
    angle = el.get("angle", 0) or 0
    if not isinstance(angle, (int, float)) or abs(angle) < 1e-9:
        return (x, y, x + w, y + h)
    cx, cy = x + w / 2, y + h / 2
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    corners = []
    for px, py in ((x, y), (x + w, y), (x + w, y + h), (x, y + h)):
        dx, dy = px - cx, py - cy
        corners.append((cx + dx * cos_a - dy * sin_a, cy + dx * sin_a + dy * cos_a))
    xs = [point[0] for point in corners]
    ys = [point[1] for point in corners]
    return (min(xs), min(ys), max(xs), max(ys))


def _hex_rgb(value):
    if not isinstance(value, str) or not value.startswith("#"):
        return None
    raw = value[1:]
    if len(raw) == 3:
        raw = "".join(char * 2 for char in raw)
    if len(raw) != 6:
        return None
    try:
        return tuple(int(raw[index:index + 2], 16) / 255 for index in (0, 2, 4))
    except ValueError:
        return None


def _relative_luminance(value):
    rgb = _hex_rgb(value)
    if rgb is None:
        return None
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in rgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(foreground, background):
    fg, bg = _relative_luminance(foreground), _relative_luminance(background)
    if fg is None or bg is None:
        return None
    light, dark = max(fg, bg), min(fg, bg)
    return (light + 0.05) / (dark + 0.05)


def _id_has_prefix(el, prefix):
    value = str(el.get("id", ""))
    return value.startswith(prefix) or value.split("--")[-1].startswith(prefix)


def _rects_overlap(a, b):
    """Return overlap area (px^2) between two bboxes, or 0 if none."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ox = max(0, min(ax2, bx2) - max(ax1, bx1))
    oy = max(0, min(ay2, by2) - max(ay1, by1))
    return ox * oy


def _rect_area(bbox):
    """Return bbox area, guarding malformed or degenerate boxes."""
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)


def _point_in_rect(point, bbox):
    x, y = point
    x1, y1, x2, y2 = bbox
    return x1 <= x <= x2 and y1 <= y <= y2


def _segments_intersect(a, b, c, d):
    """Return True when two line segments intersect."""
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    def on_segment(p, q, r):
        return (
            min(p[0], r[0]) <= q[0] <= max(p[0], r[0])
            and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])
        )

    o1 = orient(a, b, c)
    o2 = orient(a, b, d)
    o3 = orient(c, d, a)
    o4 = orient(c, d, b)
    if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0):
        return True
    eps = 1e-9
    return (
        abs(o1) <= eps and on_segment(a, c, b)
        or abs(o2) <= eps and on_segment(a, d, b)
        or abs(o3) <= eps and on_segment(c, a, d)
        or abs(o4) <= eps and on_segment(c, b, d)
    )


def _segment_intersects_rect(p1, p2, bbox, pad=0):
    """Return True when a line segment crosses or enters a rectangle."""
    x1, y1, x2, y2 = bbox
    rect = (x1 - pad, y1 - pad, x2 + pad, y2 + pad)
    if _point_in_rect(p1, rect) or _point_in_rect(p2, rect):
        return True
    rx1, ry1, rx2, ry2 = rect
    edges = [
        ((rx1, ry1), (rx2, ry1)),
        ((rx2, ry1), (rx2, ry2)),
        ((rx2, ry2), (rx1, ry2)),
        ((rx1, ry2), (rx1, ry1)),
    ]
    return any(_segments_intersect(p1, p2, a, b) for a, b in edges)


def _visual_checks(
    elements,
    warnings,
    visual_contract=None,
    sketch=False,
    cjk_handwriting=False,
    delivery_profile=None,
    app_state=None,
):
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

    # Global font contract: every template/theme uses a registered CJK
    # handwriting family for Chinese while keeping its own Latin font.
    for el in elements:
        if not isinstance(el, dict) or el.get("type") != "text":
            continue
        text = str(el.get("text", ""))
        if cjk_handwriting and any(ord(ch) >= 0x2E80 for ch in text) and el.get("fontFamily") in (1, 2, 3):
            warnings.append(f"visual: CJK text {el.get('id')!r} uses a non-CJK font family")
        if cjk_handwriting and not any(ord(ch) >= 0x2E80 for ch in text) and el.get("fontFamily") in (11, 12, 13):
            warnings.append(f"visual: English text {el.get('id')!r} uses a CJK handwriting font")
        if sketch and _id_has_prefix(el, "elbl-") and float(el.get("fontSize", 0) or 0) < 32:
            warnings.append(f"visual: edge label {el.get('id')!r} is below 32px")
        if el.get("containerId") and el.get("width", 0) < 24:
            warnings.append(f"visual: text {el.get('id')!r} has insufficient node padding")

    # Title safety zone: titles should not touch the top canvas edge.
    for el in elements:
        if isinstance(el, dict) and el.get("type") == "text" and _id_has_prefix(el, "title-"):
            if sketch and float(el.get("y", 0) or 0) < 10:
                warnings.append(f"visual: title {el.get('id')!r} is inside the top safety zone")

    titles = [el for el in elements if isinstance(el, dict) and el.get("type") == "text" and _id_has_prefix(el, "title-")]
    edge_labels = [el for el in elements if isinstance(el, dict) and el.get("type") == "text" and _id_has_prefix(el, "elbl-")]
    for title in titles:
        tb = _bbox(title)
        if not tb:
            continue
        for label in edge_labels:
            lb = _bbox(label)
            if lb and _rects_overlap(tb, lb) > 0:
                warnings.append(f"visual: title {title.get('id')!r} overlaps edge label {label.get('id')!r}")

    # Readability guard: expressive hand-drawn edge labels are allowed to be
    # large, but they must not cover node body text. Container overlap alone can
    # be aesthetically acceptable in sketch diagrams; text occlusion is not.
    readable_texts = [
        el for el in elements
        if isinstance(el, dict)
        and el.get("type") == "text"
        and not _id_has_prefix(el, "elbl-")
        and not _id_has_prefix(el, "title-")
        and str(el.get("text", "")).strip()
    ]

    # Two independent text layers must not occupy the same readable area. The
    # previous checker only compared edge labels with body text, so title/body
    # collisions could pass strict validation even when they visibly stacked.
    for index, first in enumerate(readable_texts):
        first_box = _bbox(first)
        if not first_box:
            continue
        for second in readable_texts[index + 1:]:
            if first.get("containerId") and first.get("containerId") == second.get("containerId"):
                continue
            second_box = _bbox(second)
            if not second_box:
                continue
            area = _rects_overlap(first_box, second_box)
            if area <= 0:
                continue
            small = min(_rect_area(first_box), _rect_area(second_box))
            ratio = area / small if small > 0 else 0
            if area >= 20 or ratio >= 0.08:
                warnings.append(
                    f"visual: readable text {first.get('id')!r} overlaps "
                    f"{second.get('id')!r} ({area:.0f}px^2, {ratio:.0%} of smaller)"
                )
    for label in edge_labels:
        lb = _bbox(label)
        if not lb or not str(label.get("text", "")).strip():
            continue
        label_area = _rect_area(lb)
        if label_area <= 0:
            continue
        for text_el in readable_texts:
            if label.get("id") == text_el.get("id"):
                continue
            tb = _bbox(text_el)
            if not tb:
                continue
            area = _rects_overlap(lb, tb)
            if area <= 0:
                continue
            text_area = _rect_area(tb)
            small = min(label_area, text_area)
            ratio = area / small if small > 0 else 0
            if area >= 80 or ratio >= 0.08:
                warnings.append(
                    f"visual: edge label {label.get('id')!r} overlaps readable text "
                    f"{text_el.get('id')!r} ({area:.0f}px^2, {ratio:.0%} of smaller)"
                )

    # Readability guard: connector lines should not travel through body text
    # either. This catches the common content-map failure mode where a curved
    # feedback arrow visually slices through the central topic or a neighboring
    # card label without causing a container overlap warning.
    for arrow in elements:
        if not isinstance(arrow, dict) or arrow.get("type") != "arrow":
            continue
        points = arrow.get("points") or []
        if len(points) < 2 or not all(isinstance(p, list) and len(p) == 2 for p in points):
            continue
        try:
            abs_points = [
                (float(arrow.get("x", 0) or 0) + float(p[0]), float(arrow.get("y", 0) or 0) + float(p[1]))
                for p in points
            ]
        except (TypeError, ValueError):
            continue
        bound_ids = {
            eid for eid in (
                (arrow.get("startBinding") or {}).get("elementId"),
                (arrow.get("endBinding") or {}).get("elementId"),
            ) if eid
        }
        for text_el in readable_texts:
            if text_el.get("containerId") in bound_ids:
                continue
            tb = _bbox(text_el)
            if not tb:
                continue
            for p1, p2 in zip(abs_points, abs_points[1:]):
                if _segment_intersects_rect(p1, p2, tb, pad=4):
                    warnings.append(
                        f"visual: arrow {arrow.get('id')!r} crosses readable text {text_el.get('id')!r}"
                    )
                    break

    # Video/storyboard frames have a stricter presentation contract than a
    # freeform research board: rotated stickers and captions must stay inside
    # a safe area, and text must remain readable at recording scale.
    if delivery_profile == "video-storyboard":
        state = app_state or {}
        safe_margin = float(state.get("safeMargin", 40) or 40)
        frames = {
            el.get("id"): (_bbox(el), el)
            for el in elements
            if isinstance(el, dict) and el.get("type") == "frame" and _bbox(el)
        }
        by_id = {el.get("id"): el for el in elements if isinstance(el, dict)}
        for el in elements:
            frame_id = el.get("frameId") if isinstance(el, dict) else None
            if not frame_id or frame_id not in frames or el.get("type") == "frame":
                continue
            child_box = _bbox(el)
            frame_box, _ = frames[frame_id]
            if not child_box or not frame_box:
                continue
            fx1, fy1, fx2, fy2 = frame_box
            cx1, cy1, cx2, cy2 = child_box
            if cx1 < fx1 + safe_margin or cy1 < fy1 + safe_margin or cx2 > fx2 - safe_margin or cy2 > fy2 - safe_margin:
                warnings.append(
                    f"visual: element {el.get('id')!r} leaves frame {frame_id!r} safe area "
                    f"({safe_margin:g}px)"
                )

            if el.get("type") == "text":
                role = (el.get("customData") or {}).get("typographyRole")
                font_size = float(el.get("fontSize", 0) or 0)
                if role not in ("caption", "credit", "eyebrow") and font_size < 16:
                    warnings.append(
                        f"visual: video text {el.get('id')!r} is below 16px ({font_size:g}px)"
                    )
                container = by_id.get(el.get("containerId"))
                background = container.get("backgroundColor") if container else state.get("viewBackgroundColor", "#ffffff")
                if background in (None, "transparent", "none"):
                    background = state.get("viewBackgroundColor", "#ffffff")
                ratio = _contrast_ratio(el.get("strokeColor"), background)
                if ratio is not None and ratio < 3.0:
                    warnings.append(
                        f"visual: video text {el.get('id')!r} has low contrast ({ratio:.2f}:1)"
                    )

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

    # A native Excalidraw container is designed for one bound text element.
    # Multiple bound bilingual lines are a common source of post-import
    # re-centering and visible text collisions; composite bilingual cards should
    # use grouped independent text layers instead.
    bound_text_counts = {}
    for candidate in elements:
        if isinstance(candidate, dict) and candidate.get("type") == "text" and candidate.get("containerId"):
            container_id = candidate["containerId"]
            bound_text_counts[container_id] = bound_text_counts.get(container_id, 0) + 1
    for container_id, count in bound_text_counts.items():
        if count > 1:
            warnings.append(
                f"text container {container_id!r} has {count} bound text elements; "
                "use grouped independent layers for bilingual content"
            )

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
        sketch = bool(app_state.get("sketchStyle") or app_state.get("sketchTemplate"))
        cjk_handwriting = bool(app_state.get("cjkFontFamily"))
        delivery = data.get("delivery") or {}
        delivery_profile = (
            delivery.get("profile")
            or app_state.get("deliveryProfile")
            or app_state.get("delivery_profile")
        )
        _visual_checks(
            elements,
            warnings,
            data.get("visual_contract"),
            sketch=sketch,
            cjk_handwriting=cjk_handwriting,
            delivery_profile=delivery_profile,
            app_state={**app_state, **delivery},
        )

    return errors, warnings, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="Path to .excalidraw file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--fail-on-warning", action="store_true", help="Fail when any warning is emitted (alias for strict)")
    parser.add_argument("--visual", action="store_true", help="Run layout quality heuristics (overlap/dangling/density)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument(
        "--fix-arrow-geometry",
        action="store_true",
        help="Normalize arrow width/height from points before validation",
    )
    args = parser.parse_args()

    fixed_arrows = []
    if args.fix_arrow_geometry:
        try:
            fixed_arrows = fix_arrow_geometry_file(args.file)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            # The normal validator below reports the actionable file/JSON error.
            fixed_arrows = []

    strict = args.strict or args.fail_on_warning
    errors, warnings, stats = validate_file(args.file, strict, args.visual)

    if args.json:
        result = {
            "file": args.file,
            "ok": len(errors) == 0 and not (strict and warnings),
            "errors": errors,
            "warnings": warnings,
            "stats": stats,
            "fixed_arrows": fixed_arrows,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if fixed_arrows:
            print(f"[FIXED] {len(fixed_arrows)} arrow geometries")
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
