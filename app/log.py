#!-*-coding:utf-8-*-

import logging
import os
from datetime import datetime


class Log:

    __dir_log = None
    __logger_error = None
    __logger_info = None

    @classmethod
    def __create_logdir_of_day(cls, now, dir_logs):
        """
        Method that create the directory to logs of day and return
        """
        path = os.path.abspath(__file__)
        path_project = os.path.dirname(os.path.dirname(path))
        abspath_log_day = os.path.join(path_project, dir_logs, now)

        if not os.path.exists(abspath_log_day):
            os.mkdir(abspath_log_day)

        return abspath_log_day

    @classmethod
    def __create_file_log(cls, file_name, now, app_log, dir_logs='logs'):
        """
        Function that create log file inside direrctory log of day
        """
        log_day = os.path.join(cls.__create_logdir_of_day(now), file_name)

        if not os.path.exists(log_day):
            logger = logging.getLogger(app_log)
            path_file_log = logging.FileHandler(
                os.path.join(dir_logs, file_name)
            )
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            path_file_log.setFormatter(formatter)
            logger.addHandler(path_file_log)
            logger.setLevel(logging.DEBUG)
        return logger

    @classmethod
    def info(self, msg):
        """
        Function thar write in info log's file
        """
        self.__create_logdir_of_day(now)
        print(msg)
        self.__logger_info.info(msg)

    @classmethod
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