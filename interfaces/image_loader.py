import cv2
from typing import Any


def load_image(image_path: str) -> Any:
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Failed to load image: {image_path}")
    return img
