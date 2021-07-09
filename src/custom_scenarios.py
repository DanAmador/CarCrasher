from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import List, Tuple

from beamngpy import Vehicle
from beamngpy.sensors import Camera

import BeamBuilder
from config import AIMode, Levels
from recorder import ImageSequence
from config import UserSettings as us

import numpy as np

import random


#
# @dataclass(unsafe_hash=True)
# class StaticCamera:
#     camera: Camera
#     vehicle: Vehicle
#     world_pos: np.array
#     look_at: np.array
#
#     def __init__(self, cam: Camera, vehicle: Vehicle, world_start_pos: Tuple[float, float, float]):
#         self.camera = cam
#         self.vehicle = vehicle
#         self.start_pos = np.array(cam.pos)
#         self.world_pos = np.array(world_start_pos)
#         # self.look_at = cam.direction
#
#     def update_position(self):
#         vehicle_pos = np.array(self.vehicle.state["pos"])
#         # new_pos = tuple(x - y for x, y in zip(vehicle_pos, self.world_pos))
#         new_pos = self.world_pos - vehicle_pos
#         print(f"{vehicle_pos} - {self.world_pos} = {new_pos}")
#         # print(f"{vehicle_pos} - {self.world_pos} -  {self.start_pos}")
#         self.camera.pos = new_pos
#         cam_dir = new_pos / np.linalg.norm(new_pos)
#         # print(cam_dir)
#         self.camera.direction = cam_dir
#         # self.camera.direction = (1,0,0)


class AbstractRecordingScenario(ABC):

    def __init__(self, bb: BeamBuilder):
        self.bb = bb
        self.sequences = []
        self.static_cameras = []
        self.setup_scenario()

    @abstractmethod
    def on_recording_step(self):
        for static_camera in self.static_cameras:
            static_camera.update_position()
            # self.bb.bmng.add_debug_spheres(tuple([float(a) for a in static_camera.camera.pos]),(5,5,5),(1,1,1))
        return

    @abstractmethod
    def setup_scenario(self, steps_per_sec=24):
        return []

    def create_sequences(self, car_list):
        sequences_list = []
        for car in car_list:
            sequences_list.append(ImageSequence(us.data_path / "beamng", car))

        self.sequences = sequences_list

    # def make_camera_static(self, camera, vehicle, world_pos):
    #     sc = StaticCamera(camera, vehicle, world_pos)
    #     self.static_cameras.append(sc)
    #


class TestCrash(AbstractRecordingScenario):
    def on_recording_step(self):
        return

    def spawn_car_random_position(self, index) -> Vehicle:
        car_name = f"car_{index}"
        cam = self.bb.cam_setup(annotation=True, first_person=True)

        vehicle = self.bb.with_car(vehicle_id=car_name, pos=(random.randint(-1, 360), random.randint(0, 360), 0),
                                   sensors={"camera": cam})
        return vehicle

    def setup_scenario(self, steps_per_sec=24):
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        # self.make_camera_static(cam, vehicle, (0, -2, 10))
        self.bb.build_environment(ai_mode="span", hud=True)
        vehicles = [self.spawn_car_random_position(n) for n in range(4)]
        print(vehicles)

        for idx, car in enumerate(vehicles):
            target_idx = 1
            if idx == 1:
                continue
            car.ai_set_mode(AIMode.CHASE)
            car.ai_set_target(vehicles[target_idx].vid)
            print(f"setting {vehicles[target_idx].vid} as target for {idx}")
            car.ai_set_speed(200, "limit")
        self.create_sequences(vehicles)


class FallFromSkyScenario(AbstractRecordingScenario):

    def setup_scenario(self, steps_per_sec=24):
        import random
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        cam = self.bb.cam_setup(annotation=True, first_person=True)
        vehicle = self.bb.with_car(pos=(0, 0, 50),
                                   rot=(random.randint(0, 360), random.randint(0, 360), random.randint(0, 360)),
                                   sensors={"camera": cam})
        # self.make_camera_static(cam, vehicle, (0, -2, 10))

        self.bb.build_environment()
        self.create_sequences([self.bb.ego_vehicle])

    def on_recording_step(self):
        super().on_recording_step()
        return


class BasicCarChase(AbstractRecordingScenario):

    def on_recording_step(self):
        pass

    def setup_scenario(self, steps_per_sec=24):

        self.bb.with_scenario(level=Levels.WEST_COAST)
        self.bb.build_environment(ai_mode="span", hud=True)

        start_pos = [(-741.79, 80.56, 119.13), (-667.98, 154.64, 117.40)]

        target: Vehicle = None
        cars = []
        num_cars = 3
        for i in range(num_cars):

            offset = tuple((x - y) for x, y in zip(start_pos[0], start_pos[1]))
            # offset= (40,10,0)
            new_pos = tuple(x + (y / num_cars) for x, y in zip(start_pos[1], offset))
            car_name = f"car_{i}"
            cam = self.bb.cam_setup(annotation=True)
            self.bb.with_car(vehicle_id=car_name, sensors={"camera": cam}, pos=new_pos),
            # rot_quat=(-1, 0, 0.3826834, 0.9238795))
            car = self.bb.get_vehicle(car_name)
            cars.append(car)
            if i == 1:
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

