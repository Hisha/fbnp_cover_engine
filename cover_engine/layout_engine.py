from PIL import Image, ImageDraw, ImageFilter, ImageStat
from text_renderer import render_text
from collections import Counter
import math


class CoverLayoutEngine:
    def __init__(self, cover_image_path, final_width, final_height, spine_width, debug=False):
        self.cover = Image.open(cover_image_path).convert("RGBA")
        self.final_width = final_width
        self.final_height = final_height
        self.spine_width = spine_width
        self.dpi = 300
        self.debug = debug

    def add_text(self, title, subtitle, description, author,
                 font_family, title_font_size, desc_font_size, spine_font_size,
                 title_color, desc_color,
                 add_bg=False, line_spacing=8, gradient_bg=True, text_shadow=True,
                 letter_spacing=0, body_font="Merriweather", blur_bg=False,
                 smart_position=True, auto_contrast_bg=True):

        # === SAFE ZONES ===
        bleed = int(0.125 * self.dpi)
        margin = int(0.25 * self.dpi)
        inner_padding = int(0.1 * self.dpi)

        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        # Back (left)
        back_safe_x = bleed + margin
        back_safe_y = bleed + margin
        back_safe_width = back_width - (bleed + margin + inner_padding)
        back_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_width, int(back_safe_height * 0.55))  # a bit more space for body

        # Front (right)
        front_safe_x = back_width + self.spine_width + bleed + margin
        front_safe_y = bleed + margin
        front_safe_width = front_width - (bleed + margin + inner_padding)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        # Title + subtitle column (top ~35%)
        title_area_height = int(front_safe_height * 0.35)

        # Spine
        spine_box_width = int(self.spine_width * 0.9)
        spine_box_height = int(self.final_height * 0.8)

        # === DEBUG SAFE ZONES ===
        if self.debug:
            draw = ImageDraw.Draw(self.cover, "RGBA")
            # front
            draw.rectangle([front_safe_x, front_safe_y,
                            front_safe_x + front_safe_width, front_safe_y + front_safe_height],
                           outline=(0, 255, 0, 255), width=4)
            # back
            draw.rectangle([back_safe_x, back_safe_y,
                            back_safe_x + back_safe_width, back_safe_y + back_safe_height],
                           outline=(0, 0, 255, 255), width=4)
            # spine
            spine_x = (self.final_width // 2) - (spine_box_width // 2)
            spine_y = (self.final_height // 2) - (spine_box_height // 2)
            draw.rectangle([spine_x, spine_y, spine_x + spine_box_width, spine_y + spine_box_height],
                           outline=(255, 0, 0, 255), width=4)

        # === BACKGROUND ENHANCEMENTS ===
        if gradient_bg:
            self._add_gradient_bar((front_safe_x, front_safe_y,
                                    front_safe_x + front_safe_width, front_safe_y + title_area_height))
            self._add_gradient_bar((back_safe_x, back_safe_y,
                                    back_safe_x + back_safe_width, back_safe_y + back_box[1]))
        if blur_bg:
            self._blur_area(front_safe_x, front_safe_y, front_safe_width, title_area_height)
            self._blur_area(back_safe_x, back_safe_y, back_safe_width, back_box[1])

        # === ACCENT COLOR FOR DECOR ===
        accent_color = self._extract_dominant_color()

        # === FRONT: TITLE + SUBTITLE ===
        title_block_h = title_area_height
        # Smart placement (only vertical offset inside the title zone)
        title_y_offset = 0
        if smart_position:
            title_y_offset = self._least_busy_offset(front_safe_x, front_safe_y,
                                                     front_safe_width, title_block_h,
                                                     scan_rows=6)

        title_box = (front_safe_width, int(title_block_h * (0.62 if subtitle else 0.9)))
        sub_box = (front_safe_width, title_block_h - title_box[1])

        # Title image
        title_img = render_text(
            text=title,
            font_family=font_family,
            font_size=title_font_size,
            color=title_color,
            box_size=title_box,
            align="center",
            valign="middle",
            bold=True,
            add_bg=False,
            letter_spacing=letter_spacing,
            text_shadow=text_shadow
        )

        # Subtitle (optional)
        subtitle_gap = int(self.dpi * 0.05)  # ~0.05"
        sub_img = None
        if subtitle:
            sub_img = render_text(
                text=subtitle,
                font_family=font_family,
                font_size=max(int(title_font_size * 0.6), 22),
                color=title_color,
                box_size=sub_box,
                align="center",
                valign="middle",
                bold=False,
                add_bg=False,
                letter_spacing=max(letter_spacing - 0.2, 0),
                text_shadow=text_shadow
            )

        # Auto-contrast rounded bg (behind the entire title band)
        if auto_contrast_bg:
            self._ensure_contrast_bg(front_safe_x, front_safe_y + title_y_offset,
                                     front_safe_width, title_block_h, title_color, radius=18, alpha=180)

        # Paste title (+subtitle)
        cur_y = front_safe_y + title_y_offset
        self.cover.paste(title_img, (front_safe_x, cur_y), title_img)
        if sub_img:
            cur_y += title_img.height + subtitle_gap
            self.cover.paste(sub_img, (front_safe_x, cur_y), sub_img)

        # Decorative line under the title area
        line_y = front_safe_y + title_y_offset + title_block_h + int(self.dpi * 0.02)
        self._draw_line(front_safe_x + 50, line_y,
                        front_safe_x + front_safe_width - 50,
                        color=accent_color, thickness=6)

        # === BACK: DESCRIPTION ===
        # Smart placement inside the back description zone (top half)
        back_y_offset = 0
        if smart_position:
            back_y_offset = self._least_busy_offset(back_safe_x, back_safe_y,
                                                    back_safe_width, back_box[1],
                                                    scan_rows=6)

        if auto_contrast_bg:
            self._ensure_contrast_bg(back_safe_x, back_safe_y + back_y_offset,
                                     back_safe_width, back_box[1], desc_color, radius=14, alpha=170)

        desc_img = render_text(
            text=description,
            font_family=body_font,
            font_size=desc_font_size,
            color=desc_color,
            box_size=back_box,
            align="left",
            valign="top",
            spacing=line_spacing,
            add_bg=False,
            text_shadow=text_shadow
        )
        self.cover.paste(desc_img, (back_safe_x, back_safe_y + back_y_offset), desc_img)

        # === SPINE ===
        spine_text = (f"{title} • {author}" if author else title)
        spine_img = render_text(
            text=spine_text,
            font_family=font_family,
            font_size=spine_font_size,
            color=title_color,
            box_size=(spine_box_height, spine_box_width),  # swapped for rotate
            align="center",
            valign="middle",
            italic=True,
            rotated=True,
            letter_spacing=1.2,
            text_shadow=text_shadow,
            small_caps=True
        )
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

    # ---------- Helpers ----------

    def _least_busy_offset(self, x, y, w, h, scan_rows=6):
        """Return a vertical offset inside [y, y+h] with minimum edge density."""
        region = self.cover.crop((x, y, x + w, y + h)).convert("L").filter(ImageFilter.FIND_EDGES)
        strip_h = max(h // scan_rows, 8)
        best_offset = 0
        best_score = float("inf")
        for off in range(0, h - strip_h + 1, max(strip_h // 2, 8)):
            strip = region.crop((0, off, w, off + strip_h))
            score = ImageStat.Stat(strip).mean[0]  # lower = smoother
            if score < best_score:
                best_score = score
                best_offset = off
        return best_offset

    def _srgb_to_linear(self, c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    def _relative_luminance(self, rgb):
        r, g, b = rgb[:3]
        R = self._srgb_to_linear(r)
        G = self._srgb_to_linear(g)
        B = self._srgb_to_linear(b)
        return 0.2126 * R + 0.7152 * G + 0.0722 * B

    def _contrast_ratio(self, fg_rgb, bg_rgb):
        L1 = self._relative_luminance(fg_rgb)
        L2 = self._relative_luminance(bg_rgb)
        L_light = max(L1, L2)
        L_dark = min(L1, L2)
        return (L_light + 0.05) / (L_dark + 0.05)

    def _ensure_contrast_bg(self, x, y, w, h, text_rgb, radius=16, alpha=170, min_ratio=4.5):
        """If contrast is low, draw a rounded translucent box behind the area."""
        sample = self.cover.crop((x, y, x + w, y + h)).resize((32, 32))
        avg = tuple(int(ImageStat.Stat(sample).mean[i]) for i in range(3))
        if self._contrast_ratio(text_rgb, avg) >= min_ratio:
            return  # good enough

        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        self._rounded_rect(draw, (0, 0, w, h), radius, fill=(255, 255, 255, alpha))
        self.cover.paste(overlay, (x, y), overlay)

    def _rounded_rect(self, draw, box, radius, fill):
        x1, y1, x2, y2 = box
        r = radius
        draw.rounded_rectangle([x1, y1, x2, y2], r, fill=fill)

    # === Overlays ===
    def _add_gradient_bar(self, box, opacity=180):
        x1, y1, x2, y2 = box
        bar = Image.new("RGBA", (x2 - x1, y2 - y1), (255, 255, 255, 0))
        draw = ImageDraw.Draw(bar)
        h = y2 - y1
        for i in range(h):
            a = int(opacity * (1 - (i / max(h, 1))))
            draw.line((0, i, x2 - x1, i), fill=(255, 255, 255, a))
        self.cover.paste(bar, (x1, y1), bar)

    def _blur_area(self, x, y, width, height):
        region = self.cover.crop((x, y, x + width, y + height))
        blurred = region.filter(ImageFilter.GaussianBlur(14))
        self.cover.paste(blurred, (x, y))

    def _extract_dominant_color(self):
        small = self.cover.resize((160, 160))
        pixels = list(small.getdata())
        common = Counter(pixels).most_common(20)
        for color, _ in common:
            if sum(color[:3]) < 700:  # skip near-white
                return color
        return (60, 60, 60)

    def _draw_line(self, x1, y, x2, color, thickness=4):
        draw = ImageDraw.Draw(self.cover)
        draw.line((x1, y, x2, y), fill=color, width=thickness)

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
