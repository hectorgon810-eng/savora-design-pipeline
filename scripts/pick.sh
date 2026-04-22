#!/bin/bash
# pick.sh — copy a winning variation into OUTPUT/PICKS/
# Usage: ./pick.sh <brand> <post-id> <variation>
# Example: ./pick.sh blue_mezcal BM-W-01 G1     # copies variation_G1.png
#          ./pick.sh blue_mezcal BM-W-01 2      # copies variation_2.png (single-backend)

set -euo pipefail

if [ $# -lt 3 ]; then
  echo "Usage: $0 <brand> <post-id> <variation>"
  echo "  variation: G1, G2, O1, O5, or plain 1/2/3 for single-backend batches"
  exit 1
fi

BRAND="$1"
POST="$2"
VAR="$3"

ROOT="/Users/dreamartstudio/Desktop/restaurant-design-pipeline"
SRC_DIR="$ROOT/OUTPUT/nano_banana/$BRAND/$POST"
PICKS_DIR="$ROOT/OUTPUT/PICKS/$BRAND"

mkdir -p "$PICKS_DIR"

SRC="$SRC_DIR/variation_${VAR}.png"
if [ ! -f "$SRC" ]; then
  echo "ERROR: $SRC not found"
  echo "Available:"
  ls "$SRC_DIR" | grep -E '^variation_' || true
  exit 1
fi

DEST="$PICKS_DIR/${POST}_V${VAR}.png"
cp "$SRC" "$DEST"
echo "✓ Picked: $DEST"
