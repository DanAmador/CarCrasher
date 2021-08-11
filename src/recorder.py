import time

from BeamBuilder import BeamBuilder
from Recording.Manager import SequenceManager
import CustomScenarios as cs
import keyboard

if __name__ == "__main__":
    framerate = 10
    steps_per_sec = 24

    bb = BeamBuilder(launch=False, steps_per_sec=steps_per_sec)

    scenario = cs.JsonLoaderScenarioTest(bb)
    # bb.bmng.set_relative_camera(pos=(2,2,2))

    # sequence = ImageSequence(data_path / "captures")
    # scenario.initialize_scenario()
    manager = SequenceManager(bb, scenario)
    print("Press S key to record clip")
    while True:
        # time.sleep(3)
        if scenario.should_record_predicate() or keyboard:
            print("Starting recording")
            manager.capture_footage(steps_per_sec=steps_per_sec, framerate=framerate, duration=5
                                    # total_captures=10
                                    )
            break

    print("Recording Finished")
