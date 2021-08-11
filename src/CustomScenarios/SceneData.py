from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from beamngpy import Vehicle
from beamngpy.sensors import Camera, Lidar

from src.BeamBuilder import BeamBuilder
from src.Recording.Sequence import CarSequence, StaticCamSequence
from src.config import UserSettings as us
from src.util import quaternion_to_euler_vec


@dataclass
class SceneData:
    vehicles: List[Vehicle]
    static_cameras: List[Tuple[Camera, str]]

    def get_sequence_list(self):
        sequences = []
        sequences.extend([CarSequence(us.data_path, car) for car in self.vehicles])
        sequences.extend([StaticCamSequence(us.data_path, cam, cam_id) for cam, cam_id in self.static_cameras])
        return sequences

    @staticmethod
    def from_json_file(json_path: Path, bb: BeamBuilder) -> SceneData:
        if json_path.exists():
            jay = json.loads(json_path.read_text())
            return SceneData.load_json_scene(jay, bb)
        else:
            print(f"{json_path} does not exist ")

    @staticmethod
    def load_json_scene(json_dict, bb: BeamBuilder) -> SceneData:
        def parse_bmng_pos(bmng_pos):
            return bmng_pos[:3], bmng_pos[-4:]

        bb.with_scenario(level=json_dict["level"])
        cars = []
        cams = []
        cars_dict = {}
        for car in json_dict["cars"]:
            cam, _ = bb.cam_setup(first_person=True if "first_person" in car else False)
            car_name = car["car_id"]
            model = car["model"]
            pos, rot_quat = parse_bmng_pos(car["position"])
            sensors = {'camera': cam}
            if "lidar" in car:
                sensors["lidar"] = Lidar()

            vehicle: Vehicle = bb.with_car(vehicle_id=car_name, model=model, pos=pos, rot=rot_quat, sensors=sensors)
            cars_dict[car_name] = vehicle

            cars.append(vehicle)

        for static_cam in json_dict["cameras"]:
            pos, rot_quat = parse_bmng_pos(static_cam["position"])
            cam_dir = quaternion_to_euler_vec(*rot_quat)
            print(f"quat {rot_quat} --- angle: {cam_dir}")
            cam_tup = bb.cam_setup(static_camera=True, cam_pos=pos, cam_dir=cam_dir)
            cams.append(cam_tup)
        bb.build_environment()
        for car in json_dict["cars"]:
            vehicle = cars_dict[car["car_id"]]
            if "ai" in car:
                vehicle.ai_set_mode(car["ai"])
                if "max_speed" in car:
                    vehicle.ai_set_speed(car["max_speed"], "set")
        return SceneData(cars, cams)
