#!-*-coding:utf-8-*-
import sys
import psycopg2

from log import Log
from constants import (
    HOSTADDR, USER, PASSWORD, DATABASE, SCHEMA, TABLENAME_RAPIDEYE_CATALOG
)


class DAO:

    __conn = None

    def __init__(
        self, host=HOSTADDR, db=DATABASE, user=USER,
        passwd=PASSWORD
    ):
        self.__connection(host, db, user, passwd)

    def __connection(self, host, db, user, passwd):
        """
        Method responsible to stablish connection
        """
        try:
            self.__conn = psycopg2.connect(
                host=host, database=db, user=user,
                password=passwd
            )

        except Exception as exc:
            sys.exit('Erro na conexão: {}'.format(exc))

    def __create_sql(self, data_dict):
        """
        Method that create sql to insertion
        """
        # sql only with fields
        sql_fields = "INSERT INTO {}.{} (path, image, data, tms,"\
            " quicklook, geom, nuvens, total_part)".format(
                SCHEMA, TABLENAME_RAPIDEYE_CATALOG
            )
        # sql only with values
        sql_values = " VALUES ('{path}','{image}','{data}','{tms}',"\
            "'{quicklook}', ST_GeomFromText('{geom}', 4674),{nuvens},"\
            " {total_part})".format(**data_dict)

        return sql_fields + sql_values

    def insert_catalog_rapideye(
        self, data_dict=None, table_name=TABLENAME_RAPIDEYE_CATALOG
    ):
        """
        Method that insert data in the database
        """
        sql = self.__create_sql(data_dict)
        cursor = self.__conn.cursor()
        try:
            cursor.execute(sql)

        except Exception as ex:
            self.__conn.rollback()
            Log.error(
                '{}\nA imagem {} foi processada mas seus dados"\
                " não foram inseridos no banco.'.format(
                    ex, data_dict['path']
                )
            )
        else:
            self.__conn.commit()
            Log.success('Imagem {} foi inserida com sucesso.'.format(
                data_dict['path']
            ))
