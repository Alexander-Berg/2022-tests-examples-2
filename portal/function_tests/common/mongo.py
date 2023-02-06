# -*- coding: utf-8 -*-
import pymongo
import pytest

_QAMONGO_HOSTS = ['vla2-0466-bea-vla-portal-mongo-mock-14630.gencfg-c.yandex.net:27017',
                  'man1-0398-man-portal-mongo-mock-20080.gencfg-c.yandex.net:27017',
                  'sas1-8295-sas-portal-mongo-mock-21098.gencfg-c.yandex.net:27017',
                  'vla2-0471-d6a-vla-portal-mongo-mock-14630.gencfg-c.yandex.net:27017',
                  'man1-4717-man-portal-mongo-mock-20080.gencfg-c.yandex.net:27017',
                  'sas1-8296-sas-portal-mongo-mock-21098.gencfg-c.yandex.net:27017']

_QAMONGO_URL = 'mongodb://{}'.format(','.join(_QAMONGO_HOSTS))


@pytest.fixture
def qamongo():
    client = pymongo.MongoClient(_QAMONGO_URL)
    client.morda.authenticate('morda', 't6d!~P5!=IFH6ob/rG~5')
    return client.morda
