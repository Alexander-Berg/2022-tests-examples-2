# coding=utf-8
from __future__ import unicode_literals
import pytest


@pytest.fixture()
def json():
    import library.python.resource as res
    return res.find('data.json').split('\n')


@pytest.fixture()
def sql():
    import library.python.resource as res
    return res.find('data.sql').split('\n')
