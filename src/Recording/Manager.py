from dataclasses import dataclass

from src.BeamBuilder import BeamBuilder
from src.Recording.Sequence import StaticCamSequence
from src.util import ThreadQueueWorker


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
            static_cameras = self.bb.bmng.render_cameras()
            for sequence in self.scenario.sequences:
                if isinstance(sequence, StaticCamSequence):
                    sequence.capture_frame_wrapper(current_capture, static_cameras[sequence.cam_id])
                else:
                    sequence.capture_frame(current_capture)

            if frame_buffer > batch_idx or current_capture == total_captures:
                frame_buffer = 0
                self.save_frames()
            self.bb.bmng.step(wait_time)
            self.scenario.on_recording_step()
            self.bb.bmng.pause()

        self.bb.bmng.resume()
