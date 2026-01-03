import cv2
import numpy as np
from collections import Counter

INPUT = "Images/Cups/Cryon_Cup.png"
OUTPUT = "clean_flat.png"

NUM_MAIN_COLORS = 4     # how many dominant colors to keep
TOLERANCE = 30          # how close a pixel must be to snap

# Load image
img = cv2.imread(INPUT, cv2.IMREAD_UNCHANGED)

# Separate alpha
if img.shape[2] == 4:
    rgb = img[:, :, :3]
    alpha = img[:, :, 3]
else:
    rgb = img
    alpha = None

# Flatten pixels
pixels = rgb.reshape(-1, 3)

# Find most common colors (the "main" ones)
counts = Counter(map(tuple, pixels))
main_colors = np.array([c for c, _ in counts.most_common(NUM_MAIN_COLORS)])

# Snap pixels to nearest main color if close enough
out = rgb.copy()

for color in main_colors:
    diff = np.linalg.norm(out.astype(np.int16) - color, axis=2)
    mask = diff < TOLERANCE
    out[mask] = color

# Reattach alpha
if alpha is not None:
    out = np.dstack((out, alpha))

cv2.imwrite(OUTPUT, out)
print("Saved cleaned image with snapped colors.")
