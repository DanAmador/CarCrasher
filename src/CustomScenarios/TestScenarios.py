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
            "level": "Industrial",
            "cars": [
                #{
                #    "car_id": "test_car",
                #    "position": [4.40, -355.40, 1.01, 0.0182628, -0.000119876, 0.00656274, 0.999812],
                #    "model": "etk800",
                #    "ai": "span",
                #    "max_speed": 300,
                #    "first_person": True
                #},
                {
                    "car_id": "police_back_right",
                    "position": [-383.54, -112.78, 42.34, 0.0142582, -0.0141653, 0.704651, 0.70927],
                    "model": "etk800",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "police_back_left",
                    "position": [-383.56, -109.81, 42.34, 0.0142582, -0.0141653, 0.704651, 0.70927],
                    "model": "etk800",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "police_front_right",
                    "position": [-308.98, -114.53, 41.96, -0.000485358, 0.000511862, 0.725644, 0.68807],
                    "model": "etkc",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "police_front_left",
                    "position": [-308.78, -110.63, 41.75, 0.00781297, -0.00737831, 0.686554, 0.726999],
                    "model": "etkc",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "oldtimner",
                    "position": [-303.60, -113.25, 41.61, -0.000504249, 0.000493366, 0.699351, 0.714778],
                    "model": "Serpent Beverly Sedan 1959",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "orange_van_front_left",
                    "position": [-320.13, -110.92, 43.24, 0.0520454, -0.0464531, 0.664266, 0.744234],
                    "model": "van",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "orange_van_front_right",
                    "position": [-319.83, -114.49, 42.98, 0.0260095, -0.0259837, 0.706278, 0.706979],
                    "model": "van",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "white_van",
                    "position": [-330.48, -113.98, 42.77, 0.0259258, -0.0260442, 0.708237, 0.705017],
                    "model": "van",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "murica_truck",
                    "position": [-332.35, -109.85, 43.52, 0.088969, -0.0917006, 0.711833, 0.690629],
                    "model": "semi",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "van_truck_left",
                    "position": [-341.54, -109.74, 43.05, 0.00240331, -0.0024651, 0.716019, 0.698072],
                    "model": "van",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "van_truck_right",
                    "position": [-341.65, -113.45, 43.05, 0.0250068, -0.02549, 0.713384, 0.699863],
                    "model": "van",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "orange_truck_back_left",
                    "position": [-351.00, -109.75, 42.65, 0.0269897, -0.0279153, 0.718383, 0.694564],
                    "model": "van",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "orange_truck_back_right",
                    "position": [-350.75, -113.62, 42.57, 0.0295953, -0.0297306, 0.708095, 0.70487],
                    "model": "van",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "first_google_car",
                    "position": [-256.28, -106.18, 41.35, 0.0197539, -0.100565, 0.976082, 0.191731],
                    "model": "2010 Dopel Imperium EcoTec",
                    "ai": "disabled",
                    "max_speed": 0,
                    "first_person": True
                },
                {
                    "car_id": "second_google_car",
                    "position": [-213.34, -10.10, 40.60, 0.0345355, -0.0142065, 0.380164, 0.924165],
                    "model": "2010 Dopel Imperium EcoTec",
                    "ai": "disabled",
                    "max_speed": 0,
                    "first_person": True
                }
            ],
            "cameras": [
                # {
                #     "position": [13.78, -53.91, 8.90, 0.15007, 0.020832, -0.135909, 0.979068]
                # },
                # {
                #     "position": [-334.97, 290.03, 113.97, 0.126316, 0.142928, -0.735552, 0.650061]
                # }

                #Actual Cameras. just commented out for now
                #Initial Shot1
                # {
                #     "position": [-238.73, -89.77, 66.70, -0.12936, -0.24496, 0.849666, -0.448697]
                # }
                #Initial Shot2... yes there are 2 of them, but anton s going to edit so whatevs...
                # {
                #     "position": [-241.75, -120.30, 55.37, 0.142871, 0.0873563, -0.514284, 0.841112]
                # }
                #second shot (with google car?)
                # {
                #     "position": [-258.25, -105.68, 42.58, 0.0113626, -0.0385524, 0.958431, 0.282479]
                # }
                #third shot
                # {
                #     "position": [-224.80, 44.95, 72.62, 0.046881, -0.210012, 0.953115, 0.212764]
                # }
                # last shot
                # {
                #     "position": [-334.89, 274.13, 55.78, 0.148702, -0.0178154, 0.117614, 0.981701]
                # }
                # fourth shot (with google car)
                # {
                #     "position": [-219.52, -8.03, 40.56, -0.0220088, 0.015967, 0.587006, 0.809126]
                # }
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
