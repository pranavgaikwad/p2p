import logging


def logger():
    _logger = logging.getLogger(__name__)
    if not _logger.hasHandlers():
        console_handler = logging.StreamHandler()
        _logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s %(asctime)-15s %(message)s', '%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    return _logger
