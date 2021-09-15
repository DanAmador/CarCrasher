import keyboard

import CustomScenarios as cs
from BeamBuilder import BeamBuilder
from Recording.Manager import SequenceManager

if __name__ == "__main__":
    framerate = 30
    simulation_steps_per_frame = 1

    bb = BeamBuilder(launch=True)

    scenario = cs.JsonLoaderScenarioTest(bb)

    manager = SequenceManager(bb, scenario)
    print("Press R key to record clip")
    while True:
        # time.sleep(3)
        if scenario.should_record_predicate() or keyboard.is_pressed("z"):
            print("Starting recording")
            bb.bmng.set_steps_per_second(framerate * simulation_steps_per_frame)
            manager.capture_footage(simulation_steps_per_frame=simulation_steps_per_frame, framerate=framerate, duration=10
                                    # total_captures=10
                                    )
            break

    print("Recording Finished")
