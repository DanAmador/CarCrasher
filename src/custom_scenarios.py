from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import List, Tuple

from beamngpy import Vehicle
from beamngpy.sensors import Camera, Lidar

import BeamBuilder
from config import AIMode, Levels
from recorder import ImageSequence
from config import UserSettings as us
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import random


@dataclass(unsafe_hash=True)
class StaticCamera:
    camera: Camera
    vehicle: Vehicle
    world_pos: np.array
    look_at: np.array

    def __init__(self, cam: Camera, vehicle: Vehicle, world_start_pos: Tuple[float, float, float]):
        self.camera = cam
        self.vehicle = vehicle
        self.start_pos = np.array(cam.pos)
        self.world_pos = np.array(world_start_pos)
        # self.look_at = cam.direction

    def update_position(self):
        vehicle_pos = np.array(self.vehicle.state["pos"])
        # new_pos = tuple(x - y for x, y in zip(vehicle_pos, self.world_pos))
        new_pos = self.world_pos - vehicle_pos
        print(f"{vehicle_pos} - {self.world_pos} = {new_pos}")
        # print(f"{vehicle_pos} - {self.world_pos} -  {self.start_pos}")
        self.camera.pos = new_pos
        cam_dir = new_pos / np.linalg.norm(new_pos)
        # print(cam_dir)
        self.camera.direction = cam_dir
        # self.camera.direction = (1,0,0)


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
            sequences_list.append(ImageSequence(us.data_path, car))

        self.sequences = sequences_list

    # def make_camera_static(self, camera, vehicle, world_pos):
    #     sc = StaticCamera(camera, vehicle, world_pos)
    #     self.static_cameras.append(sc)
    #


class WithLidarView(AbstractRecordingScenario):

    def __init__(self, bb):
        from beamngpy.visualiser import LidarVisualiser
        super().__init__(bb)
        self.lidar_vis = LidarVisualiser(Lidar.max_points)
        # self.lidar_vis.open(SIZE, SIZE)

        # glutReshapeFunc(self.lidar_resize)

    @staticmethod
    def lidar_resize(width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)

    @staticmethod
    def open_window(width, height):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(width, height)
        window = glutCreateWindow(b'Lidar Tour')
        WithLidarView.lidar_resize(width, height)
        return window


class TestCrash(WithLidarView):

    def spawn_car_random_position(self, index) -> Vehicle:
        car_name = f"car_{index}"
        cam = self.bb.cam_setup(annotation=True, first_person=True)

        vehicle = self.bb.with_car(vehicle_id=car_name, pos=(random.randint(-1, 360), random.randint(0, 360), 0),
                                   sensors={"camera": cam, "lidar": Lidar()})
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


class FallFromSkyScenario(WithLidarView):

    def on_recording_step(self):
        pass

    def setup_scenario(self, steps_per_sec=24):
        import random
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        cam = self.bb.cam_setup(annotation=True, first_person=True)
        vehicle = self.bb.with_car(pos=(0, 0, 50),
                                   rot=(random.randint(0, 360), random.randint(0, 360), random.randint(0, 360)),
                                   sensors={"camera": cam, "lidar": Lidar()})
        # self.make_camera_static(cam, vehicle, (0, -2, 10))

        self.bb.build_environment()
        self.create_sequences([self.bb.ego_vehicle])


class CameraMatrixTest(WithLidarView):

    def on_recording_step(self):
        pass

    def setup_scenario(self, steps_per_sec=24):
        import random
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        cam = self.bb.cam_setup(annotation=True, first_person=True)
        vehicle = self.bb.with_car(pos=(1, 0, 0),
                                   rot=(0, 0, 0),
                                   sensors={"camera": cam, "lidar": Lidar()})
        # self.make_camera_static(cam, vehicle, (0, -2, 10))

        self.bb.build_environment()
        self.create_sequences([self.bb.ego_vehicle])


class BasicCarChase(WithLidarView):

    def on_recording_step(self):
        pass

    def setup_scenario(self, steps_per_sec=24):

        self.bb.with_scenario(level=Levels.WEST_COAST)

        cam = self.bb.cam_setup(annotation=True)
        self.bb.with_car(vehicle_id="ego", sensors={"camera": cam, "lidar": Lidar()}, rot=(0, 0, 180)),
        self.bb.build_environment(ai_mode="span", hud=True)

        start_pos = [(-741.79, 80.56, 119.13), (-667.98, 154.64, 117.40)]

        target: Vehicle = self.bb.ego_vehicle
        cars = []
        num_cars = 3
        cars.append(target)

        target.ai_set_mode(AIMode.SPAN)
        target.ai_set_speed(99, "set")
        for i in range(num_cars):

            offset = tuple((x - y) for x, y in zip(start_pos[0], start_pos[1]))
            # offset= (40,10,0)
            new_pos = tuple(x + (y / num_cars) for x, y in zip(start_pos[1], offset))
            car_name = f"car_{i}"
            cam = self.bb.cam_setup(annotation=True)
            self.bb.with_car(vehicle_id=car_name, sensors={"camera": cam, "lidar": Lidar()}, pos=new_pos,
                             rot=(0, 0, 180)),
            # rot_quat=(-1, 0, 0.3826834, 0.9238795))
            car = self.bb.get_vehicle(car_name)
            cars.append(car)

            if target is not None:
                car.ai_set_mode(AIMode.CHASE)
                car.ai_set_target(target.vid)
                car.ai_set_speed(200, "limit")
            else:
                print(f"Basic Car {i}  has no target")

        self.create_sequences(cars)
