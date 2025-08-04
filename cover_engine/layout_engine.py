from PIL import Image
from text_renderer import render_text, render_rotated_text

class CoverLayoutEngine:
    def __init__(self, cover_image_path, final_width, final_height, spine_width):
        self.cover = Image.open(cover_image_path).convert("RGBA")
        self.final_width = final_width
        self.final_height = final_height
        self.spine_width = spine_width
        self.dpi = 300

    def add_text(self, title, description, author,
                 font_family, title_font_size, desc_font_size, spine_font_size,
                 title_color, desc_color,
                 add_bg=False, line_spacing=8):
        # === Safe Zones with Padding ===
        bleed = int(0.125 * self.dpi)
        margin = int(0.25 * self.dpi)
        inner_padding = int(0.1 * self.dpi)

        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        front_box = (front_width - (bleed + margin + inner_padding),
                     int((self.final_height - (2 * bleed) - (2 * margin)) * 0.3))
        back_box = (back_width - (bleed + margin + inner_padding),
                    int((self.final_height - (2 * bleed) - (2 * margin)) * 0.5))
        spine_box = (int(self.spine_width * 0.9), int(self.final_height * 0.8))

        # === Render Title ===
        title_img = self._render_scaled_text(title, font_family, title_font_size, title_color,
                                             front_box, "center", "middle", bold=True, add_bg=add_bg)
        self.cover.paste(title_img, (self.spine_width + bleed + margin, bleed + margin), title_img)

        # === Render Description ===
        desc_img = self._render_scaled_text(description, font_family, desc_font_size, desc_color,
                                            back_box, "left", "top", spacing=line_spacing, add_bg=add_bg)
        self.cover.paste(desc_img, (bleed + margin, bleed + margin), desc_img)

        # === Render Spine ===
        spine_text = f"{title} • {author}" if author else title
        spine_img = self._render_scaled_text(spine_text, font_family, spine_font_size, title_color,
                                             spine_box, "center", "middle", rotated=True, italic=True, add_bg=add_bg)
        self.cover.paste(spine_img, ((self.final_width // 2) - (spine_img.width // 2),
                                     (self.final_height // 2) - (spine_img.height // 2)), spine_img)
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
