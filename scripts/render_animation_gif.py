#!/usr/bin/env python3
"""
关键帧动画 → GIF 导出（E.3 演示，借鉴 excalimate）

读取 .excalidraw 中的 customData.animate 顺序元数据，按 order 分组生成逐帧
SVG，再用 Playwright/Chromium（或共享 svg_render fallback）渲染为 PNG 帧，
最后用 PIL 合成 GIF。

用法：
  python3 scripts/render_animation_gif.py <file.excalidraw> [--output out.gif]
      [--duration 1200] [--loop 0]

依赖：Python PIL（pip install pillow）+ 可选 Playwright（高质量帧渲染）。
无 Playwright 时自动用共享 svg_render.js 生成 SVG 帧并转 PNG（需 rsvg-convert
或 cairosvg；都没有则降级输出帧 SVG 清单并提示）。
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile


def collect_frames(scene):
    """按 customData.animate.order 分组元素 id，返回 [(order, [ids])] 排序列表。"""
    orders = {}
    for el in scene.get("elements", []):
        order = (el.get("customData") or {}).get("animate", {}).get("order")
        if order is None:
            continue
        orders.setdefault(order, []).append(el["id"])
    return sorted(orders.items())


def render_frames_svg(scene_file, orders, outdir):
    """用共享 svg_render.js 渲染每帧 SVG。返回 [svg_path]。"""
    node_script = os.path.join(os.path.dirname(__file__), "lib", "svg_render.js")
    helper = os.path.join(os.path.dirname(__file__), "_gif_frames.js")
    frames = [o for o, _ in orders]
    with open(helper, "w") as f:
        f.write('''"use strict";
const fs = require("fs");
const path = require("path");
const { renderSvgFromScene } = require(process.argv[2]);
const scene = JSON.parse(fs.readFileSync(process.argv[3], "utf-8"));
const outdir = process.argv[4];
const orders = JSON.parse(process.argv[5]);
const out = [];
for (const order of orders) {
  const { svg } = renderSvgFromScene(scene, { padding: 40, maxOrder: order });
  const p = path.join(outdir, `frame-${order}.svg`);
  fs.writeFileSync(p, svg);
  out.push(p);
}
console.log(JSON.stringify(out));
''')
    try:
        r = subprocess.run(
            ["node", helper, node_script, scene_file, outdir, json.dumps(frames)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            print(f"[ERROR] svg frame render failed: {r.stderr}", file=sys.stderr)
            return None
        return json.loads(r.stdout.strip())
    finally:
        try:
            os.unlink(helper)
        except OSError:
            pass


def svg_to_png(svg_path, png_path):
    """SVG → PNG：优先 cairosvg，其次 rsvg-convert。返回 bool。"""
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=1200)
        return True
    except Exception:
        pass
    for cmd in (["rsvg-convert", "-w", "1200", "-o", png_path, svg_path],
                ["ffmpeg", "-y", "-loglevel", "error", "-i", svg_path, png_path]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and os.path.exists(png_path):
                return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def build_gif(png_paths, gif_path, duration_ms):
    from PIL import Image
    frames = []
    for p in png_paths:
        img = Image.open(p).convert("RGBA")
        # 统一画布尺寸（白色背景）
        frames.append(img)
    w = max(f.width for f in frames)
    h = max(f.height for f in frames)
    canvas = []
    for f in frames:
        bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        bg.paste(f, (0, 0), f)
        canvas.append(bg.convert("RGB"))
    canvas[0].save(
        gif_path, save_all=True, append_images=canvas[1:],
        duration=duration_ms, loop=0, optimize=True,
    )
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help=".excalidraw 文件路径")
    ap.add_argument("--output", "-o", default=None, help="输出 GIF 路径（默认 <file>.gif）")
    ap.add_argument("--duration", type=int, default=1200, help="每帧停留毫秒（默认 1200）")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        scene = json.load(f)
    orders = collect_frames(scene)
    if not orders:
        print("[ERROR] 画布没有动画元数据（customData.animate）。先用 ir_to_excalidraw.py 生成。")
        sys.exit(1)
    print(f"[OK] 动画顺序: {[o for o, _ in orders]}")

    out_path = args.output or (args.file.replace(".excalidraw", "") + ".gif")
    with tempfile.TemporaryDirectory(prefix="excalidraw-gif-") as tmp:
        svg_paths = render_frames_svg(args.file, orders, tmp)
        if not svg_paths:
            sys.exit(1)
        png_paths = []
        for svg_path in svg_paths:
            png = svg_path.replace(".svg", ".png")
            if not svg_to_png(svg_path, png):
                print("[WARN] 无 cairosvg/rsvg-convert/ffmpeg SVG→PNG 支持，跳过 PNG。")
                break
            png_paths.append(png)
        if not png_paths:
            print("[ERROR] 无法将 SVG 帧转为 PNG（安装 cairosvg: pip install cairosvg）")
            sys.exit(1)
        build_gif(png_paths, out_path, args.duration)
    print(f"[OK] 已生成: {out_path}（{len(png_paths)} 帧, 每帧 {args.duration}ms）")


if __name__ == "__main__":
    main()
