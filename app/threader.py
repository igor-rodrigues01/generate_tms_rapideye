#!-*-coding:utf-8-*-

from threading import Thread


class Threader(Thread):

    def __init__(self, callback, **kwargs):
        self.__callback = callback
        self.__kwargs = kwargs
        super(Threader, self).__init__()
        self.setDaemon(True)

    def run(self):
        self.__callback(**self.__kwargs)
