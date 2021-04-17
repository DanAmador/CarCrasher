from beamngpy import BeamNGpy, Scenario, Vehicle
from config import beam_factory
from beamngpy import BeamNGpy, Vehicle, Scenario, ProceduralRing, StaticObject
from beamngpy.sensors import Camera
from pathlib import Path
import numpy as np
import BeamBuilder



beamng = BeamBuilder()
beamng.open(launch=False)

scenario = Scenario('west_coast_usa', 'object_placement')

vehicle = Vehicle('ego', model='etk800', licence='PYTHON', color='Green')
scenario.add_vehicle(vehicle, pos=(-198.5, -164.189, 119.7), rot=(0, 0, -126.25))

ramp = StaticObject(name='pyramp', pos=(277.5, 183.5, 118.75), rot=(0, 0, 55), scale=(1, 1, 1), shape='/levels/west_coast_usa/art/shapes/objects/ramp_massive.dae')
missile = StaticObject(name='missile', pos=(10, 10, 10), rot=(0, 0, 55), scale=(1, 1, 1), shape='/objects/missile/untitled.dae')

scenario.add_object(ramp)
scenario.add_object(missile)

ring = ProceduralRing(name='pyring', pos=(445, 301, 218), rot=(0, 0, 100), radius=5, thickness=2.5)
scenario.add_procedural_mesh(ring)

cam_pos = (391.5, 251, 197.8)
cam_dir = (445 - cam_pos[0], 301 - cam_pos[1], 208 - cam_pos[2])
cam = Camera(cam_pos, cam_dir, 60, (2048, 2048), near_far=(1, 4000), colour=True)
scenario.add_camera(cam, 'cam')

scenario.make(beamng)


beamng.set_deterministic()
beamng.load_scenario(scenario)
beamng.start_scenario()

meshes = scenario.find_procedural_meshes()

beamng.close()