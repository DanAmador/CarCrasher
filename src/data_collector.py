import time

from BeamBuilder import BeamBuilder
from config import Levels
from custom_scenarios import BasicCarChase, FallFromSkyScenario, TestCrash
from recorder import SequenceManager

if __name__ == "__main__":
    framerate = 24
    steps_per_sec = 24

    bb = BeamBuilder(launch=True, steps_per_sec=steps_per_sec)

    scenario = BasicCarChase(bb)
    # bb.bmng.set_relative_camera(pos=(2,2,2))

    # sequence = ImageSequence(data_path / "captures")
    manager = SequenceManager(bb, scenario)
    while True:
        input("Press enter to record clip")
        # time.sleep(6)
        print("Starting recording")
        manager.capture_footage(steps_per_sec=steps_per_sec, framerate=framerate, duration=5
                                # total_captures=10
                                )
