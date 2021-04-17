import config
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Camera
from config import UserSettings as cfg
from config import Levels, Cars

class BeamBuilder():

    def __init__(self, launch=False):
        self.bmng = self.beam_factory(launch)
        self.scenario = self.scenario_setup(Levels.WEST_COAST)
        self.car_setup(Cars.ETK)
        self.camera = self.cam_setup() 
        
    def build_environment(self):
        self.scenario.add_camera(self.camera, 'cam')

        self.scenario.make(self.bmng)

        self.bmng.set_deterministic()
        self.bmng.load_scenario(self.scenario)
        #self.bmng.start_scenario()
        #self.bmng.close()
        
    def beam_factory(self, launch=False) -> BeamNGpy:
        bmng = BeamNGpy('localhost', 64256, home=cfg.beam_tech_path, user=cfg.user_path)
        bmng.open(launch=launch)
        return bmng

    def cam_setup(self) -> Camera:
        cam_pos = (391.5, 251, 197.8)
        cam_dir = (445 - cam_pos[0], 301 - cam_pos[1], 208 - cam_pos[2])
        return Camera(cam_pos, cam_dir, 60, (2048, 2048), near_far=(1, 4000), colour=True)

    def scenario_setup(self, level : Levels, name: str = "example") -> Scenario:
        scenario = Scenario(level, name)

        return scenario

    def car_setup(self,  car: Cars):
        vehicle = Vehicle('ego_vehicle', model=car, licence='AntonGinzburg')
        self.scenario.add_vehicle(vehicle, pos=(-717, 101, 118), rot=None, rot_quat=(0, 0, 0.3826834, 0.9238795))
        
if __name__ == "__main__":
    bb = BeamBuilder(launch=True)
    bb.build_environment()