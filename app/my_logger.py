import logging

def setup_logger(logger_name : str, logger_file : str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # create file handler which logs messages
    file_handler = logging.FileHandler(logger_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)

    return logger