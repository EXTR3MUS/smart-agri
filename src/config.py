"""Configuration for the greenhouse simulation.

Adjust these values to control the simulated environment and server.
"""

SERVER_HOST = "localhost"
SERVER_PORT = 5020

DAY_DURATION_SECONDS = 60.0

MIN_TEMP = 18.0
MAX_TEMP = 28.0

INITIAL_SOIL_MOISTURE = 55.0

DAILY_MOISTURE_DECAY = 30.0       # how much moisture drops over one simulated day when pump OFF
DAILY_IRRIGATION_GAIN = 80.0      # how much moisture increases over one simulated day when pump ON

INITIAL_MODE = 1      # 1 = Auto, 0 = Manual
INITIAL_SETPOINT = 15 # percent

LOG_INTERVAL_SECONDS = 0.5
