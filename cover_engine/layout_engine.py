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
        # === KDP Safe Zones ===
        bleed = int(0.125 * self.dpi)  # 0.125" bleed
        margin = int(0.25 * self.dpi)  # 0.25" margin
        inner_padding = int(0.1 * self.dpi)

        # === Calculate Panels ===
        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        # === FRONT SAFE ZONE (Right Side) ===
        front_safe_x = self.spine_width + back_width + bleed + margin
        front_safe_y = bleed + margin
        front_safe_width = front_width - (bleed + margin + inner_padding)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_safe_width, int(front_safe_height * 0.3))  # top 30% for title

        # === BACK SAFE ZONE (Left Side) ===
        back_safe_x = bleed + margin
        back_safe_y = bleed + margin
        back_safe_width = back_width - (bleed + margin + inner_padding)
        back_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_width, int(back_safe_height * 0.5))  # top 50% for description

        # === SPINE SAFE ZONE (Middle) ===
        spine_box = (int(self.spine_width * 0.9), int(self.final_height * 0.8))
        spine_x = back_width + (self.spine_width // 2) - (spine_box[0] // 2)
        spine_y = (self.final_height // 2) - (spine_box[1] // 2)

        # === DEBUG OUTLINES ===
        if self.debug:
            draw = ImageDraw.Draw(self.cover, "RGBA")
            # Front zone (Green)
            draw.rectangle([front_safe_x, front_safe_y,
                            front_safe_x + front_safe_width, front_safe_y + front_safe_height],
                           outline=(0, 255, 0, 255), width=5)
            # Back zone (Blue)
            draw.rectangle([back_safe_x, back_safe_y,
                            back_safe_x + back_safe_width, back_safe_y + back_safe_height],
                           outline=(0, 0, 255, 255), width=5)
            # Spine zone (Red)
            draw.rectangle([spine_x, spine_y,
                            spine_x + spine_box[0], spine_y + spine_box[1]],
                           outline=(255, 0, 0, 255), width=5)

        # === Render Title on FRONT ===
        title_img = self._render_scaled_text(title, font_family, title_font_size, title_color,
                                             front_box, "center", "middle", bold=True, add_bg=add_bg)
        self.cover.paste(title_img, (front_safe_x, front_safe_y), title_img)

        # === Render Description on BACK ===
        desc_img = self._render_scaled_text(description, font_family, desc_font_size, desc_color,
                                            back_box, "left", "top", spacing=line_spacing, add_bg=add_bg)
        self.cover.paste(desc_img, (back_safe_x, back_safe_y), desc_img)

        # === Render Spine ===
        spine_text = f"{title} • {author}" if author else title
        spine_img = self._render_scaled_text(spine_text, font_family, spine_font_size, title_color,
                                             spine_box, "center", "middle", rotated=True, italic=True, add_bg=add_bg)
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
