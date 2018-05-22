#!-*-coding:utf-8-*-

import os
from datetime import datetime
from constants import FILE_ALL_RAPIDEYE


class Log:

    path_lot_log = None

    def __init__(self, process_one_img):
        self.__process_one_img = process_one_img
        self.path_lot_log = self.__create_dir_to_lot(process_one_img)

    def __create_dir_to_lot(self, process_one_img, dir_logs='logs'):
        """
        Method that create the directory with the lot name
        """
        path = os.path.abspath(__file__)
        path_project = os.path.dirname(os.path.dirname(path))
        if self.__process_one_img:
            now = datetime.now().strftime('%d-%m-%Y')
            lot_filename = 'oneImg_{}'.format(now)
        else:
            lot_filename = os.path.basename(FILE_ALL_RAPIDEYE)
            lot_filename = lot_filename[:-4]

        path_lot_log = os.path.join(path_project, dir_logs, lot_filename)

        if not os.path.exists(path_lot_log):
            os.makedirs(path_lot_log)

        return path_lot_log

    def __create_logdir_of_day(self, now):
        """
        Method that create the directory to logs of day and return
        """
        abspath_log_day = os.path.join(self.path_lot_log, now)

        if not os.path.exists(abspath_log_day):
            os.mkdir(abspath_log_day)

        return abspath_log_day

    def __create_write_logfile(self, filename, now, msg, is_success=True):
        """
        method tha create and write in log file
        """
        abspath_log_day = self.__create_logdir_of_day(now)
        abspath_logfile = os.path.join(abspath_log_day, filename)
        file = open(abspath_logfile, 'a+')
        preffix = 'Success' if is_success else 'Error'
        content = '{}: {}\n\n'.format(preffix, msg)
        file.write(content)
        file.close()

    def success(self, msg, now=datetime.now()):
        """
        Method that write success messages in the log file
        """
        print('\nSuccess: {}'.format(msg))
        filename = 'success.log'
        now = now.strftime('%d-%m-%Y')
        self.__create_write_logfile(filename, now, msg, is_success=True)

    def error(self, msg, now=datetime.now()):
        """
        Method that write error messages in the log file
        """
        print('Error: {}'.format(msg))
        filename = 'error.log'
        now = now.strftime('%d-%m-%Y')
        self.__create_write_logfile(filename, now, msg, is_success=False)
