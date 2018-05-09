#!-*-coding:utf-8-*-

# import pytest

import sys
sys.path.append("../")
from processing_re.app.dao import DAO


DATA_TEST = [
    100, 'abc.com', 'img123', '2016-12-01', 'img.tms', 'qicklook',
    'MULTIPOLYGON (((763500 8440500, 788500 8440500, 788500 8415500,'
    ' 763500 8415500, 763500 8440500)))',
    1.5, 1
]
HOST = '127.0.0.1'
DB = 'my_siscom'
USER = 'postgres'
PASSWD = '123456'

TABLENAME_RAPIDEYE_CATALOG = 'img_catalogo_rapideye_a'


def test_insert():
    db = DAO(host=HOST, db=DB, user=USER, passwd=PASSWD)
    db.insert_catalog_rapideye(DATA_TEST)
    assert True


def check_by_select():
    pass
