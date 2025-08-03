import os
from PIL import Image
from .image_utils import resize_with_aspect_ratio, add_bleed
from .text_renderer import render_text, render_rotated_text
from .color_utils import get_contrast_color
from .config import DPI, TRIM_WIDTH_INCH, TRIM_HEIGHT_INCH, BLEED_INCH

class CoverLayoutEngine:
    def __init__(self, metadata, base_image_path):
        """
        metadata: dict with keys:
            - title
            - description
            - author
            - page_count
        base_image_path: path to base cover art
        """
        self.metadata = metadata
        self.base_image_path = base_image_path

    def calculate_dimensions(self):
        spine_in = round(self.metadata["page_count"] / 444, 3)
        width_in = (TRIM_WIDTH_INCH * 2) + spine_in + (BLEED_INCH * 2)
        height_in = TRIM_HEIGHT_INCH + (BLEED_INCH * 2)
        return int(width_in * DPI), int(height_in * DPI), int(spine_in * DPI)

    def create_canvas(self):
        width_px, height_px, spine_px = self.calculate_dimensions()
        img = Image.open(self.base_image_path)
        img = resize_with_aspect_ratio(img, width_px, height_px)
        canvas = Image.new("RGB", (width_px, height_px), (255, 255, 255))
        canvas.paste(img, ((width_px - img.width) // 2, (height_px - img.height) // 2))
        return canvas, spine_px

    def add_text(self, canvas, spine_px):
        # TODO: Render title, description, spine text with Pango/Cairo
        pass

    def export(self, canvas, output_path, format="PDF"):
        if format.upper() == "PDF":
            canvas.save(output_path, "PDF", resolution=DPI)
        else:
            canvas.save(output_path, "PNG")

    def generate_cover(self, output_path):
        canvas, spine_px = self.create_canvas()
        self.add_text(canvas, spine_px)
        self.export(canvas, output_path)
