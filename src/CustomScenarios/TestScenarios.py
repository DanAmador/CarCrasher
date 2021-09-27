import random
from datetime import datetime

from beamngpy import Vehicle
from beamngpy.sensors import Lidar

from src.CustomScenarios.BaseScenarios import WithLidarView
from src.CustomScenarios.SceneData import SceneData
from src.config import AIMode, Levels
import numpy as np

from src.config import UserSettings as us
import json


class TestCrash(WithLidarView):

    def spawn_car_random_position(self, index) -> Vehicle:
        car_name = f"car_{index}"
        cam, _ = self.bb.cam_setup(annotation=True, first_person=True)

        vehicle = self.bb.with_car(vehicle_id=car_name, pos=(random.randint(-1, 360), random.randint(0, 360), 0),
                                   sensors={"camera": cam, "lidar": Lidar()})
        return vehicle

    def setup_scenario(self):
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
        return vehicles, []


class JsonLoaderScenarioTest(WithLidarView):
    def __init__(self, bb):
        super().__init__(bb)
        self.start_time = datetime.now()

    def setup_scenario(self) -> SceneData:
        test_json = {
            "level": Levels.INDUSTRIAL,
            "cars": [
                {
                    "car_id": "test_car",
                    "position": [-298.71, -146.55, 42.57, 0.0338056, -0.0305805, 0.670149, 0.740825],
                    "model": "etk800",
                    "ai": AIMode.DISABLED,
                    "max_speed": 300,
                    "first_person": True,
                    "cam": True
                }
            ],
            "cameras": [
                {
                    "position": [-284.10, -148.56, 49.99, 0.141861, 0.145246, -0.700493, 0.68417],
                    "fov": 50
                },
                {
                    "position": [-298.15, -132.80, 49.56, -0.00152505, -0.195584, 0.980656, -0.00764661],
                    "fov": 80
                },
                {
                    "position": [-298.15, -132.80, 49.56, -0.00152505, -0.195584, 0.980656, -0.00764661],
                    "fov": 10
                }
            ]
        }
        # position 1 euler =  -33.249096, -30.807463,132.597778
        sd = SceneData.load_json_scene(test_json, self.bb)
        return sd

    def should_record_predicate(self) -> bool:
        time_passed = datetime.now() - self.start_time
        return False
        return time_passed.seconds > 5


class FallFromSkyScenario(WithLidarView):

    def setup_scenario(self):
        import random
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        cam, _ = self.bb.cam_setup(annotation=True, first_person=True)
        vehicle = self.bb.with_car(pos=(0, 0, 50),
                                   rot=(random.randint(0, 360), random.randint(0, 360), random.randint(0, 360)),
                                   sensors={"camera": cam, "lidar": Lidar()})
        # self.make_camera_static(cam, vehicle, (0, -2, 10))

        self.bb.build_environment()
        return SceneData({vehicle.vid: vehicle}, [])


class StaticCameraTest(WithLidarView):

    def setup_scenario(self):
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        cam_tuple = self.bb.cam_setup(annotation=True, first_person=True, static_camera=True)
        cam_tuple2 = self.bb.cam_setup(annotation=True, first_person=True, static_camera=True)
        cam, _ = self.bb.cam_setup(annotation=True, first_person=True)
        vehicle = self.bb.with_car(pos=(1, 0, 0),
                                   rot=(0, 0, 0),
                                   sensors={"camera": cam, "lidar": Lidar()})
        # self.make_camera_static(cam, vehicle, (0, -2, 10))

        self.bb.build_environment()

        vehicle.ai_set_speed(200, "set")
        return SceneData({vehicle.vid: vehicle}, [cam_tuple])


class BasicCarChase(WithLidarView):

    def setup_scenario(self):

        self.bb.with_scenario(level=Levels.WEST_COAST)

        cam, _ = self.bb.cam_setup(annotation=True)
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
            cam, _ = self.bb.cam_setup(annotation=True)
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

        return SceneData({car.vid: car for car in cars}, [])


