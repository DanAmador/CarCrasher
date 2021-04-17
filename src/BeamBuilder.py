import config
from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Camera
from config import UserSettings as cfg
from config import Levels, Cars

class BeamBuilder():

    def __init__(self, launch=False, scenario_name="Beam Builder", auto_setup_car=True, auto_setup_cam=True):
        self.bmng = self.beam_factory(launch)
        self.scenario = self.scenario_setup(Levels.WEST_COAST, name= scenario_name)
        self.vehicle = self.car_setup() if auto_setup_car else None
        self.camera = self.cam_setup() if auto_setup_cam else None

        self.meshes = []


            
        
    def build_environment(self, hud=False, steps=60, ai_mode= None):
        self.scenario.add_camera(self.camera, 'camera')

        if not hud:
            self.bmng.hide_hud()
        
        self.bmng.set_steps_per_second(60)

        self.scenario.make(self.bmng)
        #self.meshes = self.scenario.find_procedural_meshes()

        self.bmng.set_deterministic()
        self.bmng.load_scenario(self.scenario)
        self.bmng.start_scenario()

        
        if ai_mode != None:
            print(f"Setting ai mode {ai_mode}")
            self.vehicle.ai_set_mode(mode=ai_mode)
        #self.bmng.close()
        
    def beam_factory(self, launch=False) -> BeamNGpy:
        bmng = BeamNGpy('localhost', 64256, home=cfg.beam_tech_path, user=cfg.user_path)
        bmng.open(launch=launch)
        return bmng

    def cam_setup(self,cam_pos=(-0.3, 1, 1), cam_dir= None,colour=True,depth=False, annotation=False, instance=False) -> Camera:
        if cam_dir == None:
            cam_dir = (445 - cam_pos[0], 301 - cam_pos[1], 208 - cam_pos[2])
        self.camera = Camera(cam_pos, cam_dir, 60, (2048, 2048), near_far=(1, 4000),colour=colour,depth=depth, annotation=annotation, instance=instance) 
        return self.camera
    
    def scenario_setup(self, level : Levels, name: str = "example") -> Scenario:
        scenario = Scenario(level, name)
        self.scenario = scenario
        return scenario

    def car_setup(self,  car: Cars= Cars.ETK, pos=(-717, 101, 118), rot= None, rot_quat = (0, 0, 0.3826834, 0.9238795), sensors={}):
        vehicle = Vehicle('ego', model=car, licence='AntonGinzburg')

        for sensor_name, sensor in sensors.items():
            print(f"Attaching {sensor_name} to {car}")
            vehicle.attach_sensor(name=sensor_name, sensor=sensor)

        self.scenario.add_vehicle(vehicle, pos=pos, rot=rot, rot_quat=rot_quat)
        self.vehicle = vehicle
        return vehicle
    
if __name__ == "__main__":
    bb = BeamBuilder(launch=False)
    bb.build_environment(ai_mode="span")