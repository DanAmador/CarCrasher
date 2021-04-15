from pathlib import Path
from beamngpy import BeamNGpy

beam_tech_path  = Path("Z:\BeamNG.tech.v0.21.3.0")
user_path = Path("Z:\Wat")
def beam_factory():
    return BeamNGpy('localhost', 64256, home=beam_tech_path, user=user_path)