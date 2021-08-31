import time

from BeamBuilder import BeamBuilder
from Recording.Manager import SequenceManager
import CustomScenarios as cs
import keyboard

if __name__ == "__main__":
    framerate = 30
    simulation_steps_per_frame = 3

    bb = BeamBuilder(launch=True, steps_per_sec=framerate)

    scenario = cs.JsonLoaderScenarioTest(bb)

    manager = SequenceManager(bb, scenario)
    print("Press S key to record clip")
    while True:
        # time.sleep(3)
        if scenario.should_record_predicate() or keyboard.is_pressed("s"):
            print("Starting recording")
            bb.bmng.set_steps_per_second(framerate * simulation_steps_per_frame)
            manager.capture_footage(simulation_steps_per_frame=simulation_steps_per_frame, framerate=framerate, duration=5
                                    # total_captures=10
                                    )
            break

    print("Recording Finished")
