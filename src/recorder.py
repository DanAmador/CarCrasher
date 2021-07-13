import copy
import json
import random
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from beamngpy import Vehicle

from BeamBuilder import BeamBuilder
from thread_worker import ThreadQueueWorker
from util import create_paths, beam2folderNames, create_folders, NumpyArrayEncoder


@dataclass(frozen=False)
class Capture:
    frame: int
    data: dict
    name: str
    entry_path: Path
    seq_name: str

    def save_to_file(self):
        #  print(f"Saving {self.seq_name}/{self.name}")

        for beamName, folderName in beam2folderNames.items():
            f_path = self.entry_path / folderName / self.seq_name
            img = self.data.get(beamName)
            if beamName == "camera":
                with open((f_path / f"{self.name}.json").absolute(), "w") as f:
                    json.dump(img, f, cls=NumpyArrayEncoder)
            elif beamName == "pointclouds":

                vertices = self.data.get("points")
                # vertices = points.reshape(points.size // 3, 3)
                # random.shuffle(vertices)
                with open((f_path / f"{self.name}.txt").absolute(), "w") as f:
                    for idx in range(len(vertices)):
                        # print(p)
                        # p = p.tolist()

                        if idx > 5000:
                            break
                        try:
                            # p = " ".join([str(v) for v in vertices[random.randint(0, len(vertices))]])
                            # p = vertices[random.randint(0, len(vertices))]
                            p = vertices[random.randint(0, len(vertices))]
                            f.write(f"{p[0]} {p[1]} {p[2]}\n")
                        except IndexError:
                            print(f"index error with {p}")
                            continue
            # o3d.io.write_point_cloud(pcd_name, pcd, False, True)
            elif img is not None:
                img.convert("RGB").save((f_path / f"{self.name}.png").absolute())

        del self.data

        # __init__(self: open3d.cpu.pybind.geometry.PointCloud, points: open3d.cpu.pybind.utility.Vector3dVector)


@dataclass
class ImageSequence:
    captures: List[Capture]
    entry_path: Path

    def __init__(self, data_path_entry: Path, vehicle: Vehicle):
        create_paths([data_path_entry])
        self.entry_path = data_path_entry
        self.seq_folder = create_folders(self.entry_path)
        self.captures = []
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
        pic_name = f"{str(current_frame).zfill(6)}"
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

        data = copy.copy(cam.data)
        data["camera"] = {
            "fov": cam.fov,
            "width": cam.resolution[0],
            "height": cam.resolution[1],
            "depth": cam.near_far[1],
            "world_car_pos": world_car_pos ,
            "local_cam_pos": local_cam_pos,
            "euler_rot": np.reshape(car_pos_matrix @ local_cam_dir.T, (3,)),
            "car_dir": car_dir,
            "up": up
        }
        data["points"] = points
        self.captures.append(Capture(current_frame, data, pic_name, self.entry_path, self.seq_folder))


@dataclass()
class SequenceManager:
    def __init__(self, bb: BeamBuilder, scenario):

        self.bb: BeamBuilder = bb
        self.threads = []
        self.scenario = scenario
        self.worker_q = ThreadQueueWorker(self.save_worker)
        self.worker_q.start_execution()

    def save_frames(self):
        for seq in self.scenario.sequences:
            if len(seq.captures) != 0:
                print(f"Saving {len(seq.captures)} frames for {seq.seq_folder}")
                for capture in seq.captures:
                    self.worker_q.push_to_queue(capture)

                seq.captures = []

        # $capture.save_to_file()

    def save_worker(self):
        while True:
            capture = self.worker_q.work_q.get()
            capture.save_to_file()

    def capture_footage(self, steps_per_sec=60, framerate: int = 24, total_captures: int = 240, duration=None):
        current_capture = 0

        wait_time = max(int(60 / framerate), 1)
        print(
            f"Recording {len(self.scenario.sequences)} sequences at  {framerate}fps every {wait_time} steps at {steps_per_sec} physics steps per second ")
        if duration is not None:
            total_captures = framerate * duration
        batch_idx = max(total_captures /
                        50, 1)
        frame_buffer = 0

        while current_capture <= total_captures:
            current_capture += 1
            frame_buffer += 1
            print(f"current_capture {current_capture} of {total_captures}")
            for sequence in self.scenario.sequences:
                sequence.capture_frame(current_capture)

            if frame_buffer > batch_idx or current_capture == total_captures:
                frame_buffer = 0
                self.save_frames()
            self.bb.bmng.render_cameras()
            self.bb.bmng.step(wait_time)
            self.scenario.on_recording_step()
            self.bb.bmng.pause()

        self.bb.bmng.resume()
