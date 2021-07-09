import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List

from beamngpy import Vehicle

from BeamBuilder import BeamBuilder
from thread_worker import ThreadQueueWorker
from util import create_paths, beam2folderNames, create_folders, NumpyArrayEncoder

import numpy as np
import json

# TODO check this
# def ply_header(count_vertices, with_normals=False, point_num_views=False):
#     if with_normals:
#         header = [
#             "ply",
#             "format ascii 1.0",
#             "element vertex {}".format(count_vertices),
#             "property float x",
#             "property float y",
#             "property float z",
#             "property float nx",
#             "property float ny",
#             "property float nz",
#             "property uchar diffuse_red",
#             "property uchar diffuse_green",
#             "property uchar diffuse_blue",
#         ]
#     else:
#         header = [
#             "ply",
#             "format ascii 1.0",
#             "element vertex {}".format(count_vertices),
#             "property float x",
#             "property float y",
#             "property float z",
#             "property uchar diffuse_red",
#             "property uchar diffuse_green",
#             "property uchar diffuse_blue",
#         ]
#
#     if point_num_views:
#         header += ["property uchar views"]
#
#     header += ["end_header"]
#
#     return header
#
#
# def points_to_ply_string(vertices, point_num_views=False):
#     header = ply_header(len(vertices), point_num_views=point_num_views)
#     return "\n".join(header + vertices + [""])
import random


@dataclass(frozen=False)
class Capture:
    frame: int
    data: dict
    name: str
    entry_path: Path
    seq_name: str

    def save_to_file(self):
        #  print(f"Saving {self.seq_name}/{self.name}")
        cam = None
        depth = None
        for beamName, folderName in beam2folderNames.items():
            img = self.data.get(beamName)
            if beamName == "extrinsic":
                cam = img
                with open((self.entry_path / "extrinsic" / self.seq_name / f"{self.name}.json").absolute(), "w") as f:
                    json.dump(img, f, cls=NumpyArrayEncoder)
                continue
            if img is not None:

                if beamName == "depth":
                    depth = img
                img.convert("RGB").save((self.entry_path / folderName / self.seq_name / f"{self.name}.png").absolute())

        if cam and depth:
            verts = self.sample_depth_map(cam, depth, 1000)
            with open((self.entry_path / "vertices" / self.seq_name / f"{self.name}.json").absolute(), "w") as f:
                json.dump(verts, f, cls=NumpyArrayEncoder)

    def sample_depth_map(self, cam, depth, number_of_points):
        vertices = []

        (w, h) = depth.size
        max_depth = cam["depth"]

        cam_pos = np.array(cam["pos"])
        cam_dir = np.array(cam["direction"])[None, :]
        for n in range(number_of_points):
            coordinates = random.randint(0, w-1), random.randint(0, h-1)
            depth_scaler = (depth.getpixel(coordinates) / 256) * max_depth
            vertices.append(cam_pos + cam_dir * depth_scaler)
        return vertices


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

    def capture_frame(self, current_frame):
        self.vehicle.poll_sensors()
        cam = self.vehicle.sensors["camera"]
        state = self.vehicle.sensors["state"].data
        data = cam.data

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
        data["extrinsic"] = {
            "pos": world_car_pos + local_cam_pos,
            "direction": (car_pos_matrix @ local_cam_dir.T).T,
            "depth": cam.near_far[1]
        }
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
            del capture

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
            self.scenario.on_recording_step()
            self.bb.bmng.render_cameras()
            self.bb.bmng.step(wait_time)
            self.bb.bmng.pause()

        self.bb.bmng.resume()
