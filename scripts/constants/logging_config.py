# constants/logging_config.py
import logging
import os

# Define the log directory (This is just a way to construct the path to the logs folder in your app file structure)
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')

# Check if the log directory exists, if not create it
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Define the log file path
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the minimum logging level (Log messages with level DEBUG or higher will be logged)
    format="%(asctime)s [%(levelname)s] %(message)s",  # Log format
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to file
        logging.StreamHandler()         # Log to console
    ]
)

# Function to return a logger instance
def get_logger(name):
    return logging.getLogger(name)
