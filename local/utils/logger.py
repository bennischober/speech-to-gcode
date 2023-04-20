import logging
from logging import Logger

logging.basicConfig(format='[%(asctime)s] %(levelname)-6s %(filename)24s:%(lineno)s : %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)

def get_logger(name = __name__) -> Logger:
    return logging.getLogger(name)