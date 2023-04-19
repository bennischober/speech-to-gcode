import logging
from logging import Logger

logging.basicConfig(format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)

def get_logger(name = __name__) -> Logger:
    return logging.getLogger(name)