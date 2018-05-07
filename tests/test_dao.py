#!-*-coding:utf-8-*-

# import pytest
# import sys
# sys.path.append("/home/igor/projects/new-tms-rapideye/generate_tms_rapideye/processing_re/tests")

from processing_re.dao import DAO


DATA_TEST = [
    100, 'abc.com', 'img123', '2016-12-01', 'img.tms', 'qicklook',
    'MULTIPOLYGON (((763500 8440500, 788500 8440500, 788500 8415500,'
    ' 763500 8415500, 763500 8440500)))',
    1.5, 1
]


def check_by_select():
    pass


def test_insert():
    db = DAO(
        host='127.0.0.1', db='my_siscom', user='postgres',
        passwd='123456'
    )
    db.insert_catalog_rapideye(DATA_TEST)
    assert True
