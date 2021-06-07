from abc import ABC, abstractmethod

from typing import List

from beamngpy import Vehicle

import BeamBuilder
from config import AIMode
from recorder import ImageSequence
from config import UserSettings as us


class AbstractRecordingScenario(ABC):

    def __init__(self, bb: BeamBuilder):
        self.bb = bb
        self.sequences = []
        self.setup_scenario()

    @abstractmethod
    def on_recording_step(self):
        return

    @abstractmethod
    def setup_scenario(self):
        return []


class BasicCarChase(AbstractRecordingScenario):
    def on_recording_step(self):
        pass

    def setup_scenario(self):

        sequences_list = []
        start_pos = (-718, 101, 118)

        target: Vehicle = None
        for i in range(3):
            offset = (i * 4, i * 5, 0)
            new_pos = tuple(x - y for x, y in zip(start_pos, offset))
            car_name = f"car_{i}"
            cam = self.bb.cam_setup(annotation=True)
            self.bb.with_car(vehicle_id=car_name, sensors={"camera": cam}, pos=new_pos),
            # rot_quat=(-1, 0, 0.3826834, 0.9238795))
            car = self.bb.get_vehicle(car_name)

            if i == 0:
                car.ai_set_mode(AIMode.RANDOM)
                car.ai_set_speed(99, "set")
                target = car
            else:
                if target is not None:
                    car.ai_set_mode(AIMode.CHASE)
                    car.ai_set_target(target.vid)
                    car.ai_set_speed(200, "limit")
                else:
                    print("Basic Car chase has no target")
            sequences_list.append(ImageSequence(us.data_path / "captures", car))

        self.sequences = sequences_list
