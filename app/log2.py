#!-*-coding:utf-8-*-

import os
from datetime import datetime


class Log:

    @classmethod
    def __create_logdir_of_day(cls, now, dir_logs='logs'):
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
    def __create_write_logfile(cls, filename, now, msg, is_success=True):
        abspath_log_day = cls.__create_logdir_of_day(now)
        abspath_logfile = os.path.join(abspath_log_day, filename)
        file = open(abspath_logfile, 'a+')
        preffix = 'Success' if is_success else 'Error'
        content = '{}: {}\n\n'.format(preffix, msg)
        file.write(content)
        file.close()

    @classmethod
    def success(cls, msg, now=datetime.now()):
        print(msg)
        filename = 'success.log'
        now = now.strftime('%d-%m-%Y')
        cls.__create_write_logfile(filename, now, msg, is_success=True)

    @classmethod
    def error(cls, msg, now=datetime.now()):
        print(msg)
        filename = 'error.log'
        now = now.strftime('%d-%m-%Y')
        cls.__create_write_logfile(filename, now, msg, is_success=False)
