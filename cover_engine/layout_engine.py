from PIL import Image, ImageDraw
from text_renderer import render_text


class CoverLayoutEngine:
    def __init__(self, cover_image_path, final_width, final_height, spine_width, debug=False):
        self.cover = Image.open(cover_image_path).convert("RGBA")
        self.final_width = final_width
        self.final_height = final_height
        self.spine_width = spine_width
        self.dpi = 300
        self.debug = debug  # ✅ Enables safe zone visualization

    def add_text(self, title, description, author,
                 font_family, title_font_size, desc_font_size, spine_font_size,
                 title_color, desc_color,
                 add_bg=False, line_spacing=8):
        # === Safe Zones with Padding ===
        bleed = int(0.125 * self.dpi)  # 0.125" bleed
        margin = int(0.25 * self.dpi)  # 0.25" margin
        inner_padding = int(0.1 * self.dpi)

        # Split cover into back, spine, front
        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        # Front safe zone (title top 30%)
        front_safe_x = self.spine_width + bleed + margin
        front_safe_y = bleed + margin
        front_safe_width = front_width - (bleed + margin + inner_padding)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_safe_width, int(front_safe_height * 0.3))

        # Back safe zone (description top 50%)
        back_safe_x = bleed + margin
        back_safe_y = bleed + margin
        back_safe_width = back_width - (bleed + margin + inner_padding)
        back_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_width, int(back_safe_height * 0.5))

        # Spine safe zone
        spine_box_width = int(self.spine_width * 0.9)
        spine_box_height = int(self.final_height * 0.8)

        # === DEBUG SAFE ZONES ===
        if self.debug:
            draw = ImageDraw.Draw(self.cover, "RGBA")
            # Front zone in green
            draw.rectangle([front_safe_x, front_safe_y,
                            front_safe_x + front_safe_width, front_safe_y + front_safe_height],
                           outline=(0, 255, 0, 255), width=5)
            # Back zone in blue
            draw.rectangle([back_safe_x, back_safe_y,
                            back_safe_x + back_safe_width, back_safe_y + back_safe_height],
                           outline=(0, 0, 255, 255), width=5)
            # Spine zone in red
            spine_x = (self.final_width // 2) - (spine_box_width // 2)
            spine_y = (self.final_height // 2) - (spine_box_height // 2)
            draw.rectangle([spine_x, spine_y,
                            spine_x + spine_box_width, spine_y + spine_box_height],
                           outline=(255, 0, 0, 255), width=5)

        # === Render Title (Center in front safe zone) ===
        title_img = self._render_scaled_text(title, font_family, title_font_size, title_color,
                                             front_box, "center", "middle", bold=True, add_bg=add_bg)

        title_x = front_safe_x + (front_safe_width - title_img.width) // 2
        title_y = front_safe_y + ((front_safe_height * 0.3) - title_img.height) // 2
        self.cover.paste(title_img, (title_x, int(title_y)), title_img)

        # === Render Description (Align left but center vertically in 50% top block) ===
        desc_img = self._render_scaled_text(description, font_family, desc_font_size, desc_color,
                                            back_box, "left", "top", spacing=line_spacing, add_bg=add_bg)

        desc_x = back_safe_x
        desc_y = back_safe_y + ((back_safe_height * 0.5) - desc_img.height) // 2
        self.cover.paste(desc_img, (desc_x, int(desc_y)), desc_img)

        # === Render Spine ===
        spine_text = f"{title} • {author}" if author else title
        rotated_box = (spine_box_height, spine_box_width)
        spine_img = self._render_scaled_text(spine_text, font_family, spine_font_size, title_color,
                                             rotated_box, "center", "middle", rotated=True, italic=True, add_bg=add_bg)

        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

        return self.cover

    def _render_scaled_text(self, text, font_family, font_size, color, box_size,
                            align, valign, rotated=False, bold=False, italic=False,
                            spacing=0, add_bg=False):
        max_width, max_height = box_size
        img = render_text(text, font_family, font_size, color, box_size, align, valign,
                          spacing=spacing, bold=bold, italic=italic, add_bg=add_bg)

        while (img.width > max_width or img.height > max_height) and font_size > 16:
            font_size -= 2
            img = render_text(text, font_family, font_size, color, box_size, align, valign,
                              spacing=spacing, bold=bold, italic=italic, add_bg=add_bg)

        if rotated:
            img = img.rotate(90, expand=True)
        return img

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
