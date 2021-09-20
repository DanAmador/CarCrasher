import json
from datetime import datetime

from src.CustomScenarios.BaseScenarios import WithLidarView
from src.CustomScenarios.SceneData import SceneData
from src.config import UserSettings as us


class FirstScenario(WithLidarView):
    def __init__(self, bb):
        super().__init__(bb)
        self.start_time = datetime.now()
        self.framerate = 30
        self.duration = 90
        self.simulation_steps_per_frame = 3

    @staticmethod
    def poly_script_from_points(poly, speed):
        old = 0
        for p in poly:
            print(p)
            val = p.get('t')
            print(val)
            p.update({'t': old + val * speed})
            old = old + val * speed
        return poly

    @staticmethod
    def apply_offset(poly, offset):
        for p in poly:
            val = p.get('t')
            p.update({'t': val + offset})
        return poly

    def setup_scenario(self) -> SceneData:
        scenario_path = us.json_path / "first_scenario"
        sd, jay = SceneData.from_json_file(scenario_path / "final_scene_description.json", self.bb)
        lane_names = ["central", "left", "right"]

        lanes = {
            lane: FirstScenario.poly_script_from_points(json.loads(
                (scenario_path / f"final_lane_{lane}.json").read_text()), 2)for lane in lane_names}
        self.bb.bmng.pause()

        # position 1 euler = -2.391787, 3.153309,52.855541
        #
        #
        #axes = ["x", "y", "z"]
        #for idx, l in enumerate(lanes.values()):
        #    points = [[s[axes[p]] for p in range(3)] for s in l]
        #    lane_color = idx / 3
        #    self.bb.bmng.add_debug_spheres(points, radii=[1 for p in points],
        #                                   rgba_colors=[(lane_color, lane_color, lane_color,1) for p in points])
        #    self.bb.bmng.add_debug_polyline(points, rgba_color=(lane_color, lane_color, lane_color, 1), cling=True)

        #this part works, but we need to wait until it is loaded in
        for car in jay["cars"]:
            if "parts" in car:
                vehicle = sd.vehicles[car["car_id"]]
                vehicle.set_part_config(car["parts"])

        for car in jay["cars"]:
            if "lane" in car:
                lane = lanes.get(car["lane"], None)
                if "offset" in car:
                    temp = FirstScenario.apply_offset(lane, car["offset"])
                    lane = temp
                vehicle = sd.vehicles[car["car_id"]]
                vehicle.ai_set_script(lane)

            #if "ai" in car:
            #    vehicle = sd.vehicles[car["car_id"]]
            #    vehicle.ai_set_mode(car["ai"])
            #    if car["ai"] == "chase":
            #        target = car["target"]
            #        vehicle.ai_set_target(target, "chase")
            #        vehicle.ai_set_speed(1, "limit")
        self.bb.bmng.resume()
        return sd
