from datetime import datetime

from src.CustomScenarios.BaseScenarios import WithLidarView
from src.CustomScenarios.SceneData import SceneData
from src.config import Levels
from src.config import UserSettings as us
import json


class FirstScenario(WithLidarView):
    def __init__(self, bb):
        super().__init__(bb)
        self.start_time = datetime.now()

    @staticmethod
    def poly_script_from_points(poly, speed):
        idx = 1
        for p in poly:
            p["t"] = idx * speed
            idx +=1
        return poly

    def setup_scenario(self) -> SceneData:
        scenario_path = us.json_path / "first_scenario"
        sd, jay = SceneData.from_json_file(scenario_path / "scene_description.json", self.bb)
        lane_names = ["central", "left", "right"]

        lanes = {
            lane: FirstScenario.poly_script_from_points(json.loads((scenario_path / f"{lane}_lane.json").read_text()), 8)
            for lane in lane_names}
        # position 1 euler = -2.391787, 3.153309,52.855541
        #
        #
        # for car in jay["cars"]:
        #     if "lane" in car:
        #         print("Ayyy lmao")
        #         lane = lanes.get(car["lane"], None)
        #         print(lane)
        #         vehicle = sd.vehicles[car["car_id"]]
        #         vehicle.ai_set_script(lane, False)

        return sd
