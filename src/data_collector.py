import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from beamngpy import BeamNGpy, Vehicle

from BeamBuilder import BeamBuilder
from config import Levels
from util import create_paths, data_path, beam2folderNames, create_folders


@dataclass(frozen=False)
class Capture:
    frame: int
    data: dict
    name: str

    def save_to_file(self, entry_path, seq_name):
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
        self.seq_folder = create_folders(self.entry_path)
        self.captures = []

    def save_frames(self):
        print(f"Saving {len(self.captures)} objects")
        for capture in self.captures:
            capture.save_to_file(self.entry_path, self.seq_folder)

    def append(self, capture: Capture):
        self.captures.append(capture)


def capture_footage(bmng: BeamNGpy, vehicle: Vehicle, seq: ImageSequence, framerate: int = 24,
                    total_captures: int = 240, duration=None):
    current_capture = 0
    wait_time = int(60 / framerate)
    print(f"Taking picture every {wait_time} steps at {framerate}fps")

    if duration is not None:
        total_captures = framerate * duration

    while current_capture < total_captures:
        current_capture += 1
        vehicle.poll_sensors()
        data = vehicle.sensors['camera'].data
        pic_name = f"{str(current_capture).zfill(6)}"
        print(f"current_capture {current_capture} of {total_captures}")

        seq.append(Capture(current_capture, data, pic_name))
        bmng.render_cameras()
        bmng.step(wait_time)
        bmng.pause()

    bmng.resume()
    return seq


if __name__ == "__main__":
    bb = BeamBuilder(launch=True)
    cam = bb.cam_setup(annotation=True)
    bb.scenario_setup(level=Levels.WEST_COAST)
    bb.car_setup(sensors={"camera": cam}, rot_quat=(0, 0, 0.3826834, 0.9238795))
    bb.build_environment(ai_mode="span", steps=30, hud=True)
    bb.vehicle.ai_set_speed(300, mode="limit")
    # bb.bmng.set_relative_camera(pos=(2,2,2))

    sequence = ImageSequence(data_path / "raw")
    input("Press space to record")
    # time.sleep(6)
    capture_footage(bb.bmng, bb.vehicle, sequence,
                    framerate=60,
                    duration=1
                    # total_captures=10
                    ).save_frames()
