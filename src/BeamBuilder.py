from __future__ import annotations

from typing import Tuple

import config
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Camera, Lidar
from config import UserSettings as cfg
from config import Levels, Cars


class BeamBuilder:

    def __init__(self, launch=False, scenario_name="Beam Builder", steps_per_sec=60):
        self.bmng = self.beam_factory(launch)
        self.scenario = None
        self.vehicles = {}
        self.ego_vehicle = None
        self.scenario_name = scenario_name
        self.meshes = []
        self.steps_per_second = steps_per_sec

    def build_environment(self, hud=False, ai_mode=None):

        if not hud:
            self.bmng.hide_hud()

        if self.ego_vehicle is None:
            cam, _ = self.cam_setup()
            self.with_car(sensors={"camera": cam, "lidar": Lidar()})

        self.bmng.set_steps_per_second(self.steps_per_second)

        self.scenario.make(self.bmng)
        # self.meshes = self.scenario.find_procedural_meshes()

        self.bmng.set_deterministic()
        self.bmng.load_scenario(self.scenario)
        self.bmng.start_scenario()

        if ai_mode is not None:
            print(f"Setting ai mode {ai_mode}")
            self.ego_vehicle.ai_set_mode(mode=ai_mode)
        # self.bmng.close()

    @staticmethod
    def beam_factory(launch=False) -> BeamNGpy:
        bmng = BeamNGpy('localhost', 64256, home=cfg.beam_tech_path, user=cfg.user_path)
        bmng.open(launch=launch)
        return bmng

    def cam_setup(self, cam_pos=(0, -5, 2), cam_dir=(0, 1, -.3), colour=True, depth=True, annotation=True,
                  instance=True, first_person=False, static_camera= False) -> Tuple[Camera, str]:
        if first_person:
            cam_pos = (0, 2, 2)
        camera = Camera(cam_pos, cam_dir, 75, (1920, 1080), near_far=(1, 50), colour=colour, depth=depth,
                        annotation=annotation, instance=instance,
                        # depth_inverse=True
                        )

        cam_name = None
        if static_camera:
            cam_name = f"camera_{len(self.scenario.cameras.keys())}"
            self.scenario.add_camera(camera, cam_name)
        return camera, cam_name

    def with_scenario(self, level: Levels = Levels.WEST_COAST, name: str = "example_scenario") -> BeamBuilder:
        scenario = Scenario(level, name)
        self.scenario = scenario
        return self

    def with_car(self, car: Cars = Cars.ETK, vehicle_id="car", pos=(-717, 101, 118), rot=None,
                 rot_quat=(0, 0, 0.3826834, 0.9238795), sensors=None):
        if sensors is None:
            sensors = {}
        vehicle = Vehicle(vehicle_id, model=car, licence='AntonGinzburg')

        while vehicle_id in self.vehicles.keys():
            repeated = [x for x in self.vehicles.keys() if x.find(vehicle_id) != -1]
            vehicle_id = f"{vehicle_id}_{len(repeated)}"

        for sensor_name, sensor in sensors.items():
            print(f"Attaching {sensor_name} to {vehicle_id}")
            vehicle.attach_sensor(name=sensor_name, sensor=sensor)


        if self.scenario is None:
            print("No scenario defined while building vehicle, building default")
            self.with_scenario(Levels.WEST_COAST, name=self.scenario_name)
        else:
            if rot is not None:
                rot_quat = None
            self.scenario.add_vehicle(vehicle, pos=pos, rot=rot, rot_quat=rot_quat)

        if len(self.vehicles) == 0:
            self.ego_vehicle = vehicle

        self.vehicles[vehicle_id] = vehicle
        return vehicle

    def get_vehicle(self, name: str = "ego") -> Vehicle:
        return self.vehicles.get(name, self.ego_vehicle)

    def assign_ego(self, name: str = "ego"):
        self.ego_vehicle = self.get_vehicle(name)


if __name__ == "__main__":
    bb = BeamBuilder(launch=True)
    # bb.build_environment(ai_mode="span")
