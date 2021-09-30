import keyboard

import CustomScenarios as cs
from BeamBuilder import BeamBuilder
from Recording.Manager import SequenceManager

if __name__ == "__main__":

    bb = BeamBuilder(launch=True)

    scenario = cs.BabaCrash(bb)

    manager = SequenceManager(bb, scenario)
    bb.bmng.set_steps_per_second(30)

    print("Press the Z key to record clip")
    while True:
        # time.sleep(3)
        if scenario.should_record_predicate() or keyboard.is_pressed("z"):
            print("Starting recording")
            manager.capture_footage()
            break

    print("Recording Finished")
