import numpy as np
from pathlib import Path
from entities.plan import Wall, Door, Window
from ultralytics import YOLO
from sklearn.cluster import DBSCAN

YOLO_MODEL_PATH = "runs/detect/train/weights/best.pt"

_yolo_model = None


def get_yolo_model():
    global _yolo_model
    if _yolo_model is None:
        p = Path(YOLO_MODEL_PATH)
        if not p.exists():
            raise FileNotFoundError(f"Model not found: {p.absolute()}")
        _yolo_model = YOLO(str(p))
    return _yolo_model


# def merge_wall_boxes_into_lines(wall_boxes, eps=20, min_samples=1):
#     """
#     Объединяет близкие bounding boxes стен в линии.
#     Предполагается, что стены — либо горизонтальные, либо вертикальные.
#     """
#     if len(wall_boxes) == 0:
#         return []

#     # Центры и ориентация
#     centers = []
#     orientations = []  # True = вертикальная, False = горизонтальная

#     for x1, y1, x2, y2 in wall_boxes:
#         cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
#         w, h = x2 - x1, y2 - y1
#         is_vertical = h > w
#         centers.append([cx, cy])
#         orientations.append(is_vertical)

#     centers = np.array(centers)
#     lines = []

#     # Раздельная кластеризация для вертикальных и горизонтальных стен
#     for is_vert in [True, False]:
#         mask = np.array(orientations) == is_vert
#         if not np.any(mask):
#             continue
#         pts = centers[mask]
#         if len(pts) == 1:
#             x1, y1, x2, y2 = wall_boxes[np.where(mask)[0][0]]
#             lines.append([(x1, y1), (x2, y2)]
#                          if is_vert else [(x1, y1), (x2, y1)])
#             continue

#         # DBSCAN для объединения близко расположенных стен
#         clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(pts)
#         labels = clustering.labels_

#         for label in set(labels):
#             if label == -1:
#                 continue  # шум
#             cluster_idxs = np.where(mask)[0][labels == label]
#             cluster_boxes = [wall_boxes[i] for i in cluster_idxs]

#             if is_vert:
#                 # Объединяем в одну вертикальную линию
#                 xs = [(b[0] + b[2]) / 2 for b in cluster_boxes]
#                 ys = [b[1] for b in cluster_boxes] + [b[3]
#                                                       for b in cluster_boxes]
#                 x = int(np.median(xs))
#                 y1, y2 = int(min(ys)), int(max(ys))
#                 lines.append([(x, y1), (x, y2)])
#             else:
#                 # Объединяем в одну горизонтальную линию
#                 ys = [(b[1] + b[3]) / 2 for b in cluster_boxes]
#                 xs = [b[0] for b in cluster_boxes] + [b[2]
#                                                       for b in cluster_boxes]
#                 y = int(np.median(ys))
#                 x1, x2 = int(min(xs)), int(max(xs))
#                 lines.append([(x1, y), (x2, y)])

#     return lines


def merge_wall_boxes_by_clusters(wall_boxes, eps=10):
    """
    Объединяет близкие bounding boxes стен в полилинии.
    Предполагается, что стены — либо горизонтальные, либо вертикальные.
    """
    if len(wall_boxes) == 0:
        return []

    centers = np.array([((b[0]+b[2])/2, (b[1]+b[3])/2) for b in wall_boxes])
    clustering = DBSCAN(eps=eps, min_samples=1).fit(centers)
    labels = clustering.labels_

    merged_boxes = []
    for label in set(labels):
        cluster_boxes = [wall_boxes[i]
                         for i in range(len(wall_boxes)) if labels[i] == label]
        x1 = min(b[0] for b in cluster_boxes)
        y1 = min(b[1] for b in cluster_boxes)
        x2 = max(b[2] for b in cluster_boxes)
        y2 = max(b[3] for b in cluster_boxes)
        merged_boxes.append((x1, y1, x2, y2))
    return merged_boxes


def detect_doors_walls_windows(image_path: str):
    model = get_yolo_model()
    results = model(image_path, conf=0.45, iou=0.5)
    wall_boxes = []
    doors, walls, windows = [], [], []
    for box in results[0].boxes:
        cls_id = int(box.cls.item())
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        bbox = (x1, y1, x2, y2)
        if cls_id == 0:
            doors.append(Door(id=f"d{len(doors)}", bbox=bbox))
        elif cls_id == 1:
            wall_boxes.append(bbox)
        elif cls_id == 2:
            windows.append(Window(id=f"w{len(windows)}", bbox=bbox))
    # # Объединяем боксы стен в линии
    # wall_lines = merge_wall_boxes_into_lines(wall_boxes, eps=25)
    # walls = [Wall(id=f"w{i}", points=line)
    #          for i, line in enumerate(wall_lines)]
    # Объединяем боксы стен в полилинии
    merged_boxes = merge_wall_boxes_by_clusters(wall_boxes)
    for i, (x1, y1, x2, y2) in enumerate(merged_boxes):
        # Преобразуем боксы стен в полилинию (замкнутый прямоугольник)
        points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
        walls.append(Wall(id=f"w{i}", points=points))

    return doors, walls, windows
