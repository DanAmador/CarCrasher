from BeamBuilder import BeamBuilder
from config import Levels
from custom_scenarios import BasicCarChase
from recorder import SequenceManager


if __name__ == "__main__":
    framerate = 24
    steps_per_sec = 100

    bb = BeamBuilder(launch=True)
    bb.with_scenario(level=Levels.WEST_COAST)
    bb.build_environment(ai_mode="span", steps=steps_per_sec, hud=True)
    scenario = BasicCarChase(bb)
    # bb.bmng.set_relative_camera(pos=(2,2,2))

    # sequence = ImageSequence(data_path / "captures")
    manager = SequenceManager(bb, scenario)
    while True:
        input("Press enter to record clip")
        # time.sleep(6)
        manager.capture_footage(steps_per_sec=steps_per_sec, framerate=framerate, duration=1
                                # total_captures=10
                                )
