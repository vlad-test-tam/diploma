import os
from abc import abstractmethod, ABC
from typing import Dict, List

import cv2
import numpy as np


class BaseDefectGenerator:
    def __init__(self, image_path: str):
        self.image_name = os.path.basename(image_path)
        self.original_image = cv2.imread(image_path)
        self.defected_image = self.original_image.copy()
        self.defect_mask = np.zeros_like(self.original_image, dtype=np.uint8)
        self.resolution = self.defected_image.shape[1], self.defected_image.shape[0]
        self.defects = []

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

    def generate_yolo_format(self, class_mapping: Dict[str, int]) -> List[str]:

        yolo_lines = []
        img_w, img_h = self.resolution

        for defect in self.defects:
            defect_type = defect.type
            class_id = class_mapping.get(defect_type, 0)

            x1, y1 = defect.coordinates.start['x'], defect.coordinates.start['y']
            x2, y2 = defect.coordinates.end['x'], defect.coordinates.end['y']

            x1 = max(0, min(x1, img_w))
            x2 = max(0, min(x2, img_w))
            y1 = max(0, min(y1, img_h))
            y2 = max(0, min(y2, img_h))

            # YOLO: [class, x_center/w, y_center/h, width/w, height/h]
            x_center = ((x1 + x2) / 2) / img_w
            y_center = ((y1 + y2) / 2) / img_h
            width = abs(x2 - x1) / img_w
            height = abs(y2 - y1) / img_h

            yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
            yolo_lines.append(yolo_line)

        return yolo_lines

    def highlight_defects_from_yolo(self, yolo_data: List[str]) -> np.ndarray:

        image_with_defects = self.defected_image.copy()

        img_w, img_h = self.resolution

        for line in yolo_data:
            parts = line.strip().split()
            class_id = int(parts[0])
            x_center = float(parts[1]) * img_w
            y_center = float(parts[2]) * img_h
            width = float(parts[3]) * img_w
            height = float(parts[4]) * img_h

            x_min = int(x_center - width / 2)
            y_min = int(y_center - height / 2)
            x_max = int(x_center + width / 2)
            y_max = int(y_center + height / 2)

            cv2.rectangle(image_with_defects, (x_min, y_min), (x_max, y_max), color=(0, 255, 0), thickness=2)

        return image_with_defects
