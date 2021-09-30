import json
from datetime import datetime

from src.CustomScenarios import PaperCompare
from src.CustomScenarios.BaseScenarios import WithLidarView
from src.CustomScenarios.SceneData import SceneData
from src.config import UserSettings as us
import numpy as np

from beamngpy import ProceduralCylinder, ProceduralCone, ProceduralCube, ProceduralBump, ProceduralRing
class FirstScenario(WithLidarView):
    def __init__(self, bb):
        super().__init__(bb)
        self.start_time = datetime.now()
        self.framerate = 30
        self.duration = 60
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
                (scenario_path / f"final_lane_{lane}.json").read_text()), 2) for lane in lane_names}
        self.bb.bmng.pause()

        # position 1 euler = -2.391787, 3.153309,52.855541
        #
        #
        # axes = ["x", "y", "z"]
        # for idx, l in enumerate(lanes.values()):
        #    points = [[s[axes[p]] for p in range(3)] for s in l]
        #    lane_color = idx / 3
        #    self.bb.bmng.add_debug_spheres(points, radii=[1 for p in points],
        #                                   rgba_colors=[(lane_color, lane_color, lane_color,1) for p in points])
        #    self.bb.bmng.add_debug_polyline(points, rgba_color=(lane_color, lane_color, lane_color, 1), cling=True)

        # this part works, but we need to wait until it is loaded in
        for car in jay["cars"]:
            if "parts" in car:
                vehicle = sd.vehicles[car["car_id"]]
                vehicle.set_part_config(car["parts"])

        # for car in jay["cars"]:
        #   if "lane" in car:
        #        lane = lanes.get(car["lane"], None)
        #        if "offset" in car:
        #            temp = FirstScenario.apply_offset(lane, car["offset"])
        #            lane = temp
        #        vehicle = sd.vehicles[car["car_id"]]
        #        vehicle.ai_set_script(lane)
        #    if car["car_id"] == "police_back_left" or car["car_id"] == "police_back_right":
        #        vehicle = sd.vehicles[car["car_id"]]
        #        vehicle.ai_set_speed(4, "set")

        # if "ai" in car:
        #    vehicle = sd.vehicles[car["car_id"]]
        #    vehicle.ai_set_mode(car["ai"])
        #    if car["ai"] == "chase":
        #        target = car["target"]
        #        vehicle.ai_set_target(target, "chase")
        #        vehicle.ai_set_speed(1, "limit")
        self.bb.bmng.resume()
        return sd


class BaseCrashScenario(WithLidarView):
    def __init__(self, bb):
        super().__init__(bb)
        self.start_time = datetime.now()
        self.framerate = 30
        self.duration = 10
        self.simulation_steps_per_frame = 3
        self.crash_record_distance = 150
        self.crasher = None
        self.target_position = np.array([0, 0, 0])

    def should_record_predicate(self) -> bool:
        if not self.is_recording and self.crasher is not None:
            sensor1 = self.crasher.poll_sensors()
            if sensor1 and "state" in sensor1:
                state1 = sensor1["state"]["state"]
                if "pos" in state1:
                    pos1 = np.array(state1["pos"])
                    dist = np.linalg.norm(pos1 - self.target_position)
                    print(dist)
                    if dist < self.crash_record_distance:
                        self.is_recording = True
                        return True
        return self.is_recording


class AnubisCrash(PaperCompare):
    def __init__(self, bb):
        super().__init__(bb)
        self.duration = 10
        self.framerate = 30
        self.predicate_distance = 290
    def setup_scenario(self) -> SceneData:
        scenario_path = us.json_path / "CrashScenes"
        sd, jay = SceneData.from_json_file(scenario_path / "CrashScene1.json", self.bb)
        crasher = sd.vehicles["crasher"]
        target = sd.vehicles["target"]
        crasher.ai_set_target(target.vid)
        self.compare_list = [crasher, target]
        return sd


class PharaoCrash(PaperCompare):
    def __init__(self, bb):
        super().__init__(bb)
        self.duration = 10
        self.framerate = 30
        self.predicate_distance = 290
        self.target_position = np.array([27.202, 29.817, 0])

    def setup_scenario(self) -> SceneData:
        scenario_path = us.json_path / "CrashScenes"
        sd, jay = SceneData.from_json_file(scenario_path / "CrashScene2.json", self.bb)
        crasher = sd.vehicles["crasher"]
        target = sd.vehicles["target"]
        crasher.ai_set_target(target.vid)

        self.compare_list = [crasher, target]
        return sd


class MouseCrash(PaperCompare):
    def __init__(self, bb):
        super().__init__(bb)
        self.duration = 10
        self.framerate = 30
        self.predicate_distance = 150
        self.target_position = np.array([9.537, -182.850, 0])

    def setup_scenario(self) -> SceneData:
        scenario_path = us.json_path / "CrashScenes"
        sd, jay = SceneData.from_json_file(scenario_path / "CrashScene3.json", self.bb)
        crasher = sd.vehicles["crasher1"]
        crasher_2 = sd.vehicles["crasher2"]
        target = sd.vehicles["target"]
        crasher.ai_set_target(target.vid)
        crasher_2.ai_set_target(target.vid)

        self.compare_list = [crasher, target]
        return sd


class CentaurCrash(PaperCompare):
    def __init__(self, bb):
        super().__init__(bb)
        self.duration = 10
        self.framerate = 30
        self.predicate_distance = 100
        self.target_position = np.array([-28.282, -260.103, 0])

    def setup_scenario(self) -> SceneData:
        scenario_path = us.json_path / "CrashScenes"
        sd, jay = SceneData.from_json_file(scenario_path / "CrashScene4.json", self.bb)
        crasher = sd.vehicles["crasher"]
        target = sd.vehicles["target"]
        crasher.ai_set_target(target.vid)

        self.compare_list = [crasher, target]
        return sd


class BabaCrash(PaperCompare):
    def __init__(self, bb):
        super().__init__(bb)
        self.duration = 10
        self.framerate = 30
        self.predicate_distance = 150
        self.target_position = np.array([11.745, -334.002, 0])

    def setup_scenario(self) -> SceneData:
        scenario_path = us.json_path / "CrashScenes"
        sd, jay = SceneData.from_json_file(scenario_path / "CrashScene5.json", self.bb)
        crasher = sd.vehicles["crasher1"]
        crasher_2 = sd.vehicles["crasher2"]
        target = sd.vehicles["target1"]
        target_2 = sd.vehicles["target2"]
        crasher.ai_set_target(target.vid)
        crasher_2.ai_set_target(target_2.vid)

        self.compare_list = [crasher, target]
        return sd
