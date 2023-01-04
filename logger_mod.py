import logging
import os

class Logger():

    def __init__(self):
        """ This is a constructor, once the logger class is called it will init
        the instance variable basically it will create a generic logger and sets its
        setlevels.
        Arguments:    None
        Returns:    None
        """
        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.DEBUG)
        self.__formate = logging.Formatter('%(levelname)8s : %(name)6s :   %(asctime)20s :  %(module)8s  :%(message)8s ',
                                         datefmt="%d-%m-%Y %I:%M:%S %p")
        self.__console_formate = logging.Formatter('%(message)s')

    def setup_logger(self):
        """
        This method is to create 3 different file handlers based on there loglevel
        and a stream handler for printing error messages in console.
        Arguments: None
        Returns: logger Object
        """

        file_handler_info = logging.FileHandler(" info.log")
        file_handler_info.setLevel(logging.INFO)
        file_handler_info.setFormatter(self.__formate)
        self.__logger.addHandler(file_handler_info)

        file_handler_debug = logging.FileHandler(" debug.log")
        file_handler_debug.setLevel(logging.DEBUG)
        file_handler_debug.setFormatter(self.__formate)
        self.__logger.addHandler(file_handler_debug)

        file_handler_error = logging.FileHandler(" error.log")
        file_handler_error.setLevel(logging.ERROR)
        file_handler_error.setFormatter(self.__formate)
        self.__logger.addHandler(file_handler_error)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(self.__console_formate)
        self.__logger.addHandler(stream_handler)

        return self._Logger__logger

log_ref = Logger()
log = log_ref.setup_logger()