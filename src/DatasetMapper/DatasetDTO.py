from __future__ import annotations
from dataclasses import dataclass

from typing import List, Tuple, Dict, Set


# Adapted from https://github.com/mcordts/cityscapesScripts/blob/aeb7b82531f86185ce287705be28f452ba3ddbb8/cityscapesscripts/helpers/labels.py#L62
@dataclass(unsafe_hash=True)
class Label:
    name: str
    id: int
    trainId: int
    category: str
    categoryId: int
    color: Tuple[int, int, int]

    def __init__(self, name, id=None, trainId=None, category=None, categoryId=None, color=(0, 0, 0)):
        self.name = name
        self.id = id
        self.trainId = trainId
        self.category = category
        self.categoryId = categoryId
        self.color = color


@dataclass()
class Dataset:
    labels: Dict[str, Label]
    mappings: Dict[Tuple[int, int, int], Tuple[int, int, int]]

    def __init__(self, labels: List[Label]):
        self.labels = {}
        self.mappings = {}
        for label in labels:
            self.labels[label.name] = label

    def get_label(self, name: str):
        return self.labels.get(name, None)

    def get_all_group_labels(self, group_name: str):
        group = []
        for label in self.labels.values():
            if label.category == group_name:
                group.append(label)
        return group

    def create_mappings_from_dict(self, mapping_dict: Dict[str, List[str]], other_dataset: Dataset, grayscale=False):
        for k, v in mapping_dict.items():
            self_label = self.get_label(k)
            for label in v:
                other_label = other_dataset.get_label(label)
                # TODO check if it's really trainid
                gray = other_label.trainId
                gray_tup = (gray, gray, gray)
                self.mappings[self_label.color] = other_label.color if not grayscale else gray_tup
