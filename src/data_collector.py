import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from beamngpy import BeamNGpy, Vehicle, Image

from BeamBuilder import BeamBuilder
import time
data_path = (Path(__file__).absolute()).parent.parent / "data"

beam2folderNames = {
    "colour": "images",
    "instance": "seg_maps",
    "depth": "depth",
    "annotation": "annotation",
    "annotation_dict": "annotation_dict",

}


@dataclass(frozen=False)
class Capture:
    frame: int
    data: dict
    name: str
    annotation_json: dict

    def save_to_file(self, entry_path, seq_name):
        for beamName, folderName in beam2folderNames.items():
            img = self.data.get(beamName)
            if img is not None:
                img.convert("RGB").save((entry_path / folderName / seq_name / f"{self.name}.png").absolute())

        with open((entry_path / "annotation_dict" / seq_name / f"{self.name}.json").absolute(), 'w') as f:
            json.dump(self.annotation_json, f)


@dataclass
class ImageSequence:
    captures: List[Capture]
    sequence_name: str
    entry_path: Path

    def __init__(self, name: str, data_path: Path):
        self.sequence_name = name
        self.entry_path = data_path / name
        self.seq_folder = self.create_folders(self.entry_path)
        self.captures = []

    def save_frames(self):
        print(f"Saving {len(self.captures)} objects")
        for capture in self.captures:
            capture.save_to_file(self.entry_path, self.seq_folder)

    def append(self, capture: Capture):
        self.captures.append(capture)

    @staticmethod
    def create_folders(entry_path: Path):
        def create_paths(paths):
            for p in paths:
                if not p.exists():
                    os.mkdir(p)

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
        create_paths([folder / seq_name for folder in folders])
        return seq_name


def capture_footage(bmng: BeamNGpy, vehicle: Vehicle, seq: ImageSequence, framerate: int = 24,
                    total_captures: int = 240):
    current_capture = 0
    wait_time = int(60 / framerate)
    print(f"Taking picture every {wait_time} steps at {framerate}fps")

    while current_capture < total_captures:
        current_capture += 1
        vehicle.poll_sensors()
        data = vehicle.sensors['camera'].data
        pic_name = f"{str(current_capture).zfill(6)}"
        print(current_capture)

        seq.append(Capture(current_capture, data, pic_name, annotation_json=bb.bmng.get_annotations()))
        bmng.render_cameras()
        bmng.step(wait_time)
        bmng.pause()

    bmng.resume()
    return seq


if __name__ == "__main__":
    bb = BeamBuilder(launch=False)
    cam = bb.cam_setup(annotation=True)
    bb.scenario_setup()
    bb.car_setup(sensors={"camera": cam}, rot_quat=(0, 0, 0.3826834, 0.9238795))
    bb.build_environment(ai_mode="span")
    #bb.bmng.set_relative_camera(pos=(2,2,2))

    sequence = ImageSequence("Example", data_path)
    time.sleep(5)
    capture_footage(bb.bmng, bb.vehicle, sequence, total_captures=10).save_frames()
