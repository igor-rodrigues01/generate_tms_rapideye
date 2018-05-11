#!-*-coding:utf-8-*-

# import pytest

import psycopg2
import pytest

from app.dao import DAO


DATA_TEST = {
    'image': 'abc.com', 'path': 'teste/teste',
    'data': '2016-12-01', 'tms': 'img.tms', 'quicklook': 'quicklook',
    'geom': 'MULTIPOLYGON (((763500 8440500, 788500 8440500, 788500 8415500,'
    ' 763500 8415500, 763500 8440500)))', 'nuvens': 1.5, 'total_part': 1
}

HOST = '127.0.0.1'
DB = 'my_siscom'
USER = 'postgres'
PASSWD = '123456'
SCHEMA = 'ibama'

TABLENAME_RAPIDEYE_CATALOG = 'img_catalogo_rapideye_a'


@pytest.fixture
def connection():
    return psycopg2.connect(host=HOST, database=DB, user=USER, password=PASSWD)


def test_insert():
    db = DAO(host=HOST, db=DB, user=USER, passwd=PASSWD)
    db.insert_catalog_rapideye(DATA_TEST)
    assert True


def test_check_db_by_select(connection):
    cursor = connection.cursor()
    sql = 'SELECT * FROM {}.{}'.format(SCHEMA, TABLENAME_RAPIDEYE_CATALOG)
    cursor.execute(sql)
    result = cursor.fetchall()
    assert len(result) != 0
