import logging.handlers
import os

# Define the log file path
log_file_path = os.path.join(os.path.dirname(__file__), 'resources', 'app.log')

# Create a custom logger
logger = logging.getLogger('codesimulator')
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=2)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters and add them to handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
