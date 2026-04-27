"""Convert image to HTML pixel art for browser preview."""

import sys
import os
from PIL import Image, ImageOps

def render_html(image_path: str, width: int = 66) -> str:
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")

    orig_w, orig_h = img.size
    target_height = round(width * orig_h / orig_w)
    if target_height % 2 != 0:
        target_height += 1
    img = img.resize((width, target_height), Image.LANCZOS)

    pixels = img.load()
    w, h = img.size
    rows = []

    for y in range(0, h, 2):
        cells = []
        for x in range(w):
            tr, tg, tb = pixels[x, y]
            if y + 1 < h:
                br, bg_, bb = pixels[x, y + 1]
            else:
                br, bg_, bb = 0, 0, 0
            cells.append(
                f'<span style="color:rgb({tr},{tg},{tb});'
                f'background:rgb({br},{bg_},{bb})">&#9600;</span>'
            )
        rows.append("".join(cells))

    body = "<br>\n".join(rows)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ background: #000; margin: 0; padding: 8px; }}
pre {{ font-size: 10px; line-height: 10px; letter-spacing: 0; }}
</style></head>
<body><pre>{body}</pre></body></html>"""


if __name__ == "__main__":
    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 66
    html = render_html(image_path, width)
    out_path = os.path.splitext(image_path)[0] + ".html"
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Saved to {out_path}")
