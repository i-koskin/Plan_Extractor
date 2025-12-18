import cv2
import numpy as np
from pathlib import Path
from entities.plan import Plan
from interfaces.image_loader import load_image


def visualize_plan(plan: Plan, output_image_path: str):
    """
    Сохраняет визуализацию плана: стены, двери, окна, помещения, размеры.

    Args:
        plan: объект Plan с результатами извлечения
        output_image_path: путь для сохранения изображения
    """
    # Загружаем исходное изображение
    img = load_image(plan.source)

    output = img.copy()

    # 1. Стены — зелёные полилинии
    for wall in plan.walls:
        pts = np.array(wall.points, np.int32)
        if pts.shape[0] > 1:
            cv2.polylines(output, [pts], isClosed=False,
                          color=(0, 255, 0), thickness=2)

    # 2. Двери — синие прямоугольники
    for door in plan.doors:
        x1, y1, x2, y2 = door.bbox
        cv2.rectangle(output, (x1, y1), (x2, y2),
                      color=(255, 0, 0), thickness=2)
        cv2.putText(output, "door", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # 3. Окна — красные прямоугольники
    for window in plan.windows:
        x1, y1, x2, y2 = window.bbox
        cv2.rectangle(output, (x1, y1), (x2, y2),
                      color=(0, 0, 255), thickness=2)
        cv2.putText(output, "window", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Сохраняем
    Path(output_image_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(output_image_path, output)
