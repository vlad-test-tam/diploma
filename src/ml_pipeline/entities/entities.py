from pydantic import BaseModel
from typing import Dict, Literal


class Coordinates(BaseModel):
    start: Dict[str, int]
    end: Dict[str, int]


class Defect(BaseModel):
    type: Literal['scratch', 'noise']
    coordinates: Coordinates


class_mapping = {
    "scratch": 0,
    "noise": 1
}
