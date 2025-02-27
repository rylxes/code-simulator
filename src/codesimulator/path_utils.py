import os
import sys
import tempfile
import platform
from .logging_config import logger


def is_packaged():
    """Check if running in a packaged environment."""
    return getattr(sys, 'frozen', False)


def get_resource_path(app=None, *paths):
    """
    Get the correct path to resource files, working in both development and packaged environments.

    Args:
        app: Optional Toga app instance
        *paths: Path components to join to the resource path
    """
    try:
        # First try to use Toga's paths if available
        if app and hasattr(app, 'paths') and hasattr(app.paths, 'resources'):
            base_path = app.paths.resources
            logger.debug(f"Using Toga resource path: {base_path}")
        else:
            # Fallback based on environment
            if is_packaged():
                # Packaged app - path depends on platform
                if platform.system() == 'Darwin':  # macOS
                    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.executable))),
                                             'Resources')
                elif platform.system() == 'Windows':
                    base_path = os.path.join(os.path.dirname(sys.executable), 'app', 'resources')
                else:  # Linux and others
                    base_path = os.path.join(os.path.dirname(sys.executable), 'resources')
                logger.debug(f"Using packaged resource path: {base_path}")
            else:
                # Development environment
                base_path = os.path.join(os.path.dirname(__file__), 'resources')
                logger.debug(f"Using development resource path: {base_path}")

        full_path = os.path.join(base_path, *paths)
        logger.debug(f"Full resource path: {full_path}")
        return full_path
    except Exception as e:
        logger.error(f"Error getting resource path: {e}")
        # Last resort fallback
        return os.path.join(os.path.dirname(__file__), 'resources', *paths)


def get_log_path():
    """Returns a path suitable for log files."""
    if is_packaged():
        # Use system temp directory for packaged app
        log_dir = tempfile.gettempdir()
    else:
        # Use resources directory in development
        log_dir = os.path.join(os.path.dirname(__file__), 'resources')

    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            pass

    return os.path.join(log_dir, 'codesimulator.log')


def log_environment_info():
    """Log detailed environment information for debugging."""
    info = {
        "Platform": platform.system(),
        "Python Version": sys.version,
        "Packaged App": is_packaged(),
        "Executable Path": sys.executable,
        "Current Directory": os.getcwd(),
        "Module Path": os.path.dirname(__file__),
        "Resource Path Example": get_resource_path(None, 'config.json')
    }

    for key, value in info.items():
        logger.info(f"{key}: {value}")


def get_log_path():
    """Returns a path suitable for log files."""
    try:
        if is_packaged():
            # Use a more accessible location for packaged app
            if platform.system() == "Windows":
                log_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser("~")), "CodeSimulator", "logs")
            elif platform.system() == "Darwin":  # macOS
                log_dir = os.path.join(os.path.expanduser("~"), "Library", "Logs", "CodeSimulator")
            else:  # Linux and others
                log_dir = os.path.join(os.path.expanduser("~"), ".codesimulator", "logs")
        else:
            # Use resources directory in development
            log_dir = os.path.join(os.path.dirname(__file__), 'resources')

        # Create directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        return os.path.join(log_dir, 'codesimulator.log')
    except Exception as e:
        # If all else fails, use system temp directory
        import tempfile
        return os.path.join(tempfile.gettempdir(), 'codesimulator.log')
