import queue
import threading
from dataclasses import dataclass
from multiprocessing.dummy import Pool as ThreadPool
from pathlib import Path
from typing import List

from beamngpy import Vehicle

from BeamBuilder import BeamBuilder
from config import Levels, AIMode
from util import create_paths, data_path, beam2folderNames, create_folders
import time

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

    def __init__(self, data_path_entry: Path, vehicle: Vehicle):
        create_paths([data_path_entry])
        self.entry_path = data_path_entry
        self.seq_folder = create_folders(self.entry_path)
        self.captures = []
        self.save_queue = queue.Queue()
        self.vehicle = vehicle

    def save_frames(self):
        if len(self.captures) != 0:
            print(f"Saving {len(self.captures)} frames for {self.seq_folder}")
            for capture in self.captures:
                self.save_queue.put(capture)

            self.captures = []
            with ThreadPool() as pool:
                pool.apply_async(self.save_worker, (self.save_queue,))
        # $capture.save_to_file()

    def save_worker(self, q, multiplicity=5, maxlevel=3, lock=threading.Lock()):
        for capture in iter(q.get, None):  # blocking get until None is received
            try:
                with lock:
                    capture.save_to_file(self.entry_path, self.seq_folder)
            finally:
                q.task_done()

    def capture_frame(self, current_frame):
        self.vehicle.poll_sensors()
        data = self.vehicle.sensors['camera'].data
        pic_name = f"{str(current_frame).zfill(6)}"
        # print(f"current_capture {current_frame} of {total_captures}")

        self.captures.append(Capture(current_frame, data, pic_name))


@dataclass()
class SequenceManager:
    sequences: List[ImageSequence]
    bb: BeamBuilder

    def capture_footage(self, steps_per_sec=60, framerate: int = 24, total_captures: int = 240, duration=None):
        current_capture = 0
        wait_time = max(int(60 / framerate), 1)
        print(
            f"Recording {len(self.sequences)} sequences at  {framerate}fps every {wait_time} steps at {steps_per_sec} physics steps per second ")
        if duration is not None:
            total_captures = framerate * duration
        batch_idx = max(total_captures / 5, 1)

        while current_capture <= total_captures:
            current_capture += 1
            print(f"current_capture {current_capture} of {total_captures}")
            for sequence in sequences:
                sequence.capture_frame(current_capture)

                if len(sequence.captures) > batch_idx or current_capture == total_captures:
                    sequence.save_frames()
            self.bb.bmng.render_cameras()
            self.bb.bmng.step(wait_time)
            self.bb.bmng.pause()

        self.bb.bmng.resume()


def setup_test_sequence():
    sequences_list = []
    start_pos = (-717, 101, 118)

    target: Vehicle = None
    for i in range(3):
        offset = (i * 5, i * 5, 0)
        new_pos = tuple(x - y for x, y in zip(start_pos, offset))
        car_name = f"car_{i}"
        cam = bb.cam_setup(annotation=True)
        bb.with_car(vehicle_id=car_name, sensors={"camera": cam}, pos=new_pos, rot_quat=(0, 0, 0.3826834, 0.9238795))
        car = bb.get_vehicle(car_name)

        if i == 0:
            car.ai_set_mode(AIMode.SPAN)
            car.ai_set_speed(100, "set")
            target = car
        else:
            car.ai_set_mode(AIMode.CHASE)
            car.ai_set_target(target.vid)
            car.ai_set_speed(60, "limit")
        sequences_list.append(ImageSequence(data_path / "captures", car))

    # Set AIs

    return sequences_list


if __name__ == "__main__":
    framerate = 24
    steps_per_sec = 100

    bb = BeamBuilder(launch=True)
    bb.with_scenario(level=Levels.WEST_COAST)
    bb.build_environment(ai_mode="span", steps=steps_per_sec, hud=True)
    sequences = setup_test_sequence()
    # bb.bmng.set_relative_camera(pos=(2,2,2))

    # sequence = ImageSequence(data_path / "captures")
    manager = SequenceManager(sequences, bb)
    while True:
        #input("Press enter to record clip")
        time.sleep(6)
        manager.capture_footage(steps_per_sec=steps_per_sec, framerate=framerate, duration=1
                                # total_captures=10
                                )
