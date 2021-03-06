from __future__ import annotations

from typing import Tuple

import config
from beamngpy import BeamNGpy, Scenario, Vehicle, angle_to_quat
from beamngpy.sensors import Camera, Lidar
from config import UserSettings as cfg
from config import Levels, Cars


class BeamBuilder:

    def __init__(self, launch=False, scenario_name="Beam Builder"):
        self.bmng = self.beam_factory(launch)
        self.scenario = None
        self.vehicles = {}
        self.ego_vehicle = None
        self.scenario_name = scenario_name

    def build_environment(self, hud=False, ai_mode=None):

        if not hud:
            self.bmng.hide_hud()

        if self.ego_vehicle is None:
            cam, _ = self.cam_setup()
            self.with_car(sensors={"camera": cam, "lidar": Lidar()})

        self.scenario.make(self.bmng)

        self.bmng.set_deterministic()
        self.bmng.load_scenario(self.scenario)
        self.bmng.start_scenario()

        if ai_mode is not None:
            print(f"Setting ai mode {ai_mode}")
            self.ego_vehicle.ai_set_mode(mode=ai_mode)
        print("Environment has been built")
        self.bmng.resume()
        # self.bmng.close()

    @staticmethod
    def beam_factory(launch=False) -> BeamNGpy:
        bmng = BeamNGpy('localhost', 64256, home=cfg.beam_tech_path, user=cfg.user_path)
        bmng.open(launch=launch)
        return bmng

    def cam_setup(self, cam_pos=(0, -5, 2), cam_dir=(0, 1, -.3), colour=True, depth=True, annotation=True,
                  instance=True, first_person=False, static_camera=False, fov=50) -> Tuple[Camera, str]:
        if first_person:
            cam_pos = (0, 2, 1.8)
            cam_dir = (0, 1, 0)
        camera = Camera(cam_pos, cam_dir, fov, (1024, 512), colour=colour, depth=depth,
                        annotation=annotation, instance=instance,
                        # depth_inverse=True
                        )

        cam_name = None
        if static_camera:
            cam_name = f"static_camera_{len(self.scenario.cameras.keys())}"
            self.scenario.add_camera(camera, cam_name)
        return camera, cam_name

    def with_scenario(self, level: Levels = Levels.WEST_COAST, name: str = "example_scenario") -> BeamBuilder:
        scenario = Scenario(level, name)
        self.scenario = scenario
        return self

    def with_car(self, model: Cars = Cars.ETK, vehicle_id="car", pos=(-717, 101, 118), rot=None,
                 rot_quat=(0, 0, 0.3826834, 0.9238795), sensors=None, cling=True, confg=None):
        if sensors is None:
            sensors = {}
        vehicle = Vehicle(vehicle_id, model=model, licence='AntonGinzburg')

        while vehicle_id in self.vehicles.keys():
            repeated = [x for x in self.vehicles.keys() if x.find(vehicle_id) != -1]
            vehicle_id = f"{vehicle_id}_{len(repeated)}"



        for sensor_name, sensor in sensors.items():
            print(f"Attaching {sensor_name} to {vehicle_id}")
            vehicle.attach_sensor(name=sensor_name, sensor=sensor)

        if self.scenario is None:
            print("No scenario defined while building vehicle, building default")
            self.with_scenario(Levels.SMALL_GRID, name=self.scenario_name)
        else:
            if rot is not None:
                rot_quat = angle_to_quat(rot)
            self.scenario.add_vehicle(vehicle, pos=pos, rot_quat=rot_quat, cling=cling)
        if confg:
            self.bmng.set_part_config(vehicle, confg)
        if len(self.vehicles) == 0:
            self.ego_vehicle = vehicle
        # if confg is not None and vehicle is not None:
        #    print("Before call")
        #    print(self.bmng)
        #    self.bmng.set_part_config(vehicle, confg)
        #    print("After call")
        self.vehicles[vehicle_id] = vehicle
        return vehicle

    def get_vehicle(self, name: str = "ego") -> Vehicle:
        return self.vehicles.get(name, self.ego_vehicle)

    def assign_ego(self, name: str = "ego"):
        self.ego_vehicle = self.get_vehicle(name)


if __name__ == "__main__":
    bb = BeamBuilder(launch=True)
    # bb.build_environment(ai_mode="span")
