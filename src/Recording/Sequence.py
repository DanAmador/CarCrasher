from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from beamngpy import Vehicle
from beamngpy.sensors import Camera

from src.Recording.Capture import Capture
from src.util import create_paths, create_folders


@dataclass
class ImageSequence(ABC):
    captures: List[Capture]
    entry_path: Path

    def __init__(self, data_path_entry: Path):
        create_paths([data_path_entry])
        self.entry_path = data_path_entry
        self.seq_folder = create_folders(self.entry_path)
        self.captures = []

    @abstractmethod
    def capture_frame(self, current_frame):
        pass


class StaticCamSequence(ImageSequence):

    def __init__(self, data_path_entry: Path, camera: Camera, camera_id):
        super().__init__(data_path_entry)
        self.cam = camera
        self.cam_id = camera_id
        self.data = {}

    def capture_frame(self, current_frame):
        self.captures.append(
            Capture(current_frame, self.data, f"{str(current_frame).zfill(6)}", self.entry_path, self.seq_folder))


class CarSequence(ImageSequence):
    def __init__(self, data_path_entry: Path, vehicle: Vehicle):
        super().__init__(data_path_entry)
        self.vehicle = vehicle
        self.points = np.array([])

    def capture_frame(self, current_frame):
        self.vehicle.poll_sensors()
        lidar = self.vehicle.sensors["lidar"]
        cam = self.vehicle.sensors["camera"]
        state = self.vehicle.sensors["state"].data

        points = []
        if lidar:
            points = lidar.data["points"].reshape(lidar.data["points"].size // 3, 3)
        # print(f"current_capture {current_frame} of {total_captures}")
        local_cam_pos = np.array(cam.pos)
        local_cam_dir = np.array(cam.direction)[None, :]
        world_car_pos = np.array(state["pos"])
        up = np.array(state["up"])
        car_dir = np.array(state["dir"])
        car_pos_matrix = np.array([
            car_dir,
            up,
            np.cross(up, car_dir)
        ])
        # car_pos_matrix = [np.array()]

        data = cam.data
        data["camera"] = {
            "fov": cam.fov,
            "width": cam.resolution[0],
            "height": cam.resolution[1],
            "depth": cam.near_far[1],
            "world_car_pos": world_car_pos,
            "local_cam_pos": local_cam_pos,
            "euler_rot": np.reshape(car_pos_matrix @ local_cam_dir.T, (3,)),
            "car_dir": car_dir,
            "up": up
        }
        data["points"] = points
        self.captures.append(
            Capture(current_frame, data, f"{str(current_frame).zfill(6)}", self.entry_path, self.seq_folder))

