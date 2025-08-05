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
                 letter_spacing=0, body_font="Merriweather", blur_bg=False):

        # === SAFE ZONES ===
        bleed = int(0.125 * self.dpi)
        margin = int(0.25 * self.dpi)
        inner_padding = int(0.1 * self.dpi)

        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        back_safe_x = bleed + margin
        back_safe_y = bleed + margin
        back_safe_width = back_width - (bleed + margin + inner_padding)
        back_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_width, int(back_safe_height * 0.5))

        front_safe_x = back_width + self.spine_width + bleed + margin
        front_safe_y = bleed + margin
        front_safe_width = front_width - (bleed + margin + inner_padding)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_safe_width, int(front_safe_height * 0.3))

        spine_box_width = int(self.spine_width * 0.9)
        spine_box_height = int(self.final_height * 0.8)

        # === DEBUG SAFE ZONES ===
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

        # === BACKGROUND ENHANCEMENTS ===
        if gradient_bg:
            self._add_gradient_bar((front_safe_x, front_safe_y,
                                    front_safe_x + front_safe_width, front_safe_y + front_box[1]))
            self._add_gradient_bar((back_safe_x, back_safe_y,
                                    back_safe_x + back_safe_width, back_safe_y + back_box[1]))
        if blur_bg:
            self._blur_area(front_safe_x, front_safe_y, front_safe_width, front_box[1])
            self._blur_area(back_safe_x, back_safe_y, back_safe_width, back_box[1])

        # === ACCENT COLOR FOR DECOR ===
        accent_color = self._extract_dominant_color()

        # === TITLE HANDLING ===
        split_title = self._split_title(title)
        title_text = "\n".join(split_title)

        # === RENDER TITLE ===
        title_img = render_text(title_text, font_family, title_font_size, title_color,
                                front_box, align="center", valign="middle",
                                bold=True, add_bg=add_bg, letter_spacing=letter_spacing,
                                text_shadow=text_shadow)
        self.cover.paste(title_img, (front_safe_x, front_safe_y), title_img)

        # === DECORATIVE LINE BELOW TITLE ===
        self._draw_line(front_safe_x + 50, front_safe_y + title_img.height + 20,
                        front_safe_x + front_box[0] - 50, color=accent_color, thickness=6)

        # === RENDER DESCRIPTION ===
        desc_img = render_text(description, body_font, desc_font_size, desc_color,
                               back_box, align="left", valign="top",
                               spacing=line_spacing, add_bg=add_bg, text_shadow=text_shadow)
        self.cover.paste(desc_img, (back_safe_x, back_safe_y), desc_img)

        # === RENDER SPINE ===
        spine_text = (f"{title.upper()} • {author.upper()}" if author else title.upper())
        spine_img = render_text(spine_text, font_family, spine_font_size, title_color,
                                (spine_box_height, spine_box_width),
                                align="center", valign="middle", italic=True,
                                rotated=True, letter_spacing=2, text_shadow=text_shadow)
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

    # === UTILITY: Gradient Overlay ===
    def _add_gradient_bar(self, box, opacity=180):
        x1, y1, x2, y2 = box
        bar = Image.new("RGBA", (x2 - x1, y2 - y1), (255, 255, 255, 0))
        draw = ImageDraw.Draw(bar)
        for i in range(bar.height):
            alpha = int(opacity * (1 - (i / bar.height)))
            draw.line((0, i, bar.width, i), fill=(255, 255, 255, alpha))
        self.cover.paste(bar, (x1, y1), bar)

    # === UTILITY: Blur Background Area ===
    def _blur_area(self, x, y, width, height):
        region = self.cover.crop((x, y, x + width, y + height))
        blurred = region.filter(ImageFilter.GaussianBlur(15))
        self.cover.paste(blurred, (x, y))

    # === UTILITY: Extract Accent Color ===
    def _extract_dominant_color(self):
        small = self.cover.resize((150, 150))
        pixels = list(small.getdata())
        most_common = Counter(pixels).most_common(10)
        for color, _ in most_common:
            if sum(color[:3]) < 700:  # Filter out bright/white
                return color
        return (50, 50, 50)

    # === UTILITY: Split Title ===
    def _split_title(self, title):
        words = title.split()
        if len(words) <= 4:
            return [title]
        midpoint = len(words) // 2
        return [" ".join(words[:midpoint]), " ".join(words[midpoint:])]

    # === UTILITY: Decorative Line ===
    def _draw_line(self, x1, y, x2, color, thickness=4):
        draw = ImageDraw.Draw(self.cover)
        draw.line((x1, y, x2, y), fill=color, width=thickness)

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
