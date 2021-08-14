import random
from typing import Tuple, List

from beamngpy import Vehicle
from beamngpy.sensors import Lidar, Camera

from src.CustomScenarios.BaseScenarios import WithLidarView
from src.CustomScenarios.SceneData import SceneData
from src.config import AIMode, Levels
from datetime import datetime


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
        super(JsonLoaderScenarioTest, self).__init__(bb)
        self.start_time = datetime.now()

    def setup_scenario(self) -> SceneData:
        test_json = {
            "level": "smallgrid",
            "cars": [
                {
                    "car_id": "test_car",
                    "position": [59.03, 86.14, 3.05, 0.0189849, -0.00283056, 0.147438, 0.988885],
                    "model": "etk800",
                    "ai": "span",
                    "max_speed": 300,
                    "first_person": True
                }
            ],
            "cameras": [
                # {
                #     "position": [49.60, 90.78, 6.16, 0.137144, -0.187947, 0.785636, 0.573275],
                #     "fov": 50
                # },
                {
                    "position": [60.19, 78.05, 7.42, 0.375808, 0.0165959, -0.040877, 0.925647],
                    "fov": 80
                }
            ]
        }
        # position 1 euler =  -33.249096, -30.807463,132.597778
        sd = SceneData.load_json_scene(test_json, self.bb)
        return sd

    def should_record_predicate(self) -> bool:
        time_passed = datetime.now() - self.start_time
        return time_passed.seconds > 5


class FallFromSkyScenario(WithLidarView):

    def on_recording_step(self):
        pass

    def setup_scenario(self):
        import random
        self.bb.with_scenario(level=Levels.SMALL_GRID)

        cam, _ = self.bb.cam_setup(annotation=True, first_person=True)
        vehicle = self.bb.with_car(pos=(0, 0, 50),
                                   rot=(random.randint(0, 360), random.randint(0, 360), random.randint(0, 360)),
                                   sensors={"camera": cam, "lidar": Lidar()})
        # self.make_camera_static(cam, vehicle, (0, -2, 10))

        self.bb.build_environment()
        return SceneData([vehicle], [])


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
        return SceneData([vehicle], [cam_tuple])


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

        return SceneData(cars, [])
