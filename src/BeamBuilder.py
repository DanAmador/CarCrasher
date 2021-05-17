from __future__ import annotations
import config
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Camera
from config import UserSettings as cfg
from config import Levels, Cars


class BeamBuilder:

    def __init__(self, launch=False, scenario_name="Beam Builder"):
        self.bmng = self.beam_factory(launch)
        self.scenario = None
        self.vehicles = {}
        self.ego_vehicle = None
        self.camera = None
        self.scenario_name = scenario_name
        self.meshes = []

    def build_environment(self, hud=False, steps=60, ai_mode=None):

        if not hud:
            self.bmng.hide_hud()

        if self.ego_vehicle is None:
            self.with_car()

        if self.camera is None:
            self.cam_setup()

        self.scenario.add_camera(self.camera, 'camera')

        self.bmng.set_steps_per_second(steps)

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

    def cam_setup(self, cam_pos=(0, -5, 2), cam_dir=(0, 1, -.3), colour=True, depth=False, annotation=False,
                  instance=False) -> Camera:
        self.camera = Camera(cam_pos, cam_dir, 75, (1920, 1080), near_far=(1, 100), colour=colour, depth=depth,
                             annotation=annotation, instance=instance)
        return self.camera

    def with_scenario(self, level: Levels = Levels.WEST_COAST, name: str = "example_scenario") -> BeamBuilder:
        scenario = Scenario(level, name)
        self.scenario = scenario
        return self

    def with_car(self, car: Cars = Cars.ETK, vehicle_id="ego", pos=(-717, 101, 118), rot=None,
                 rot_quat=(0, 0, 0.3826834, 0.9238795), sensors={}):
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
            self.scenario.add_vehicle(vehicle, pos=pos, rot=rot, rot_quat=rot_quat)

        if len(self.vehicles) == 0:
            self.ego_vehicle = vehicle

        self.vehicles[vehicle_id] = vehicle
        return self

    def get_vehicle(self, name: str = "ego") -> Vehicle:
        return self.vehicles.get(name, self.ego_vehicle)

    def assign_ego(self, name: str = "ego"):
        self.ego_vehicle = self.get_vehicle(name)


if __name__ == "__main__":
    bb = BeamBuilder(launch=True)
    bb.build_environment(ai_mode="span")
