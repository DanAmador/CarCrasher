from pathlib import Path

project_root = (Path(__file__).absolute()).parent.parent


class UserSettings:
    beam_tech_path = project_root / "BeamNG.tech"
    user_path = project_root / "user_path"
    data_path = project_root / "data" / "beamng"
    json_path = project_root / "src" / "jsons"


class Levels:
    WEST_COAST = 'west_coast_usa'
    ITALY = "italy"
    INDUSTRIAL = "industrial"
    EAST_COAST_USA = "east_coast_usa"
    SMALL_GRID = "smallgrid"
    GRIDMAP = "gridmap"
    KONRAD = "ownmap"

class Cars:
    ETK = "etk800"
    VAN = "van"
    ETKC = "etkc"
    TRUCK = "semi"
    OLD = "oldtimer"
    DOPE = "dopel"


"""

       * ``disabled``: Turn the AI off (default state)
       * ``random``: Drive from random points to random points on the map
       * ``span``: Drive along the entire road network of the map
       * ``manual``: Drive to a specific waypoint, target set separately
       * ``chase``: Chase a target vehicle, target set separately
       * ``flee``: Flee from a vehicle, target set separately
       * ``stopping``: Make the vehicle come to a halt (AI disables itself
                                                          once the vehicle
                                                          stopped.)

      """


class AIMode:
    DISABLED = "disabled"
    RANDOM = "random"
    SPAN = "span"
    MANUAL = "manual"
    CHASE = "chase"
    FLEE = "flee"
    STOPPING = "stopping"
