import json
from cover_engine.layout_engine import CoverLayoutEngine

if __name__ == "__main__":
    with open("example_cover.json") as f:
        metadata = json.load(f)

    engine = CoverLayoutEngine(metadata, base_image_path="sample_cover.png")
    engine.generate_cover("output_cover.pdf")
