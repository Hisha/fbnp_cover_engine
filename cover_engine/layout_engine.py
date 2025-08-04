from PIL import Image, ImageDraw
from text_renderer import render_text
import math


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
                 add_bg=False, line_spacing=8, gradient_bg=True, text_shadow=True):
        """
        Add title, description, and spine text to the cover image with advanced styling options.
        """

        # === Safe Zones ===
        bleed = int(0.125 * self.dpi)
        margin = int(0.25 * self.dpi)
        inner_padding = int(0.1 * self.dpi)

        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        # Back safe zone
        back_safe_x = bleed + margin
        back_safe_y = bleed + margin
        back_safe_width = back_width - (bleed + margin + inner_padding)
        back_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_width, int(back_safe_height * 0.5))

        # Front safe zone
        front_safe_x = back_width + self.spine_width + bleed + margin
        front_safe_y = bleed + margin
        front_safe_width = front_width - (bleed + margin + inner_padding)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_safe_width, int(front_safe_height * 0.3))

        # Spine safe zone
        spine_box_width = int(self.spine_width * 0.9)
        spine_box_height = int(self.final_height * 0.8)

        # === Debug Zones ===
        if self.debug:
            draw = ImageDraw.Draw(self.cover, "RGBA")
            draw.rectangle([front_safe_x, front_safe_y,
                            front_safe_x + front_safe_width, front_safe_y + front_safe_height],
                           outline=(0, 255, 0, 255), width=5)
            draw.rectangle([back_safe_x, back_safe_y,
                            back_safe_x + back_safe_width, back_safe_y + back_safe_height],
                           outline=(0, 0, 255, 255), width=5)
            spine_x = (self.final_width // 2) - (spine_box_width // 2)
            spine_y = (self.final_height // 2) - (spine_box_height // 2)
            draw.rectangle([spine_x, spine_y,
                            spine_x + spine_box_width, spine_y + spine_box_height],
                           outline=(255, 0, 0, 255), width=5)

        # === Optional Gradient Bars ===
        if gradient_bg:
            self._add_gradient_bar((front_safe_x, front_safe_y,
                                    front_safe_x + front_safe_width, front_safe_y + front_box[1]))
            self._add_gradient_bar((back_safe_x, back_safe_y,
                                    back_safe_x + back_safe_width, back_safe_y + back_box[1]))

        # === Render Title (Front Cover) ===
        title_img = self._render_styled_text(
            text=title,
            font_family=font_family,
            font_size=title_font_size,
            color=title_color,
            box_size=front_box,
            align="center", valign="middle",
            bold=True,
            shadow=text_shadow,
            add_bg=add_bg,
            letter_spacing=1
        )
        self.cover.paste(title_img, (front_safe_x, front_safe_y), title_img)

        # === Render Description (Back Cover) ===
        desc_img = self._render_styled_text(
            text=description,
            font_family="DejaVu Serif",  # ✅ More readable for body text
            font_size=desc_font_size,
            color=desc_color,
            box_size=back_box,
            align="left", valign="top",
            spacing=line_spacing,
            shadow=text_shadow,
            add_bg=add_bg
        )
        self.cover.paste(desc_img, (back_safe_x, back_safe_y), desc_img)

        # === Render Spine Text ===
        spine_text = f"{title} • {author}" if author else title
        spine_img = self._render_styled_text(
            text=spine_text,
            font_family=font_family,
            font_size=spine_font_size,
            color=title_color,
            box_size=(spine_box_height, spine_box_width),  # Swapped for rotation
            align="center", valign="middle",
            rotated=True,
            italic=True,
            shadow=text_shadow,
            add_bg=add_bg,
            letter_spacing=2
        )
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

        return self.cover

    def _render_styled_text(self, text, font_family, font_size, color, box_size,
                            align, valign, rotated=False, bold=False, italic=False,
                            spacing=0, letter_spacing=0, shadow=False, add_bg=False):
        img = render_text(
            text=text,
            font_family=font_family,
            font_size=font_size,
            color=color,
            box_size=box_size,
            align=align,
            valign=valign,
            spacing=spacing,
            bold=bold,
            italic=italic,
            add_bg=add_bg,
            gradient_bg=False,  # Gradient handled externally
            letter_spacing=letter_spacing,
            text_shadow=shadow
        )
        if rotated:
            img = img.rotate(90, expand=True)
        return img

    def _add_gradient_bar(self, box, opacity=180):
        x1, y1, x2, y2 = box
        bar = Image.new("RGBA", (x2 - x1, y2 - y1), (255, 255, 255, 0))
        draw = ImageDraw.Draw(bar)
        for i in range(bar.height):
            alpha = int(opacity * (1 - (i / bar.height)))
            draw.line((0, i, bar.width, i), fill=(255, 255, 255, alpha))
        self.cover.paste(bar, (x1, y1), bar)

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
