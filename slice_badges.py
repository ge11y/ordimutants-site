#!/usr/bin/env python3
"""
Slice badge sprite sheets into individual PNG files.
Each sheet is a 5 column x 4 row grid (20 badges per sheet).
"""

from PIL import Image
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BADGES_DIR = os.path.join(SCRIPT_DIR, 'badges')
MEDIA_DIR = '/Users/goobbotv3/.openclaw/media/inbound'

# Sprite sheet configuration
SHEETS = [
    'file_9---1abe3894-f0bb-4253-a1a7-07dc056da26f.jpg',  # badges_sheet_1.png
    # Add second sheet when available
    # 'badges_sheet_2.png',
]

COLS = 5
ROWS = 4

def slice_spritesheet(sheet_path, sheet_num):
    """Slice a sprite sheet into individual badges."""
    print(f"\nProcessing: {sheet_path}")
    
    img = Image.open(sheet_path)
    width, height = img.size
    
    print(f"  Image size: {width}x{height}")
    
    tile_width = width // COLS
    tile_height = height // ROWS
    
    print(f"  Tile size: {tile_width}x{tile_height}")
    
    count = 0
    for row in range(ROWS):
        for col in range(COLS):
            left = col * tile_width
            top = row * tile_height
            right = left + tile_width
            bottom = top + tile_height
            
            # Crop the tile
            tile = img.crop((left, top, right, bottom))
            
            # Trim transparent padding
            bbox = tile.getbbox()
            if bbox:
                tile = tile.crop(bbox)
            
            # Calculate badge number (sheet 1 = 1-20, sheet 2 = 21-40)
            badge_num = (sheet_num - 1) * (COLS * ROWS) + row * COLS + col + 1
            
            # Save as PNG with transparency
            output_path = os.path.join(BADGES_DIR, f'badge_{badge_num:02d}.png')
            tile.save(output_path, 'PNG')
            count += 1
            
            print(f"  Created: badge_{badge_num:02d}.png ({tile.width}x{tile.height})")
    
    return count

def main():
    os.makedirs(BADGES_DIR, exist_ok=True)
    
    total = 0
    for i, sheet_name in enumerate(SHEETS):
        sheet_path = os.path.join(MEDIA_DIR, sheet_name)
        if os.path.exists(sheet_path):
            total += slice_spritesheet(sheet_path, i + 1)
        else:
            print(f"  Warning: Sheet not found: {sheet_path}")
    
    print(f"\n=== Summary ===")
    print(f"Total badges created: {total}")
    
    # List created files
    files = sorted(os.listdir(BADGES_DIR))
    print(f"\nFiles in {BADGES_DIR}:")
    for f in files:
        print(f"  {f}")

if __name__ == '__main__':
    main()
