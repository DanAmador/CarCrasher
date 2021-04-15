from beamngpy import BeamNGpy, Scenario, Vehicle
import config 
#p = "Z:\BeamNG.research.v1.7.0.0"
# Instantiate BeamNGpy instance running the simulator from the given path,
# communicating over localhost:64256
print("loading")
bng = config.beam_factory()
# Launch BeamNG.tech
print("opening")
bng.open(launch=True)
print("scenario load")
# Create a scenario in west_coast_usa called 'example'
scenario = Scenario('west_coast_usa', 'example')
# Create an ETK800 with the licence plate 'PYTHON'
vehicle = Vehicle('ego_vehicle', model='etk800', licence='PYTHON')
# Add it to our scenario at this position and rotation
scenario.add_vehicle(vehicle, pos=(-717, 101, 118), rot=None, rot_quat=(0, 0, 0.3826834, 0.9238795))
# Place files defining our scenario for the simulator to read
print("making")
scenario.make(bng)

# Load and start our scenario
bng.load_scenario(scenario)
bng.start_scenario()
# Make the vehicle's AI span the map
vehicle.ai_set_mode('span')
input('Hit enter when done...')