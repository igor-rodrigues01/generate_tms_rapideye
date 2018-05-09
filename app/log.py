#!-*-coding:utf-8-*-

import logging
import os
from datetime import datetime


class Log:

    __dir_log = None
    __logger_error = None
    __logger_info = None

    def __init__(
        self, dir_log='logs', filename_error_log='error',
        filename_info_log='info'
    ):
        path = os.path.abspath(__file__)
        path_project = os.path.dirname(os.path.dirname(path))
        now = datetime.now().strftime('%d-%m-%Y')

        self.__dir_log = os.path.join(path_project, dir_log)
        self.__filename_error_log = '{}/{}.log'.format(now, filename_error_log)
        self.__filename_info_log = '{}/{}.log'.format(now, filename_info_log)
        self.__create_logdir_of_day(now)
        self.__logger_info = self.__create_log(
            self.__filename_info_log, 'info'
        )
        self.__logger_error = self.__create_log(
            self.__filename_error_log, 'erro'
        )

    def __create_logdir_of_day(self, now):
        """
        Methode that create the directory to logs of day
        """
        dir_of_day = os.path.join(self.__dir_log, now)
        if not os.path.exists(dir_of_day):
            os.makedirs(dir_of_day)

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
        print(msg)
        self.__logger_info.info(msg)

    def error(self, msg):
        """
        Function thar write in error log's file
        """
        print(msg)
        self.__logger_error.error(msg)


if __name__ == '__main__':
    l = Log()
    l.info('ABC')
    l.error('asdfadfd')