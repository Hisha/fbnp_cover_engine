from PIL import Image, ImageDraw, ImageFilter
from text_renderer import render_text
from collections import Counter

class CoverLayoutEngine:
    def __init__(self, cover_image_path, final_width, final_height, spine_width, debug=False):
        self.cover = Image.open(cover_image_path).convert("RGBA")
        self.final_width = final_width
        self.final_height = final_height
        self.spine_width = spine_width
        self.dpi = 300
        self.debug = debug

    def add_text(self, title, description, author,
                 font_family, title_font_size, desc_font_size, spine_font_size,
                 title_color, desc_color,
                 add_bg=False, line_spacing=8, gradient_bg=True, text_shadow=True,
                 letter_spacing=0, body_font="Merriweather", blur_bg=False,
                 # pro extras
                 pro_title_case="title", pro_underline=False, pro_frame_border=False,
                 pro_gradient_opacity=180, pro_blur_radius=8):

        # === SAFE ZONES ===
        bleed = int(0.125 * self.dpi)
        margin = int(0.25 * self.dpi)
        inner_padding = int(0.10 * self.dpi)

        back_width  = (self.final_width - self.spine_width) // 2
        front_width = back_width

        back_safe_x = bleed + margin
        back_safe_y = bleed + margin
        back_safe_w = back_width  - (bleed + margin + inner_padding)
        back_safe_h = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_w, int(back_safe_h * 0.50))

        front_safe_x = back_width + self.spine_width + bleed + margin
        front_safe_y = bleed + margin
        front_safe_w = front_width - (bleed + margin + inner_padding)
        front_safe_h = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_safe_w, int(front_safe_h * 0.32))

        spine_box_w = int(self.spine_width * 0.9)
        spine_box_h = int(self.final_height * 0.8)

        if self.debug:
            d = ImageDraw.Draw(self.cover, "RGBA")
            d.rectangle([front_safe_x, front_safe_y,
                         front_safe_x + front_safe_w, front_safe_y + front_safe_h],
                        outline=(0, 255, 0, 220), width=4)
            d.rectangle([back_safe_x, back_safe_y,
                         back_safe_x + back_safe_w, back_safe_y + back_safe_h],
                        outline=(0, 0, 255, 220), width=4)
            spine_x = (self.final_width // 2) - (spine_box_w // 2)
            spine_y = (self.final_height // 2) - (spine_box_h // 2)
            d.rectangle([spine_x, spine_y, spine_x + spine_box_w, spine_y + spine_box_h],
                        outline=(255, 0, 0, 220), width=4)

        # Optional frame inside bleed
        if pro_frame_border:
            self._draw_frame_inside_bleed(bleed, margin, color=(0, 0, 0, 50), width=2)

        # Background treatments behind text
        if gradient_bg:
            self._add_gradient_bar((front_safe_x, front_safe_y,
                                    front_safe_x + front_safe_w, front_safe_y + front_box[1]),
                                   opacity=pro_gradient_opacity)
            self._add_gradient_bar((back_safe_x, back_safe_y,
                                    back_safe_x + back_safe_w, back_safe_y + back_box[1]),
                                   opacity=pro_gradient_opacity)
        if blur_bg:
            self._blur_area(front_safe_x, front_safe_y, front_safe_w, front_box[1], radius=pro_blur_radius)
            self._blur_area(back_safe_x, back_safe_y, back_safe_w, back_box[1], radius=pro_blur_radius)

        # Accent color from artwork
        accent = self._extract_dominant_color()

        # Title casing profile
        title_text = self._apply_title_case(title, pro_title_case)
        # If long, split into two lines (rough, but effective)
        title_text = "\n".join(self._split_title(title_text))

        # Render Title
        title_img = render_text(
            title_text, font_family, title_font_size, title_color,
            front_box, align="center", valign="middle",
            bold=True, add_bg=False, letter_spacing=letter_spacing,
            text_shadow=text_shadow
        )
        self.cover.paste(title_img, (front_safe_x, front_safe_y), title_img)

        # Optional underline / rule
        if pro_underline:
            y_rule = front_safe_y + title_img.height + int(0.04 * self.dpi)
            self._draw_line(front_safe_x + 40, y_rule, front_safe_x + front_box[0] - 40,
                            color=accent, thickness=5, alpha=210)

        # Render Description
        desc_img = render_text(
            description, body_font, desc_font_size, desc_color,
            back_box, align="left", valign="top",
            spacing= line_spacing, add_bg=False,
            text_shadow=text_shadow
        )
        self.cover.paste(desc_img, (back_safe_x, back_safe_y), desc_img)

        # Render Spine
        spine_text = (f"{title} • {author}" if author else title)
        spine_img = render_text(
            spine_text, font_family, spine_font_size, title_color,
            (spine_box_h, spine_box_w), align="center", valign="middle",
            italic=True, rotated=True, letter_spacing=1.2, text_shadow=text_shadow, small_caps=False
        )
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

    # ---- helpers ----

    def _add_gradient_bar(self, box, opacity=180):
        x1, y1, x2, y2 = box
        w, h = x2 - x1, y2 - y1
        bar = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        draw = ImageDraw.Draw(bar)
        for i in range(h):
            alpha = int(opacity * (1 - (i / max(h, 1))))
            draw.line((0, i, w, i), fill=(255, 255, 255, alpha))
        self.cover.paste(bar, (x1, y1), bar)

    def _blur_area(self, x, y, w, h, radius=8):
        region = self.cover.crop((x, y, x + w, y + h))
        blurred = region.filter(ImageFilter.GaussianBlur(radius))
        # soft rounded mask
        mask = Image.new("L", (w, h), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.rounded_rectangle((0, 0, w, h), radius=int(0.06 * h), fill=255)
        self.cover.paste(blurred, (x, y), mask)

    def _draw_line(self, x1, y, x2, color, thickness=4, alpha=255):
        draw = ImageDraw.Draw(self.cover)
        rgba = (color[0], color[1], color[2], alpha) if len(color) == 3 else color
        draw.line((x1, y, x2, y), fill=rgba, width=thickness)

    def _draw_frame_inside_bleed(self, bleed, margin, color=(0,0,0,60), width=2):
        inset = bleed + margin
        x1, y1 = inset, inset
        x2, y2 = self.final_width - inset, self.final_height - inset
        d = ImageDraw.Draw(self.cover)
        d.rectangle([x1, y1, x2, y2], outline=color, width=width)

    def _extract_dominant_color(self):
        small = self.cover.resize((140, 140))
        pixels = list(small.getdata())
        most_common = Counter(pixels).most_common(30)
        for color, _ in most_common:
            # prefer saturated / mid-tone colors over near-white
            if sum(color[:3]) < 700 and max(color[:3]) - min(color[:3]) > 30:
                return color[:3]
        return (60, 60, 60)

    def _split_title(self, t):
        words = t.split()
        if len(words) <= 4:
            return [t]
        # try to split near the middle at a word boundary
        mid = len(words) // 2
        # bias to break before prepositions/conjunctions
        pivots = {"for", "and", "of", "the", "to", "with", "in"}
        for i in range(max(2, mid-2), min(len(words)-2, mid+2)):
            if words[i].lower() not in pivots:
                mid = i
                break
        return [" ".join(words[:mid]), " ".join(words[mid:])]

    def _apply_title_case(self, t, mode):
        if mode == "upper":
            return t.upper()
        if mode == "sentence":
            return t[:1].upper() + t[1:]
        if mode == "title":
            # lightweight title-case
            lowers = {"a","an","and","the","for","of","in","on","to","with","by","or"}
            words = t.split()
            out = []
            for i,w in enumerate(words):
                wl = w.lower()
                if i != 0 and wl in lowers:
                    out.append(wl)
                else:
                    out.append(w[:1].upper() + w[1:])
            return " ".join(out)
        return t  # as_is

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
