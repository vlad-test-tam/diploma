import os
from typing import List, Dict

import cv2
import numpy as np
from scipy.stats import poisson

from src.ml_pipeline.entities.entities import Coordinates, Defect
from src.ml_pipeline.preprocessing.defects_generator.defect_generator import BaseDefectGenerator


class NoiseGenerator(BaseDefectGenerator):
    def __init__(self, image_path):
        self.image_name = os.path.basename(image_path)
        self.original_image = cv2.imread(image_path)
        self.defected_image = self.original_image.copy()
        self.defects = []

    def generate_defects(self):
        h, w = self.defected_image.shape[:2]

        centers = np.column_stack(
            (np.random.randint(0, w, 40), np.random.randint(0, h, 40))
        )

        max_defect_size_h = h // 5  # Максимальная высота дефекта
        max_defect_size_w = w // 5  # Максимальная ширина дефекта

        for center in centers:
            x, y = center

            defect_height = np.random.randint(1, max_defect_size_h + 1)
            defect_width = np.random.randint(1, max_defect_size_w + 1)

            growth_steps = int((defect_height * defect_width) // 10)

            top_left_x = max(0, x - defect_width // 2)
            top_left_y = max(0, y - defect_height // 2)
            bottom_right_x = min(w - 1, top_left_x + defect_width)
            bottom_right_y = min(h - 1, top_left_y + defect_height)

            if top_left_x >= bottom_right_x or top_left_y >= bottom_right_y:
                continue

            noise_points = []
            for _ in range(growth_steps):
                x_new = np.random.randint(top_left_x, bottom_right_x)
                y_new = np.random.randint(top_left_y, bottom_right_y)

                if 0 <= x_new < w and 0 <= y_new < h:
                    self.defected_image[y_new, x_new] = np.clip(
                        self.defected_image[y_new, x_new] + np.random.exponential(50), 0, 255
                    )
                    noise_points.append((x_new, y_new))

            defect_coordinates = Coordinates(
                start={"x": top_left_x, "y": top_left_y},
                end={"x": bottom_right_x, "y": bottom_right_y}
            )
            defect = Defect(type="noise", coordinates=defect_coordinates)
            self.defects.append(defect)

    def highlight_defects(self) -> np.ndarray:
        image_with_defects = self.defected_image.copy()

        for defect in self.defects:
            start = defect.coordinates.start
            end = defect.coordinates.end
            cv2.rectangle(image_with_defects,
                          (start['x'], start['y']),
                          (end['x'], end['y']),
                          color=(0, 255, 0),
                          thickness=2)
        return image_with_defects

    def generate_json(self) -> Dict:
        json_data = {
            "pic_name": self.image_name,
            "defects": [
                {
                    "type": defect.type,
                    "coordinates": {
                        "start": defect.coordinates.start,
                        "end": defect.coordinates.end
                    }
                } for defect in self.defects
            ]
        }
        return json_data
