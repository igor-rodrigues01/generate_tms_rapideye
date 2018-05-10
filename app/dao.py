#!-*-coding:utf-8-*-

import psycopg2
import sys
from log2 import Log

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
        # import pdb; pdb.set_trace()
        # sql only with fields
        sql_fields = "INSERT INTO {}.{} (gid, path, image, data, tms,"\
            " quicklook, geom, nuvens, total_part)".format(
                SCHEMA, TABLENAME_RAPIDEYE_CATALOG
            )
        # sql only with values
        sql_values = " VALUES ({gid},'{path}','{image}','{data}','{tms}',"\
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
            Log.success('Sucesso: Imagem {} foi inserida com sucesso.'.format(
                data_dict['path']
            ))


# insert into ibama.img_catalogo_rapideye_a
#     (gid, path, image, "data", tms, quicklook, geom, nuvens, total_part)
# values(
#    3, 'abc.com', 'img123', '2016-12-01', 'img.tms', 'qicklook',
#    ST_GeomFromText('MULTIPOLYGON (((763500 8440500, 788500 8440500, 788500 8415500, 763500 8415500, 763500 8440500)))', 4674),
#   1.5,1)
