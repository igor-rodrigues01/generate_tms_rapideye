#!-*-coding:utf-8-*-

import logging
import os


class Log:

    __dir_log = None
    __logger_error = None
    __logger_info = None

    def __init__(
        self, dir_log='../logs', filename_error_log='errors.log',
        filename_info_log='info.log'
    ):
        self.__dir_log = dir_log
        self.__filename_error_log = filename_error_log
        self.__filename_info_log = filename_info_log
        self.__logger_info = self.__create_log(
            self.__filename_info_log, 'info'
        )
        self.__logger_error = self.__create_log(
            self.__filename_error_log, 'erro'
        )

    def __create_log(self, file_name, log):
        """
        Function that create log file
        """
        logger = logging.getLogger(log)
        path_file_log = logging.FileHandler(
            os.path.join(self.__dir_log, file_name)
        )
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        path_file_log.setFormatter(formatter)
        logger.addHandler(path_file_log)
        logger.setLevel(logging.DEBUG)
        return logger

    def info(self, msg):
        """
        Function thar write in info log's file
        """
        self.__logger_info.info(msg)

    def error(self, msg):
        """
        Function thar write in error log's file
        """
        self.__logger_error.error(msg)


if __name__ == '__main__':
    l = Log()
    l.info('ABC')
    l.error('asdfadfd')