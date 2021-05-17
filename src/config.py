from pathlib import Path


class UserSettings:
    beam_tech_path = Path("Z:\BeamNG.tech.v0.21.3.0")
    user_path = Path("Z:\Wat")


class Levels:
    WEST_COAST = 'west_coast_usa'
    ITALY = "italy"
    INDUSTRIAL = "industrial"
    EAST_COAST_USA = "east_coast_usa"


class Cars:
    ETK = "etk800"


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
