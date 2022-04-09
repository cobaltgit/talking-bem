from PIL import Image, ImageFont, ImageDraw
import textwrap
from io import BytesIO

def generate_news(image: BytesIO, text: str = None) -> BytesIO:
    IMAGE_BACKGROUND = "files/news_bg.jpg"
    size = 152,85
    with Image.open(IMAGE_BACKGROUND) as bg_img:
        bg = bg_img.copy()
        with Image.open(image) as fg:
            fg = fg.resize(size, Image.ANTIALIAS)
            bg.paste(fg, (181,156))
        if text is not None:
            draw = ImageDraw.Draw(bg)
            w,h = bg.size
            font = ImageFont.truetype(font="files/Impact.ttf", size=h // 10)
            cw, ch = font.getsize("A")
            cpl = w // cw
            lines = textwrap.wrap(text, width=cpl)

            y = 1
            for line in lines:
                lw, lh = font.getsize(line)
                x = (w - lw) / 2
                draw.text((x - 1, y), line, font=font, fill="black")
                draw.text((x + 1, y), line, font=font, fill="black")
                draw.text((x, y - 1), line, font=font, fill="black")
                draw.text((x, y + 1), line, font=font, fill="black")
                draw.text((x, y), line, fill="white", font=font)
                y += lh
        out = BytesIO()
        bg.save(out, format="png")
        out.seek(0)
        return out