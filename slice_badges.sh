#!/bin/bash
# Slice badge sprite sheets into tightly cropped individual PNG files

BADGES_DIR="/Users/goobbotv3/.openclaw/workspace-cody/ordimutants-v2/badges"
MEDIA_DIR="/Users/goobbotv3/.openclaw/media/inbound"

mkdir -p "$BADGES_DIR"

# Sheet 1 - copy to temp location with proper permissions
SHEET1_TMP="/tmp/badges_sheet_1.jpg"
cp "$MEDIA_DIR/file_9---1abe3894-f0bb-4253-a1a7-07dc056da26f.jpg" "$SHEET1_TMP" 2>/dev/null || cp "/Users/goobbotv3/.openclaw/media/inbound/file_9---1abe3894-f0bb-4253-a1a7-07dc056da26f.jpg" "$SHEET1_TMP"

if [ -f "$SHEET1_TMP" ]; then
    echo "Processing sheet 1..."
    
    # Get dimensions
    WIDTH=$(identify -format "%w" "$SHEET1_TMP")
    HEIGHT=$(identify -format "%h" "$SHEET1_TMP")
    
    echo "  Size: ${WIDTH}x${HEIGHT}"
    
    # Calculate tile size (5 cols x 4 rows = 20 tiles)
    TILE_W=$((WIDTH / 5))
    TILE_H=$((HEIGHT / 4))
    
    echo "  Tile size: ${TILE_W}x${TILE_H}"
    
    # Slice each tile with -trim to remove transparent padding
    for row in 0 1 2 3; do
        for col in 0 1 2 3 4; do
            NUM=$((row * 5 + col + 1))
            X=$((col * TILE_W))
            Y=$((row * TILE_H))
            
            # Use -crop then -trim to tightly crop each tile
            magick "$SHEET1_TMP" -crop "${TILE_W}x${TILE_H}+${X}+${Y}" -trim +repage "$BADGES_DIR/badge_$(printf '%02d' $NUM).png" 2>/dev/null
            
            # Verify the output
            if [ -f "$BADGES_DIR/badge_$(printf '%02d' $NUM).png" ]; then
                SIZE=$(identify -format "%wx%h" "$BADGES_DIR/badge_$(printf '%02d' $NUM).png")
                echo "  Created: badge_$(printf '%02d' $NUM).png (${SIZE})"
            fi
        done
    done
else
    echo "Error: Sheet not found"
fi

echo ""
echo "=== Summary ==="
echo "Total badges created: $(ls -1 $BADGES_DIR/*.png 2>/dev/null | wc -l)"
echo ""
echo "Files in $BADGES_DIR:"
ls -la "$BADGES_DIR"
