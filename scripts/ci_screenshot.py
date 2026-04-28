#!/usr/bin/env python3
"""Capture a full-screen screenshot and save as WEBP.

Usage: python scripts/ci_screenshot.py output.webp
"""
import os
import sys

try:
    from mss import MSS
    from PIL import Image
except Exception:
    print("Missing dependencies: please install mss and pillow.")
    raise


def capture(output_path: str) -> int:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with MSS() as sct:
        monitor = sct.monitors[0]
        sct_img = sct.grab(monitor)
        img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
        img.save(output_path, 'WEBP', quality=85)
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: ci_screenshot.py OUTPUT_PATH")
        return 2
    output = sys.argv[1]
    try:
        return capture(output)
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
