"""Generate stt.ico for the compiled exe."""
from PIL import Image, ImageDraw, ImageFont
import os

def make_icon():
    sizes = [256, 128, 64, 48, 32, 16]
    frames = []

    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d   = ImageDraw.Draw(img)

        pad = size * 0.08

        # Dark rounded background
        d.rounded_rectangle(
            [pad, pad, size - pad, size - pad],
            radius=size * 0.18,
            fill=(30, 30, 30, 255),
        )

        # Mic body (white rounded rect)
        mx1 = size * 0.35
        mx2 = size * 0.65
        my1 = size * 0.12
        my2 = size * 0.58
        d.rounded_rectangle([mx1, my1, mx2, my2], radius=size * 0.14, fill=(255, 255, 255, 255))

        # Arc (mic stand)
        aw  = size * 0.22
        ax1 = size * 0.5 - aw
        ax2 = size * 0.5 + aw
        ay1 = size * 0.38
        ay2 = size * 0.70
        lw  = max(2, int(size * 0.055))
        d.arc([ax1, ay1, ax2, ay2], start=0, end=180, fill=(255, 255, 255, 255), width=lw)

        # Vertical pole
        px  = size * 0.5 - lw / 2
        py1 = size * 0.68
        py2 = size * 0.78
        d.rectangle([px, py1, px + lw, py2], fill=(255, 255, 255, 255))

        # Base bar
        bw  = size * 0.24
        bh  = max(2, int(size * 0.055))
        bx1 = size * 0.5 - bw
        bx2 = size * 0.5 + bw
        by  = size * 0.78
        d.rounded_rectangle([bx1, by, bx2, by + bh], radius=bh // 2, fill=(255, 255, 255, 255))

        # "STT" label at bottom — only for larger sizes
        if size >= 48:
            font_size = max(8, int(size * 0.155))
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except Exception:
                font = ImageFont.load_default()

            text   = "STT"
            bbox   = d.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx     = (size - tw) / 2
            ty     = size * 0.84
            d.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

        frames.append(img)

    out = os.path.join(os.path.dirname(__file__), "stt.ico")
    frames[0].save(
        out,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )
    print(f"Icon saved: {out}")


if __name__ == "__main__":
    make_icon()
