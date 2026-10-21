# -*- coding: utf-8 -*-
"""把动作 GIF 转成动画 WebP（C2）。

WebP 动画在 180px 的演示图上是无损可接受的，体积通常只有 GIF 的 1/3。
保留原 GIF 作为老浏览器（Safari < 14）的回退，前端按 <img src=webp onerror→gif> 兜底。

用法：python3 scripts/make_webp.py [--quality 75] [--force]
"""
import argparse
import glob
import os
import sys
from PIL import Image, ImageSequence

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.path.join(BASE, "videos")


def convert(gif_path, quality, force=False):
    webp_path = os.path.splitext(gif_path)[0] + ".webp"
    if os.path.exists(webp_path) and not force:
        return None
    im = Image.open(gif_path)
    durations, frames = [], []
    for frame in ImageSequence.Iterator(im):
        durations.append(frame.info.get("duration", 100) or 100)
        frames.append(frame.convert("RGB").copy())
    if not frames:
        return None
    frames[0].save(
        webp_path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=im.info.get("loop", 0),
        quality=quality,
        method=6,
    )
    return os.path.getsize(gif_path), os.path.getsize(webp_path), len(frames)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", type=int, default=75)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(VIDEO_DIR, "*.gif")))
    if not files:
        print("videos/ 里没有找到 GIF")
        return 1
    total_gif = total_webp = done = skipped = 0
    for i, f in enumerate(files, 1):
        res = convert(f, args.quality, args.force)
        if res is None:
            skipped += 1
            continue
        g, w, n = res
        total_gif += g
        total_webp += w
        done += 1
        print(f"[{i}/{len(files)}] {os.path.basename(f)} {g/1024:.0f}KB -> {w/1024:.0f}KB ({n} 帧)")
    if done:
        saved = 1 - total_webp / total_gif
        print(f"\n转换 {done} 个，跳过 {skipped} 个")
        print(f"GIF 合计 {total_gif/1048576:.2f} MB -> WebP 合计 {total_webp/1048576:.2f} MB，节省 {saved:.0%}")
    else:
        print(f"无需转换（跳过 {skipped} 个）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
