#!-*-coding:utf-8-*-

import psycopg2
import sys


class DAO:

    __conn = None

    def __init__(
        self, host='127.0.0.1', db='teste', user='postgres', passwd='123456'
    ):
        self.__connection(host, db, user, passwd)

    def __connection(self, host, db, user, passwd):
        try:
            self.__conn = psycopg2.connect(
                host=host, database=db, user=user,
                password=passwd
            )

        except Exception as exc:
            sys.exit('Erro na conexão: {}'.format(exc))


if __name__ == '__main__':
    dao = DAO()