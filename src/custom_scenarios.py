from abc import ABC, abstractmethod

from typing import List

from beamngpy import Vehicle

import BeamBuilder
from config import AIMode, Levels
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
    def setup_scenario(self, steps_per_sec=24):
        return []

    def create_sequences(self, car_list):
        sequences_list = []
        for car in car_list:
            sequences_list.append(ImageSequence(us.data_path / "beamng", car))

        self.sequences = sequences_list


class FallFromSkyScenario(AbstractRecordingScenario):

    def setup_scenario(self, steps_per_sec=24):
        import random
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        cam = self.bb.cam_setup(annotation=True)
        self.bb.with_car(pos=(0, 0, 50), rot=(random.randint(0, 360), random.randint(0, 360), random.randint(0, 360)),
                         sensors={"camera": cam})
        self.bb.build_environment(ai_mode="span", hud=True)

        self.create_sequences([self.bb.ego_vehicle])

    def on_recording_step(self):
        return


class BasicCarChase(AbstractRecordingScenario):

    def on_recording_step(self):
        pass

    def setup_scenario(self, steps_per_sec=24):

        self.bb.with_scenario(level=Levels.WEST_COAST)
        self.bb.build_environment(ai_mode="span", hud=True)
        sequences_list = []
        start_pos = (-718, 101, 118)

        target: Vehicle = None
        cars = []
        for i in range(3):
            offset = (i * 4, i * 5, 0)
            new_pos = tuple(x - y for x, y in zip(start_pos, offset))
            car_name = f"car_{i}"
            cam = self.bb.cam_setup(annotation=True)
            self.bb.with_car(vehicle_id=car_name, sensors={"camera": cam}, pos=new_pos),
            # rot_quat=(-1, 0, 0.3826834, 0.9238795))
            car = self.bb.get_vehicle(car_name)
            cars.append(car)
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

        self.create_sequences(cars)
