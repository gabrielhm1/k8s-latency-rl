import logging


def setup_logging():
    # Create a logger
    logger = logging.getLogger("model_logger")
    logger.setLevel(logging.DEBUG)

    # Create file handlers
    info_handler = logging.FileHandler("app_logs/info.log")
    debug_error_handler = logging.FileHandler("app_logs/debug.log")

    # Set log levels for each handler
    info_handler.setLevel(logging.INFO)
    debug_error_handler.setLevel(logging.DEBUG)

    # Define formatters for the handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    info_handler.setFormatter(formatter)
    debug_error_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(info_handler)
    logger.addHandler(debug_error_handler)

    return logger
