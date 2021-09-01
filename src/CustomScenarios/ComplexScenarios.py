from datetime import datetime

from src.CustomScenarios.BaseScenarios import WithLidarView
from src.CustomScenarios.SceneData import SceneData
from src.config import Levels


class FirstScenario(WithLidarView):
    def __init__(self, bb):
        super().__init__(bb)
        self.start_time = datetime.now()

    def setup_scenario(self) -> SceneData:
        test_json = {
            "level": Levels.INDUSTRIAL,
            "cars": [
                {
                    "car_id": "police_back_right",
                    "position": [-383.54, -112.78, 42.34, -0.00372912, -0.00315651, -0.646066, 0.763266],
                    "model": "etk800",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True,
                    "cam": True
                },
                {
                    "car_id": "police_back_left",
                    "position": [-383.56, -109.81, 42.34, 0.00477008, 0.00451204, -0.687169, 0.726468],
                    "model": "etk800",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "police_front_right",
                    "position": [-308.98, -114.53, 41.96, -0.00729508, -0.00694865, -0.68967, 0.724054],
                    "model": "etkc",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "police_front_left",
                    "position": [-308.78, -110.63, 41.75, -0.0103203, -0.00980974, -0.688881, 0.724734],
                    "model": "etkc",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                    "car_id": "oldie",
                    "position": [-303.60, -113.25, 41.61, -0.0139384, -0.0135561, -0.697076, 0.716734],
                    "model": "oldtimer",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                     "car_id": "orange_once_van_front_left",
                     "position": [-320.13, -110.92, 43.24, 0.0211522, 0.0201477, -0.689412, 0.723781],
                     "model": "van",
                     "ai": "span",
                     "max_speed": 40,
                     "first_person": True
                },
                {
                     "car_id": "orange_once_van_front_right",
                     "position": [-319.83, -114.49, 42.98, 0.0101612, 0.00943942, -0.680541, 0.732579],
                     "model": "van",
                     "ai": "span",
                     "max_speed": 40,
                     "first_person": True
                },
                {
                     "car_id": "flatbed_truck",
                     "position": [-330.48, -113.98, 42.77, 0.000235508, 0.000215754, -0.675506, 0.737354],
                     "model": "van",
                     "ai": "span",
                     "max_speed": 40,
                     "first_person": True
                },
                {
                    "car_id": "murica_truck",
                    "position": [-332.35, -109.85, 43.52, 0.0245456, 0.0241223, -0.700515, 0.712807],
                    "model": "semi",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                {
                     "car_id": "van_truck_left",
                     "position": [-341.54, -109.74, 43.05, 0.00829754, 0.00834913, -0.709246, 0.704863],
                     "model": "van",
                     "ai": "span",
                     "max_speed": 40,
                     "first_person": True
                },
                {
                     "car_id": "van_truck_right",
                     "position": [-341.65, -113.45, 43.05, 0.0206972, 0.0194828, -0.685145, 0.727852],
                     "model": "van",
                     "ai": "span",
                     "max_speed": 40,
                     "first_person": True
                },
                {
                     "car_id": "orange_once_truck_back_left",
                     "position": [-351.00, -109.75, 42.65, 0.0118151, 0.0121893, -0.717941, 0.695897],
                     "model": "van",
                     "ai": "span",
                     "max_speed": 40,
                     "first_person": True
                },
                {
                     "car_id": "orange_once_truck_back_right",
                     "position": [-350.75, -113.62, 42.57, 0.0123366, 0.0116612, -0.686835, 0.726615],
                     "model": "van",
                     "ai": "span",
                     "max_speed": 40,
                     "first_person": True
                },
                {
                     "car_id": "first_google_car",
                     "position": [-256.28, -106.18, 41.35, -0.00237524, -0.000715758, -0.288525, 0.957469],
                     "model": "dopel",
                     "ai": "disabled",
                     "max_speed": 0,
                     "first_person": True
                },
                {
                     "car_id": "second_google_car",
                     "position": [-213.34, -10.10, 40.60, -0.00163257, -0.00421831, 0.932583, -0.360927],
                     "model": "dopel",
                     "ai": "disabled",
                     "max_speed": 0,
                     "first_person": True
                },
                {
                    "car_id": "maybachtest",
                    "position": [-290.78, -110.63, 41.75, -0.0103203, -0.00980974, -0.688881, 0.724734],
                    "model": "maybach",
                    "ai": "span",
                    "max_speed": 40,
                    "first_person": True
                },
                #Props
                {
                    "car_id": "proptest",
                    "position": [-367.88, -110.81, 42.51, 0.00665086, -0.00706784, 0.728229, 0.685265],
                    "model": "Aphrodite",
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

                # Actual Cameras. just commented out for now
                # Initial Shot1
                # {
                #   "position": [-238.73, -89.77, 66.70, -0.12936, -0.24496, 0.849666, -0.448697]
                # }
                # Initial Shot2... yes there are 2 of them, but anton s going to edit so whatevs...
                # {
                #     "position": [-241.75, -120.30, 55.37, 0.142871, 0.0873563, -0.514284, 0.841112]
                # }
                # second shot (with google car?)
                # {
                #     "position": [-258.25, -105.68, 42.58, 0.0113626, -0.0385524, 0.958431, 0.282479]
                # }
                # third shot
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
        # position 1 euler = -2.391787, 3.153309,52.855541
        sd = SceneData.load_json_scene(test_json, self.bb)
        return sd
