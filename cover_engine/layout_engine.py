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

    def add_text(
        self,
        title,
        description,
        author,
        font_family,
        title_font_size,
        desc_font_size,
        spine_font_size,
        title_color,
        desc_color,
        add_bg=True,
        line_spacing=8,
        gradient_bg=True,
        text_shadow=True,
        letter_spacing=1.2,
        body_font="Merriweather",
        blur_bg=True,
    ):
        # === KDP SAFE ZONES ===
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

        # Front (right)
        front_safe_x = back_width + self.spine_width + bleed + margin
        front_safe_y = bleed + margin
        front_safe_width = front_width - (bleed + margin + inner_padding)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)

        # Sub-areas
        title_area_h = int(front_safe_height * 0.36)
        subtitle_gap = int(0.04 * self.dpi)
        subtitle_area_h = int(front_safe_height * 0.16)
        desc_area_h = int(back_safe_height * 0.52)

        front_title_box = (front_safe_width, title_area_h)
        front_subtitle_box = (front_safe_width, subtitle_area_h)
        back_desc_box = (back_safe_width := back_safe_width, desc_area_h)  # noqa: F841

        # Spine
        spine_box_w = int(self.spine_width * 0.9)
        spine_box_h = int(self.final_height * 0.8)

        # === Debug Guides ===
        if self.debug:
            d = ImageDraw.Draw(self.cover, "RGBA")
            # full safe areas
            d.rectangle([front_safe_x, front_safe_y,
                         front_safe_x + front_safe_width, front_safe_y + front_safe_height],
                        outline=(0, 255, 0, 255), width=4)
            d.rectangle([back_safe_x, back_safe_y,
                         back_safe_x + back_safe_width, back_safe_y + back_safe_height],
                        outline=(0, 0, 255, 255), width=4)
            # spine
            spine_cx = self.final_width // 2
            d.rectangle([spine_cx - spine_box_w // 2, (self.final_height - spine_box_h) // 2,
                         spine_cx + spine_box_w // 2, (self.final_height + spine_box_h) // 2],
                        outline=(255, 0, 0, 255), width=4)

        # === Background Enhancements ===
        if gradient_bg:
            self._add_gradient_bar((front_safe_x, front_safe_y,
                                    front_safe_x + front_safe_width, front_safe_y + title_area_h))
            self._add_gradient_bar((back_safe_x, back_safe_y,
                                    back_safe_x + back_safe_width, back_safe_y + desc_area_h))
        if blur_bg:
            self._blur_area(front_safe_x, front_safe_y, front_safe_width, title_area_h)
            self._blur_area(back_safe_x, back_safe_y, back_safe_width, desc_area_h)

        # === Accent Line Color from Art ===
        accent_color = self._extract_dominant_color()

        # === Split Title / Subtitle ===
        main_title, subtitle = self._split_title_subtitle(title)

        # === Render Title (Front) ===
        title_img = render_text(
            main_title,
            font_family,
            title_font_size,
            title_color,
            front_title_box,
            align="center",
            valign="middle",
            bold=True,
            add_bg=True,            # semi panel
            gradient_bg=False,
            letter_spacing=letter_spacing,
            text_shadow=text_shadow,
            rounded_bg=True,
            padding_px=18,
        )
        self.cover.paste(title_img, (front_safe_x, front_safe_y), title_img)

        # Decorative rule under title
        self._draw_line(
            x1=front_safe_x + 60,
            y=front_safe_y + title_img.height + 18,
            x2=front_safe_x + front_title_box[0] - 60,
            color=accent_color,
            thickness=5,
        )

        # === Render Subtitle (optional) ===
        if subtitle.strip():
            sub_img = render_text(
                subtitle,
                font_family,
                max(12, int(title_font_size * 0.43)),
                title_color,
                front_subtitle_box,
                align="center",
                valign="top",
                bold=False,
                add_bg=False,
                gradient_bg=False,
                letter_spacing=letter_spacing * 0.8,
                text_shadow=text_shadow,
                rounded_bg=False,
                padding_px=8,
            )
            sub_y = front_safe_y + title_img.height + 34  # below rule
            self.cover.paste(sub_img, (front_safe_x, sub_y), sub_img)

        # === Render Description (Back) — justified ===
        desc_img = render_text(
            description,
            body_font,
            desc_font_size,
            desc_color,
            (back_safe_width, desc_area_h),
            align="left",
            valign="top",
            spacing=line_spacing,
            add_bg=True,
            gradient_bg=False,
            justify=True,
            text_shadow=text_shadow,
            padding_px=16,
        )
        self.cover.paste(desc_img, (back_safe_x, back_safe_y), desc_img)

        # === Render Spine ===
        spine_text = (f"{main_title} • {author}" if author else main_title)
        spine_img = render_text(
            spine_text,
            font_family,
            spine_font_size,
            title_color,
            (spine_box_h, spine_box_w),  # swapped for rotation
            align="center",
            valign="middle",
            italic=False,
            rotated=True,
            small_caps=True,
            letter_spacing=1.6,
            text_shadow=text_shadow,
            add_bg=False,
        )
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

    # ===== Helpers =====
    def _add_gradient_bar(self, box, opacity=175):
        x1, y1, x2, y2 = box
        bar = Image.new("RGBA", (x2 - x1, y2 - y1), (255, 255, 255, 0))
        draw = ImageDraw.Draw(bar)
        h = bar.height
        for i in range(h):
            alpha = int(opacity * (1 - (i / max(1, h))))
            draw.line((0, i, bar.width, i), fill=(255, 255, 255, alpha))
        self.cover.paste(bar, (x1, y1), bar)

    def _blur_area(self, x, y, w, h):
        region = self.cover.crop((x, y, x + w, y + h))
        self.cover.paste(region.filter(ImageFilter.GaussianBlur(12)), (x, y))

    def _extract_dominant_color(self):
        small = self.cover.resize((120, 120))
        pixels = list(small.getdata())
        # Count colors, pick the darkest “common” to avoid white
        common = Counter(pixels).most_common(40)
        for color, _ in common:
            if sum(color[:3]) < 680:  # push away near-white
                return color
        return (45, 45, 45)

    def _split_title_subtitle(self, text: str):
        # Try typical splitters, keep the first as title, the rest as subtitle
        for sep in [" — ", " – ", " - ", ":", "|", "—", "–", "-"]:
            if sep in text:
                parts = [p.strip() for p in text.split(sep, 1)]
                if len(parts) == 2:
                    return parts[0], parts[1]
        return text, ""  # no subtitle

    def _draw_line(self, x1, y, x2, color, thickness=4):
        d = ImageDraw.Draw(self.cover)
        d.line((x1, y, x2, y), fill=color, width=thickness)

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
