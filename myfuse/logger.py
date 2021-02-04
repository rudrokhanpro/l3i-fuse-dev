import logging

log_filename = 'mydrive.log'

logging.basicConfig(
    filename=log_filename,
    level=logging.DEBUG
)


def log(string):
    logging.info(string)
