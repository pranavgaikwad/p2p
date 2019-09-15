import logging

def logger():
    logger = logging.getLogger(__name__)
    consoleHandler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(consoleHandler)
    return logger
