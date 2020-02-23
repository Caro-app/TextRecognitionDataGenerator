import random as rnd

from PIL import Image, ImageColor, ImageFont, ImageDraw, ImageFilter

import string
import re

# whitespace_unicode = u''
# for c in range(sys.maxunicode+1):
#     u = chr(c)
#     if unicodedata.category(u) == 'Zs':
#         whitespace_unicode += "\\u{:04X}".format(c)
WHITESPACE_UNICODE = r'[\u0020\u00A0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F\u3000]'
# control_unicode = u''
# for c in range(sys.maxunicode+1):
#     u = chr(c)
#     if unicodedata.category(u) == 'Cc':
#         control_unicode += "\\u{:04X}".format(c)
CONTROL_UNICODE = r'[\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008\u0009\u000A\u000B\u000C\u000D\u000E\u000F\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019\u001A\u001B\u001C\u001D\u001E\u001F\u007F\u0080\u0081\u0082\u0083\u0084\u0085\u0086\u0087\u0088\u0089\u008A\u008B\u008C\u008D\u008E\u008F\u0090\u0091\u0092\u0093\u0094\u0095\u0096\u0097\u0098\u0099\u009A\u009B\u009C\u009D\u009E\u009F]'

def generate(
    text, font_en, font_ch, text_color, font_size, orientation, space_width, character_spacing, fit
):

    # normalize whitespace
    text = re.sub(WHITESPACE_UNICODE, ' ', text)
    # normalize control unicode (e.g. backspace)
    text = re.sub(CONTROL_UNICODE, '', text)

    if orientation == 0:
        return _generate_horizontal_text(
            text, font_en, font_ch, text_color, font_size, space_width, character_spacing, fit
        )
    elif orientation == 1:
        return _generate_vertical_text(
            text, font_en, font_ch, text_color, font_size, space_width, character_spacing, fit
        )
    else:
        raise ValueError("Unknown orientation " + str(orientation))


def _generate_horizontal_text(
    text, font_en, font_ch, text_color, font_size, space_width, character_spacing, fit
):
    image_font_en = ImageFont.truetype(font=font_en, size=font_size)
    image_font_ch = ImageFont.truetype(font=font_ch, size=font_size)

    en_character = string.ascii_letters + string.digits + string.punctuation + " "

    space_width_en = int(image_font_en.getsize(" ")[0] * space_width)
    # space_width_ch = int(image_font_ch.getsize(" ")[0] * space_width)

    char_widths = []
    for c in text:
        if c.strip() != "":
            if c in en_character:
                char_widths.append(image_font_en.getsize(c)[0])
            else:
                char_widths.append(image_font_ch.getsize(c)[0])
        else:
            char_widths.append(space_width_en)

    text_width = sum(char_widths) + character_spacing * (len(text) - 1)
    text_height = max([image_font_en.getsize(c)[1] for c in text] + [image_font_ch.getsize(c)[1] for c in text])

    txt_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    txt_mask = Image.new("RGB", (text_width, text_height), (0, 0, 0))

    txt_img_draw = ImageDraw.Draw(txt_img)
    txt_mask_draw = ImageDraw.Draw(txt_mask, mode="RGB")
    txt_mask_draw.fontmode = "1"

    colors = [ImageColor.getrgb(c) for c in text_color.split(",")]
    c1, c2 = colors[0], colors[-1]

    fill = (
        rnd.randint(min(c1[0], c2[0]), max(c1[0], c2[0])),
        rnd.randint(min(c1[1], c2[1]), max(c1[1], c2[1])),
        rnd.randint(min(c1[2], c2[2]), max(c1[2], c2[2])),
    )

    for i, c in enumerate(text):
        if c in en_character:
            txt_img_draw.text(
                (sum(char_widths[0:i]) + i * character_spacing, 0),
                c,
                fill=fill,
                font=image_font_en,
            )
            txt_mask_draw.text(
                (sum(char_widths[0:i]) + i * character_spacing, 0),
                c,
                fill=((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255),
                font=image_font_en,
            )
        else:
            txt_img_draw.text(
                (sum(char_widths[0:i]) + i * character_spacing, 0),
                c,
                fill=fill,
                font=image_font_ch,
            )
            txt_mask_draw.text(
                (sum(char_widths[0:i]) + i * character_spacing, 0),
                c,
                fill=((i + 1) // (255 * 255), (i + 1) // 255, (i + 1) % 255),
                font=image_font_ch,
            )

    if fit:
        return txt_img.crop(txt_img.getbbox()), txt_mask.crop(txt_img.getbbox())
    else:
        return txt_img, txt_mask


def _generate_vertical_text(
    text, font_en, font_ch, text_color, font_size, space_width, character_spacing, fit
):
    image_font_en = ImageFont.truetype(font=font_en, size=font_size)
    image_font_ch = ImageFont.truetype(font=font_ch, size=font_size)

    en_character = string.ascii_letters + string.digits + string.punctuation + " "

    space_height_en = int(image_font_en.getsize(" ")[1] * space_width)

    char_heights = []
    for c in text:
        if c.strip() != "":
            if c in en_character:
                char_heights.append(image_font_en.getsize(c)[1])
            else:
                char_heights.append(image_font_ch.getsize(c)[1])
        else:
            char_heights.append(space_height_en)

    text_width = max([image_font_en.getsize(c)[0] for c in text] + [image_font_ch.getsize(c)[0] for c in text])

    text_height = sum(char_heights) + character_spacing * len(text)

    txt_img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    txt_mask = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))

    txt_img_draw = ImageDraw.Draw(txt_img)
    txt_mask_draw = ImageDraw.Draw(txt_img)

    colors = [ImageColor.getrgb(c) for c in text_color.split(",")]
    c1, c2 = colors[0], colors[-1]

    fill = (
        rnd.randint(c1[0], c2[0]),
        rnd.randint(c1[1], c2[1]),
        rnd.randint(c1[2], c2[2]),
    )

    for i, c in enumerate(text):
        if c in en_character:
            txt_img_draw.text(
                (0, sum(char_heights[0:i]) + i * character_spacing),
                c,
                fill=fill,
                font=image_font_en,
            )
            txt_mask_draw.text(
                (0, sum(char_heights[0:i]) + i * character_spacing),
                c,
                fill=(i // (255 * 255), i // 255, i % 255),
                font=image_font_en,
            )
        else:
            txt_img_draw.text(
                (0, sum(char_heights[0:i]) + i * character_spacing),
                c,
                fill=fill,
                font=image_font_ch,
            )
            txt_mask_draw.text(
                (0, sum(char_heights[0:i]) + i * character_spacing),
                c,
                fill=(i // (255 * 255), i // 255, i % 255),
                font=image_font_ch,
            )


    if fit:
        return txt_img.crop(txt_img.getbbox()), txt_mask.crop(txt_img.getbbox())
    else:
        return txt_img, txt_mask