class PaperCompare(WithLidarView):
    def __init__(self, bb):
        super().__init__(bb)
        self.compare_list = []
        self.is_recording = False
        self.simulation_steps_per_frame = 1
        self.duration = 8
        self.predicate_distance = 150

    @staticmethod
    def get_json(first_person):
        return {
            "level": Levels.KONRAD,
            "cars": [
                {
                    "car_id": "crasher",
                    "position": [8.83, -574.10, 0.59, 0.00107191, -0.0308801, 0.998921, 0.0346746],
                    "model": "etk800",
                    "ai": AIMode.CHASE,
                    "max_speed": 300,
                    "first_person": first_person,
                    "cam": True
                },
                {
                    "car_id": "target",
                    "position": [1.30, -326.09, 0.71, 0.0187382, 0.0283661, -0.833902, 0.550864],
                    "model": "etk800",
                    "first_person": False,
                    "cam": True
                },
            ],

            "cameras": [

            ]
        }

    def should_record_predicate(self) -> bool:
        if len(self.compare_list) > 0 and not self.is_recording:
            sensor1 = self.compare_list[0].poll_sensors()
            sensor2 = self.compare_list[1].poll_sensors()
            if "state" in sensor1 and "state" in sensor2:
                state1 = sensor1["state"]["state"]
                state2 = sensor2["state"]["state"]
                if "pos" in state1 and "pos" in state2:
                    pos1 = np.array(state1["pos"])
                    pos2 = np.array(state2["pos"])
                    dist = np.linalg.norm(pos1 - pos2)
                    print(dist)
                    if dist < self.predicate_distance:
                        self.is_recording = True
                        return True
        return self.is_recording

    def setup_scenario(self) -> SceneData:
        sd = SceneData.load_json_scene(self.get_json(False), self.bb)
        crasher = sd.vehicles["crasher"]
        target = sd.vehicles["target"]
        crasher.ai_set_target(target.vid)
        self.compare_list = [crasher, target]
        return sd


class LoopScenario(WithLidarView):

    def __init__(self, bb):
        super().__init__(bb)
        self.duration = 25

    @staticmethod
    def get_json(first_person):
        return {
            "level": Levels.KONRAD,
            "cars": [
                {
                    "car_id": "looper",
                    "position": [6.62, -411.39, 0.78, 0.000163614, 0.00535084, 0.999518, -0.0305626],
                    "model": "etk800",
                    "ai": AIMode.MANUAL,
                    "max_speed": 300,
                    "first_person": first_person,
                    "cam": True
                },

            ],

            "cameras": [

            ]
        }

    @staticmethod
    def poly_script_from_points(poly):
        idx = 1
        axes = ["x", "y", "z"]
        ai_script = []
        for p in poly:
            entry = {}
            for axis, val in enumerate(p):
                if axis > 2:
                    break
                entry[axes[axis]] = val
            entry["t"] = idx * 4
            ai_script.append(entry)
            idx += 1
        return ai_script

    def setup_scenario(self) -> SceneData:
        # [9.57, -434.38, 1.54, 0.0140053],
        loop_positions = json.loads((us.json_path / "LoopScenario" / "loop_positions.json").read_text())
        ai_script = self.poly_script_from_points(loop_positions)
        points = [p[0:3] for p in loop_positions]
        print(points)
        self.bb.bmng.add_debug_polyline(points, rgba_color=(1, 1, .6, 1), cling=True)
        self.bb.bmng.add_debug_spheres(points, radii=[1 for p in points], rgba_colors=[(idx/len(p), idx/len(p), idx/len(p), 1) for idx,p in enumerate(points)],
                                       cling=True)
        sd = SceneData.load_json_scene(self.get_json(True), self.bb)
        looper = sd.vehicles["looper"]
        looper.ai_set_script(ai_script, cling=True)

        return sd
