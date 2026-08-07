#!/usr/bin/env python3
"""
增量编辑与迭代工具 — 合并新旧 Excalidraw 场景，保留旧元素 id，支持微调/重排/回退。

用法：
  # 合并：旧场景 + 新场景，按 id 保留旧元素，新元素用新 id（冲突时后缀 -new）
  python3 scripts/merge_excalidraw.py merge base.excalidraw update.excalidraw --output out.excalidraw

  # 微调：修改指定元素的属性（位置/颜色/文字）
  python3 scripts/merge_excalidraw.py patch scene.excalidraw --set 'rect-1.x=150' --set 'rect-1.y=200'
  python3 scripts/merge_excalidraw.py patch scene.excalidraw --set 'text-1.text=新标题' --set 'rect-1.backgroundColor=#b2f2bb'
  python3 scripts/merge_excalidraw.py patch scene.excalidraw --move 'rect-1:20,30'   # 相对位移

  # 备份历史（每次 patch 前自动备份到 output/history/）
  python3 scripts/merge_excalidraw.py patch scene.excalidraw --set 'a.x=1' --history-dir output/history

  # 回退到备份
  python3 scripts/merge_excalidraw.py restore scene.excalidraw output/history/backup-20260808-120000.excalidraw
"""

import argparse
import json
import os
import re
import shutil
import sys
import time


def load_scene(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_scene(scene, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(scene, fh, ensure_ascii=False, indent=2)


def backup(scene, history_dir, label="backup"):
    if not history_dir:
        return None
    os.makedirs(history_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(history_dir, f"{label}-{ts}.excalidraw")
    save_scene(scene, path)
    return path


def merge_scenes(base, update):
    """Merge two scenes: keep base element ids, add new elements with unique ids."""
    out = json.loads(json.dumps(base))
    existing = {}
    for el in out.get("elements", []):
        existing[el.get("id")] = el

    for el in update.get("elements", []):
        eid = el.get("id")
        if eid in existing:
            # Preserve existing element, but copy over non-geometric fields
            # (text, colors) so content edits flow through; keep geometry stable
            old = existing[eid]
            merged = dict(old)
            for k, v in el.items():
                if k in ("x", "y", "width", "height", "version", "versionNonce", "updated", "seed"):
                    continue  # keep old geometry
                merged[k] = v
            existing[eid] = merged
        else:
            # New element: ensure unique id
            new_id = eid
            seen = set(existing.keys())
            if new_id in seen:
                new_id = f"{eid}-new"
                counter = 2
                while new_id in seen:
                    new_id = f"{eid}-new{counter}"
                    counter += 1
            new_el = json.loads(json.dumps(el))
            new_el["id"] = new_id
            existing[new_id] = new_el

    out["elements"] = list(existing.values())
    return out


def parse_prop_set(expr):
    """Parse 'elementId.field=value' into (id, field, raw_value)."""
    m = re.match(r"^([^.\s]+)\.([^=\s]+)=(.*)$", expr)
    if not m:
        return None
    eid, field, raw = m.group(1), m.group(2), m.group(3)
    return eid, field, raw


def coerce_value(raw):
    """Coerce string value to number/bool/null where applicable."""
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if raw.lower() in ("null", "none"):
        return None
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        return float(raw)
    except ValueError:
        return raw


def patch_scene(scene, sets=None, moves=None):
    """Apply --set and --move operations in place."""
    by_id = {el.get("id"): el for el in scene.get("elements", [])}

    if sets:
        for expr in sets:
            parsed = parse_prop_set(expr)
            if not parsed:
                print(f"[WARN] 无法解析 --set 表达式: {expr!r}（应为 elementId.field=value）")
                continue
            eid, field, raw = parsed
            if eid not in by_id:
                print(f"[WARN] 元素 {eid!r} 不存在，跳过 {field}={raw}")
                continue
            by_id[eid][field] = coerce_value(raw)
            print(f"[OK] 设置 {eid}.{field} = {by_id[eid][field]!r}")

    if moves:
        for expr in moves:
            m = re.match(r"^([^:\s]+):\s*([+-]?\d+(?:\.\d+)?)\s*,\s*([+-]?\d+(?:\.\d+)?)$", expr)
            if not m:
                print(f"[WARN] 无法解析 --move 表达式: {expr!r}（应为 elementId:dx,dy）")
                continue
            eid, dx, dy = m.group(1), float(m.group(2)), float(m.group(3))
            if eid not in by_id:
                print(f"[WARN] 元素 {eid!r} 不存在，跳过移动")
                continue
            el = by_id[eid]
            el["x"] = (el.get("x") or 0) + dx
            el["y"] = (el.get("y") or 0) + dy
            print(f"[OK] 移动 {eid} → ({el['x']:.1f}, {el['y']:.1f})")
    return scene


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p_merge = sub.add_parser("merge", help="合并两个场景")
    p_merge.add_argument("base")
    p_merge.add_argument("update")
    p_merge.add_argument("--output", "-o", required=True)

    p_patch = sub.add_parser("patch", help="微调元素属性")
    p_patch.add_argument("file")
    p_patch.add_argument("--set", action="append", help="elementId.field=value")
    p_patch.add_argument("--move", action="append", help="elementId:dx,dy")
    p_patch.add_argument("--output", "-o", help="输出文件（默认覆盖原文件）")
    p_patch.add_argument("--history-dir", default="output/history", help="备份目录")

    p_restore = sub.add_parser("restore", help="从备份恢复")
    p_restore.add_argument("target")
    p_restore.add_argument("backup_file")

    args = ap.parse_args()

    if args.command == "merge":
        base = load_scene(args.base)
        update = load_scene(args.update)
        out = merge_scenes(base, update)
        save_scene(out, args.output)
        print(f"[OK] 合并完成: {args.output} ({len(out['elements'])} elements)")

    elif args.command == "patch":
        scene = load_scene(args.file)
        bk = backup(scene, args.history_dir, "backup")
        if bk:
            print(f"[OK] 已备份: {bk}")
        scene = patch_scene(scene, sets=args.set, moves=args.move)
        out_path = args.output or args.file
        save_scene(scene, out_path)
        print(f"[OK] 已保存: {out_path}")

    elif args.command == "restore":
        if not os.path.exists(args.backup_file):
            print(f"[ERROR] 备份文件不存在: {args.backup_file}")
            sys.exit(1)
        shutil.copyfile(args.backup_file, args.target)
        print(f"[OK] 已从 {args.backup_file} 恢复到 {args.target}")


if __name__ == "__main__":
    main()
