# FBNP Cover Engine

An automated layout engine to generate **professional KDP-ready coloring book covers** with:
- Dynamic spine calculation
- Title and description placement
- High-resolution PDF export

## Features
✅ Full-bleed KDP-compliant sizing  
✅ Intelligent text layout (Pango/Cairo)  
✅ Automated font scaling and color contrast  
✅ Spine text rendering  
✅ Ready for automation in n8n workflows  

## Requirements.txt
```bash
# Core image processing
Pillow==10.4.0

# PDF generation
reportlab==4.2.2

# Advanced vector graphics + text rendering
pycairo==1.25.1

# Layout calculations and typography
fonttools==4.53.0

# Optional: if we add SVG overlays later
cairosvg==2.7.1

# For CLI interface (optional but recommended)
click==8.1.7



## Usage
```bash
python examples/run_example.py
