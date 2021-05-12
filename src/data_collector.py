import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List

from beamngpy import BeamNGpy, Vehicle

from BeamBuilder import BeamBuilder
from config import Levels
from util import create_paths, data_path, beam2folderNames, create_folders
from multiprocessing.dummy import Pool as ThreadPool
import queue
from multiprocessing import Queue


@dataclass(frozen=False)
class Capture:
    frame: int
    data: dict
    name: str

    def save_to_file(self, entry_path: Path, seq_name: str):
        for beamName, folderName in beam2folderNames.items():
            img = self.data.get(beamName)
            if img is not None:
                img.convert("RGB").save((entry_path / folderName / seq_name / f"{self.name}.png").absolute())


@dataclass
class ImageSequence:
    captures: List[Capture]
    entry_path: Path

    def __init__(self, data_path_entry: Path):
        create_paths([data_path_entry])
        self.entry_path = data_path_entry
        self.seq_folder = "default"
        self.captures = []
        self.save_queue = queue.Queue()

    def save_frames(self):
        if len(self.captures) != 0:
            print(f"Saving {len(self.captures)} frames for {self.seq_folder}")
            for capture in self.captures:
                self.save_queue.put(capture)

            self.captures = []
            with ThreadPool() as pool:
                pool.apply_async(self.worker, (self.save_queue,))
        # $capture.save_to_file()

    def worker(self, q, multiplicity=5, maxlevel=3, lock=threading.Lock()):
        for capture in iter(q.get, None):  # blocking get until None is received
            try:
                with lock:
                    capture.save_to_file(self.entry_path, self.seq_folder)
            finally:
                q.task_done()

    def capture_footage(self, bmng: BeamNGpy, vehicle: Vehicle, steps_per_sec=60, framerate: int = 24,
                        total_captures: int = 240, duration=None):

        self.seq_folder = create_folders(self.entry_path)
        current_capture = 0
        wait_time = max(int(60 / framerate), 1)
        print(
            f"Recording {self.seq_folder} {framerate}fps every {wait_time} steps at {steps_per_sec} physics steps per second ")

        if duration is not None:
            total_captures = framerate * duration

        batch_idx = max(total_captures / 10, 1)
        while current_capture < total_captures:
            current_capture += 1
            vehicle.poll_sensors()
            data = vehicle.sensors['camera'].data
            pic_name = f"{str(current_capture).zfill(6)}"
            print(f"current_capture {current_capture} of {total_captures}")

            self.captures.append(Capture(current_capture, data, pic_name))

            if len(self.captures) > batch_idx:
                self.save_frames()
            bmng.render_cameras()
            bmng.step(wait_time)
            bmng.pause()

        bmng.resume()

        self.save_frames()
        return self


if __name__ == "__main__":
    framerate = 24
    steps_per_sec = 100

    bb = BeamBuilder(launch=True)
    cam = bb.cam_setup(annotation=True)
    bb.scenario_setup(level=Levels.WEST_COAST)
    bb.car_setup(sensors={"camera": cam}, rot_quat=(0, 0, 0.3826834, 0.9238795))
    bb.build_environment(ai_mode="span", steps=steps_per_sec, hud=True)
    bb.vehicle.ai_set_speed(300, mode="limit")
    # bb.bmng.set_relative_camera(pos=(2,2,2))

    sequence = ImageSequence(data_path / "captures")

    while True:
        input("Press enter to record clip")
        # time.sleep(6)
        sequence.capture_footage(bb.bmng, bb.vehicle, steps_per_sec=steps_per_sec, framerate=framerate, duration=1
                                 # total_captures=10
                                 )
