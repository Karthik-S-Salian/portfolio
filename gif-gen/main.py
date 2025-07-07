import os
import cv2
import numpy as np
from PIL import Image

# Directories
################################################
input_gif = "Xp6VZ6Zp0ho7CaccLg.gif"
flood_fill_diff = (20, 20, 20)
erode_kernel = np.ones((3, 3), np.uint8)
output_gif = "output.gif"
################################################

frame_dir = "frames"
output_dir = "processed_frames"

os.makedirs(frame_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Step 1: Extract frames using ffmpeg
os.system(f"ffmpeg -y -i {input_gif} {frame_dir}/frame_%04d.png")

# Step 2: Flood fill from edges
def remove_edge_white(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]

    # Ensure 4 channels (BGRA)
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    bgr = img[:, :, :3].copy()
    alpha = img[:, :, 3].copy()

    # Create mask for floodFill (size must be 2px larger than image)
    mask = np.zeros((h + 2, w + 2), np.uint8)

    # Create a transparent mask to apply later
    transparent_mask = np.zeros((h, w), np.uint8)

    # Flood fill from edges in BGR
    for x in range(w):
        for y in [0, h - 1]:
            cv2.floodFill(bgr, mask, (x, y), (0, 0, 0),
                          loDiff=flood_fill_diff, upDiff=flood_fill_diff
                        , flags=4 | (255 << 8))
        for y in range(h):
            for x in [0, w - 1]:
                cv2.floodFill(bgr, mask, (x, y), (0, 0, 0),
                              loDiff=flood_fill_diff, upDiff=flood_fill_diff
                                , flags=4 | (255 << 8))

    # Extract filled area from mask and apply to alpha
    filled = mask[1:-1, 1:-1]  # crop back to original size
    alpha[filled == 255] = 0   # make filled area fully transparent

    # Merge back into BGRA
    result = cv2.merge((bgr[:, :, 0], bgr[:, :, 1], bgr[:, :, 2], alpha))
    return result


# Step 3: Process each frame
for filename in sorted(os.listdir(frame_dir)):
    if filename.endswith(".png"):
        path = os.path.join(frame_dir, filename)
        img = remove_edge_white(path)
        # Optional: Clean up thin white outlines by eroding transparent edges

        alpha_mask = img[:, :, 3]
        alpha_mask = cv2.erode(alpha_mask, erode_kernel, iterations=1)
        img[:, :, 3] = alpha_mask

        out_path = os.path.join(output_dir, filename)
        cv2.imwrite(out_path, img)

# Step 4: Convert processed frames back to GIF
from PIL import Image

frames = [Image.open(os.path.join(output_dir, f)) for f in sorted(os.listdir(output_dir)) if f.endswith(".png")]
frames[0].save(output_gif, save_all=True, append_images=frames[1:], loop=0, duration=100, disposal=2, transparency=0)
