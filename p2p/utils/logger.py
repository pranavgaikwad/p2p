import logging

def logger():
    logger = logging.getLogger(__name__)
    consoleHandler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s %(asctime)-15s %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    return logger
