#!/usr/bin/env python3
"""Assemble three platform screenshots into individual webp files and a combined thumbnail.

Usage:
  python scripts/assemble_thumbnails.py --windows path --linux path --macos path --output thumbnail.webp

The script will also write the individual images to `src/assets/img/{windows,linux,macos}.webp` if paths provided.
"""
import argparse
import os
from PIL import Image


def load_or_fail(path):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(path)
    return Image.open(path).convert('RGBA')


def compose_side_by_side(images, spacing=8, bg=(255, 255, 255, 0)):
    widths, heights = zip(*(im.size for im in images))
    total_width = sum(widths) + spacing * (len(images) - 1)
    max_height = max(heights)

    result = Image.new('RGBA', (total_width, max_height), bg)
    x = 0
    for im in images:
        y = (max_height - im.size[1]) // 2
        result.paste(im, (x, y), im)
        x += im.size[0] + spacing
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--windows', required=True)
    p.add_argument('--linux', required=True)
    p.add_argument('--macos', required=True)
    p.add_argument('--out-windows', default='src/assets/img/windows.webp')
    p.add_argument('--out-linux', default='src/assets/img/linux.webp')
    p.add_argument('--out-macos', default='src/assets/img/macos.webp')
    p.add_argument('--output', default='src/assets/img/thumbnail.webp')
    args = p.parse_args()

    imgs = []
    imgs.append(load_or_fail(args.windows))
    imgs.append(load_or_fail(args.linux))
    imgs.append(load_or_fail(args.macos))

    # Save individual images (normalize to webp)
    os.makedirs(os.path.dirname(args.out_windows), exist_ok=True)
    imgs[0].save(args.out_windows, 'WEBP', quality=85)
    imgs[1].save(args.out_linux, 'WEBP', quality=85)
    imgs[2].save(args.out_macos, 'WEBP', quality=85)

    combined = compose_side_by_side(imgs, spacing=12)
    combined.save(args.output, 'WEBP', quality=85)
    print(f"Wrote {args.out_windows}, {args.out_linux}, {args.out_macos}, and {args.output}")


if __name__ == '__main__':
    main()
