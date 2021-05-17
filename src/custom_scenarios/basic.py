from beamngpy import BeamNGpy, Vehicle, Scenario, ProceduralRing, StaticObject
from beamngpy.sensors import Camera
from pathlib import Path
import numpy as np
from ..BeamBuilder import BeamBuilder
from ..config import Cars

if __name__ == "__main__":

    bb = BeamBuilder(launch=True)

    bb.with_car(car=Cars.ETK, pos=(-198.5, -164.189, 119.7))




    ramp = StaticObject(name='pyramp', pos=(277.5, 183.5, 118.75), rot=(0, 0, 55), scale=(1, 1, 1), shape='/levels/west_coast_usa/art/shapes/objects/ramp_massive.dae')
    missile = StaticObject(name='missile', pos=(10, 10, 10), rot=(0, 0, 55), scale=(1, 1, 1), shape='/objects/missile/untitled.dae')

    bb.scenario.add_object(ramp)
    bb.scenario.add_object(missile)

    ring = ProceduralRing(name='pyring', pos=(445, 301, 218), rot=(0, 0, 100), radius=5, thickness=2.5)


    bb.scenario.add_procedural_mesh(ring)



    bb.build_environment(hud=True)
