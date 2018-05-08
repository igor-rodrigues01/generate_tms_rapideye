#!-*-coding:utf-8-*-

import psycopg2
import sys

# CONNECTION DATA
# HOSTADDR = '10.1.8.58'
# USER = 'indicarprocess'
# PASSWORD = 'ind!c@rprcss'
# DATABASE = 'siscom'
TABLENAME_RAPIDEYE_CATALOG = 'img_catalogo_rapideye_a'
SCHEMA = 'ibama'
FIELDS_RAPIDEYE_CATALOG = [
    'gid', 'path', 'image', 'data', 'tms', 'quicklook', 'geom',
    'nuvens', 'total_part'
]


class DAO:

    __conn = None

    def __init__(
        self, host='127.0.0.1', db='my_siscom', user='postgres',
        passwd='123456'
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

    def __create_sql(self, data):
        """
        Method that create sql to insertion
        """
        # sql only with fields
        sql_fields = "INSERT INTO {}.{} ({},{},{},{},{},{},{},{},{})".format(
            SCHEMA, TABLENAME_RAPIDEYE_CATALOG, *FIELDS_RAPIDEYE_CATALOG
        )
        # sql only with values
        sql_values = " VALUES ({},'{}','{}','{}','{}','{}'," \
            "ST_GeomFromText('{}', 4674),{},{})".format(*data)

        return sql_fields + sql_values

    def insert_catalog_rapideye(
        self, data_list=None, table_name=TABLENAME_RAPIDEYE_CATALOG
    ):
        """
        Method that insert data in the database
        """
        sql = self.__create_sql(data)
        cursor = self.__conn.cursor()
        try:
            cursor.execute(sql)

        except Exception as ex:
            self.__conn.rollback()
            print(ex)

        else:
            self.__conn.commit()
            print('Dados inseridos com sucesso')


if __name__ == '__main__':
    dao = DAO()
    data = [
        8, 'abc.com', 'img123', '2016-12-01', 'img.tms', 'qicklook',
        'MULTIPOLYGON (((763500 8440500, 788500 8440500, 788500 8415500,' \
        ' 763500 8415500, 763500 8440500)))',
        1.5, 1
    ]
    dao.insert_catalog_rapideye(data)


# insert into ibama.img_catalogo_rapideye_a
#     (gid, path, image, "data", tms, quicklook, geom, nuvens, total_part)
# values(
#    3, 'abc.com', 'img123', '2016-12-01', 'img.tms', 'qicklook',
#    ST_GeomFromText('MULTIPOLYGON (((763500 8440500, 788500 8440500, 788500 8415500, 763500 8415500, 763500 8440500)))', 4674),
#   1.5,1)
