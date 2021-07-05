import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List

from beamngpy import Vehicle

from BeamBuilder import BeamBuilder
from util import create_paths, beam2folderNames, create_folders


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
            img = self.data.get(beamName)
            if img is not None:
                img.convert("RGB").save((self.entry_path / folderName / self.seq_name / f"{self.name}.png").absolute())


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
        data = self.vehicle.sensors['camera'].data
        pic_name = f"{str(current_frame).zfill(6)}"
        # print(f"current_capture {current_frame} of {total_captures}")

        self.captures.append(Capture(current_frame, data, pic_name, self.entry_path, self.seq_folder))

@dataclass()
class SequenceManager:
    def __init__(self, bb: BeamBuilder, scenario):

        self.bb: BeamBuilder = bb
        self.save_queue = queue.Queue()
        self.threads = []
        self.scenario = scenario

        for t in range(10):
            worker = threading.Thread(target=self.save_worker)
            worker.daemon = True
            worker.start()
            self.threads.append(worker)

    def save_frames(self):
        for seq in self.scenario.sequences:
            if len(seq.captures) != 0:
                print(f"Saving {len(seq.captures)} frames for {seq.seq_folder}")
                for capture in seq.captures:
                    self.save_queue.put(capture)

                seq.captures = []

        # $capture.save_to_file()

    def save_worker(self):
        while True:
            capture = self.save_queue.get()
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
            self.bb.bmng.render_cameras()
            self.bb.bmng.step(wait_time)
            self.scenario.on_recording_step()
            self.bb.bmng.pause()

        self.bb.bmng.resume()

