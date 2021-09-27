import os
import queue
import threading
from json import JSONEncoder
from pathlib import Path

import numpy as np
from beamngpy.beamngcommon import compute_rotation_matrix


def quaternion_to_direction_vector(quaternion, axis=0):
    rot_matrix = compute_rotation_matrix(quaternion)
    vec = rot_matrix[axis % 3, :]
    print(f"Quat: {quaternion} - Vector: {vec} - Axis: {axis}")
    return vec


class ThreadQueueWorker:
    def __init__(self, worker_function):
        self.threads = []
        self.work_q = queue.Queue()
        for t in range(10):
            worker = threading.Thread(target=worker_function)
            worker.daemon = True
            self.threads.append(worker)

    def start_execution(self, timeout=None):
        for thread in self.threads:
            thread.start()

        if timeout is not None:
            self.wait_until_done(timeout)

    def wait_until_done(self, timeout):
        for thread in self.threads:  # iterates over the threads
            thread.join(timeout)  # waits until the thread has finished work

    def push_to_queue(self, to_add):
        self.work_q.put(to_add)


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def create_paths(paths):
    for p in paths:
        if not p.exists():
            os.mkdir(p)


def create_folders(entry_path: Path, with_seq=True):
    folder_names = list(beam2folderNames.values())
    folders = [entry_path / name for name in folder_names]
    create_paths([entry_path])
    create_paths(folders)
    amount_of_seqs = []
    for folder in folders:
        amount_of_seqs.append(len([x for x in folder.iterdir() if x.is_dir()]))

    has_same = [x == amount_of_seqs[-1] for x in amount_of_seqs]
    assert all(has_same)

    seq_num = str(amount_of_seqs[-1] + 1).zfill(4)
    seq_name = f"seq{seq_num}"
    if with_seq:
        create_paths([folder / seq_name for folder in folders])
    return seq_name


beam2folderNames = {
    "colour": "images",
    "instance": "instance_maps",
    "depth": "depth",
    "annotation": "raw_annotations",
    "camera": "camera",
    "pointclouds": "pointclouds",
    "fragments": "fragments",
    "unprojections": "unprojections"
}

# 'unlabeled',
# 'ego vehicle',
# 'rectification border',
# 'out of roi',
# 'static',
# 'dynamic',
# ground
# 'road',
# 'parking',
# 'rail track', 10,
# 'building', 11, 2,
# 'wall', 12, 3, 'co
# 'fence', 13, 4, 'co
# 'guard rail', 14, 255, 'co
# 'bridge', 15, 255, 'co
# 'tunnel', 16, 255, 'c
# 'pole', 17,
# 'polegroup', 18, 25
# 'traffic light', 19,
# 'traffic sign', 20
# 'vegetation', 21,
# 'terrain', 22,
# 'person', 24
# 'rider',
# 'car', 26
# 'truck', 2
# 'bus', 28,
# 'caravan', 29
# 'trailer', 30,
# 'train', 31,
# 'motorcycle', 32
# 'bicycle', 33,
# 'license plate', -1,


beam2CityLabelMap = {
    "SKY": "sky",
    "STREET": "road",
    "SIDEWALK": "sidewalk",
    "ASPHALT": "road",
    "CAR": "car",
    "BUILDINGS": "building",
    "POLE": "pole",
    "TRUCK": "truck",
    "BACKGROUND": "sky",
    "DASHED_LINE": "guard rail",
    "COBBLESTONE": "road",
    "NATURE": "vegetation",
    "OBSTACLES": "person",
    "DRIVING_INSTRUCTIONS": "person",
    "RESTRICTED_STREET": "road",
    "ROADBLOCK": "wall",
    "SIDEBARS": "guard rail",
    "SOLID_LINE": "person",
    "SPEED_BUMP": "person",
    "TRAFFIC_SIGNALS": "traffic light",
    "TRAFFIC_SIGNS": "traffic sign",
    "TRUCK_TRAILERS": "bus",
    "ZEBRA_CROSSING": "person",
    "GUARD_RAIL": "person",
    "WATER": "vegetation",
    "ROCK": "vegetation",
    "SAND": "terrain",
    "GRASS": "vegetation",
    "MUD": "vegetation",
}

