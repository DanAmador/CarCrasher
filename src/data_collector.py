from BeamBuilder import BeamBuilder
from config import Cars
from pathlib import Path
import numpy as np
from PIL import Image 
import PIL 
import time
import json
if __name__ == "__main__":
    data_path = (Path(__file__).absolute()).parent.parent / "data"
    print(data_path.absolute())
    bb = BeamBuilder(launch=False, auto_setup_cam=False, auto_setup_car=False)

    cam = bb.cam_setup(annotation=True)
    bb.car_setup(sensors={"camera": cam})
    
    bb.build_environment(ai_mode="span")
    ego = bb.vehicle
    time.sleep(10)  # Some sleeping time to make sure the level fully loaded.

    ego.poll_sensors()
    print(ego.sensors)
    data = ego.sensors['camera'].data
    annotations = bb.bmng.get_annotations()
    print(annotations)
    with open((data_path / "test.json").absolute(), 'w') as f:
        json.dump(annotations, f)
    data['colour'].convert('RGB').save((data_path / "test.png").absolute(), "PNG")
    data['annotation'].convert('RGB').save((data_path / "annotation.png").absolute(), "PNG")
    