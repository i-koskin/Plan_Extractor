from entities.plan import Plan
from adapters.cv_wall_detector import detect_doors_walls_windows
import os


def extract_plan_from_image(image_path: str) -> Plan:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    doors, walls, windows = detect_doors_walls_windows(image_path)

    return Plan(
        source=image_path,
        walls=walls,
        doors=doors,
        windows=windows
    )
