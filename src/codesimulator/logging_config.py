import logging
import logging.handlers
import os
import sys
import tempfile
import platform

# Create a custom logger
logger = logging.getLogger('codesimulator')
logger.setLevel(logging.DEBUG)

# Always set up console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Flag to track if file logging has been set up
_file_logging_initialized = False


def get_log_path():
    """Get a guaranteed writable log file path"""
    try:
        # For macOS (which is what you're using)
        if platform.system() == "Darwin":
            # This directory should always be writable for the current user on macOS
            log_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Logs', 'CodeSimulator')
        else:
            # For other platforms
            log_dir = os.path.join(tempfile.gettempdir(), 'CodeSimulator', 'logs')

        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Return full path
        return os.path.join(log_dir, 'codesimulator.log')
    except Exception:
        # Ultimate fallback - use temp directory
        return os.path.join(tempfile.gettempdir(), 'codesimulator.log')


def setup_file_logging():
    """Set up file logging"""
    global _file_logging_initialized

    # Only initialize once
    if _file_logging_initialized:
        return

    try:
        # Get log path
        log_file_path = get_log_path()

        # Create handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path, maxBytes=5 * 1024 * 1024, backupCount=2
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Add to logger
        logger.addHandler(file_handler)

        # Mark as initialized
        _file_logging_initialized = True

        # Log startup information
        logger.info(f"File logging initialized at: {log_file_path}")

    except Exception as e:
        # If file logging fails, log to console
        logger.error(f"Failed to set up file logging: {e}")


# Initialize file logging at module import time
setup_file_logging()