import logging
from logging.handlers import TimedRotatingFileHandler
import os
from dotenv import load_dotenv

load_dotenv()

LOG_DIR = os.getenv("LOG_DIR")
LOG_ROLL_DAYS = int(os.getenv("LOG_ROLE_DAYS"))

def setup_logger(logger_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with daily log rotation and automatic cleanup.

    Args:
        logger_name (str): Name of the logger.
        level (int): Logging level (e.g., DEBUG, INFO).

    Returns:
        logging.Logger: Configured logger.
    """
    
    # Create the logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # current date's log file will be app.log
    log_file = os.path.join(LOG_DIR, "app.log")  # Base name for logs

    # Set up the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Prevent duplicate handlers if the logger is already configured
    if logger.hasHandlers():
        return logger

    # Define log format
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Create a TimedRotatingFileHandler
    handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=LOG_ROLL_DAYS
    )
    handler.setFormatter(formatter)
    handler.suffix = "%Y-%m-%d"  # Add a suffix to log files for rolling
    handler.setLevel(level)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Add a console handler for debugging purposes
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    return logger