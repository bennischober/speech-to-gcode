import logging
import os

def get_logger(name: str, filename: str = "image_pipeline.log"):
    logs_dir = os.getenv('LOGS_DIR')

    # Create a logger for the module
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Check for existing file handlers and update or create as necessary
    file_handler = None
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            file_handler = handler
            break

    if file_handler is None:
        # Create a file handler if none exists
        file_handler = logging.FileHandler(os.path.join(logs_dir, filename))
        logger.addHandler(file_handler)

    # Update the file path
    file_handler.baseFilename = os.path.join(logs_dir, filename)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    return logger
