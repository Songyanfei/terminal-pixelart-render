"""Render images as terminal pixel art using Unicode half-block characters."""

import argparse
import os
import shutil
import sys

from PIL import Image, ImageOps

UPPER_HALF_BLOCK = "\u2580"  # ▀
RESET = "\033[0m"
GRAYSCALE_RAMP = " .,:;+*?%S#@"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pixelart",
        description="Render an image as terminal pixel art using Unicode half-block characters.",
    )
    parser.add_argument("image", help="Path to the image file")
    parser.add_argument(
        "-w", "--width",
        type=int,
        default=None,
        help="Output width in terminal columns (default: auto-detect)",
    )
    parser.add_argument(
        "-n", "--no-color",
        action="store_true",
        help="Render in grayscale ASCII instead of color",
    )
    parser.add_argument(
        "--256color",
        action="store_true",
        dest="force_256",
        help="Force 256-color mode instead of true color",
    )
    return parser


def get_terminal_size() -> os.terminal_size:
    try:
        return shutil.get_terminal_size((80, 24))
    except (AttributeError, ValueError, OSError):
        return os.terminal_size((80, 24))


def detect_color_mode(args) -> str:
    if args.no_color:
        return "grayscale"
    if getattr(args, "force_256", False):
        return "256color"
    colorterm = os.environ.get("COLORTERM", "")
    if colorterm in ("truecolor", "24bit"):
        return "truecolor"
    return "truecolor"


def load_and_resize(image_path: str, target_width: int) -> Image.Image:
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")

    orig_w, orig_h = img.size
    target_height = round(target_width * orig_h / orig_w)
    if target_height % 2 != 0:
        target_height += 1
    target_height = max(target_height, 2)

    return img.resize((target_width, target_height), Image.LANCZOS)


def rgb_to_256(r: int, g: int, b: int) -> int:
    return 16 + round(r * 5 / 255) * 36 + round(g * 5 / 255) * 6 + round(b * 5 / 255)


def render_image(img: Image.Image, color_mode: str) -> str:
    pixels = img.load()
    width, height = img.size
    rows = []

    for y in range(0, height, 2):
        row_parts = []
        prev_fg = None
        prev_bg = None

        for x in range(width):
            top_r, top_g, top_b = pixels[x, y]

            if y + 1 < height:
                bot_r, bot_g, bot_b = pixels[x, y + 1]
            else:
                bot_r, bot_g, bot_b = 0, 0, 0

            if color_mode == "truecolor":
                top_color = (top_r, top_g, top_b)
                bot_color = (bot_r, bot_g, bot_b)
                if top_color != prev_fg:
                    row_parts.append(f"\033[38;2;{top_r};{top_g};{top_b}m")
                    prev_fg = top_color
                if bot_color != prev_bg:
                    row_parts.append(f"\033[48;2;{bot_r};{bot_g};{bot_b}m")
                    prev_bg = bot_color
                row_parts.append(UPPER_HALF_BLOCK)

            elif color_mode == "256color":
                fg_idx = rgb_to_256(top_r, top_g, top_b)
                bg_idx = rgb_to_256(bot_r, bot_g, bot_b)
                if fg_idx != prev_fg:
                    row_parts.append(f"\033[38;5;{fg_idx}m")
                    prev_fg = fg_idx
                if bg_idx != prev_bg:
                    row_parts.append(f"\033[48;5;{bg_idx}m")
                    prev_bg = bg_idx
                row_parts.append(UPPER_HALF_BLOCK)

            else:  # grayscale
                brightness = 0.299 * top_r + 0.587 * top_g + 0.114 * top_b
                idx = round(brightness / 255 * (len(GRAYSCALE_RAMP) - 1))
                row_parts.append(GRAYSCALE_RAMP[idx])

        row_parts.append(RESET)
        rows.append("".join(row_parts))

    return "\n".join(rows)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print(f"Error: file not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    try:
        width = args.width or get_terminal_size().columns
        color_mode = detect_color_mode(args)

        img = load_and_resize(args.image, width)
        output = render_image(img, color_mode)

        sys.stdout.write(output)
        sys.stdout.write("\n")
        sys.stdout.flush()

    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)

    except KeyboardInterrupt:
        sys.exit(130)

    except Image.UnidentifiedImageError:
        print(f"Error: cannot identify image file: {args.image}", file=sys.stderr)
        sys.exit(1)

    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
