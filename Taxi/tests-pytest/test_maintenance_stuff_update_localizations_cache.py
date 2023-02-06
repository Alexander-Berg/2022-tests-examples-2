# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import pytest
from django import test as django_test

from taxi.core import async
from taxi.core import db
from taxi.internal import localization_update as localizations
from taxi_maintenance.stuff import update_localizations_cache

MOCK_TANKER_KEYSET = {
    'keysets': {
        'backend.geoareas': {
            'keys': {
                'some.big.key': {
                    'info': {
                        'references': '',
                        'is_plural': False,
                        'context': '',
                    },
                    'translations': {
                        'ru': {
                            'status': 'approved',
                            'change_date': '17:49:12 21.03.2019',
                            'form': 'luke! am ur father!',
                            'translator_comment': '',
                            'author': 'some',
                        }
                    }
                }
            }
        }
    }
}


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    LOCALES_SUPPORTED=['en', 'ru'],
    TANKER_KEYSETS={'geoareas': 'backend.geoareas'},
    LOCALES_AZ_OVERRIDE_KEYSETS={
        'geoareas': 'ignore',
    },
    USE_PERIODIC_FOR_LOCALIZATIONS=True,
)
@pytest.inline_callbacks
def test_do_stuff(patch):
    @patch('taxi.external.tanker.fetch_keyset')
    @async.inline_callbacks
    def fetch_keyset_mock(*args, **kwargs):
        yield
        async.return_value(MOCK_TANKER_KEYSET)

    yield update_localizations_cache.do_stuff()

    assert (yield db.localizations_cache.find().count()) == 1

    cache_diff = yield db.localizations_meta.find_one({
        '_id': localizations.KEYSETS_DIFF_CACHE_ID,
    })
    assert cache_diff['value'] == ['geoareas']
    response = django_test.Client().get(
        '/api/update_localizations/keysets_diff/',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {'keysets': [{'id': 'geoareas'}]}

    cache = yield db.localizations_cache.find_one({
        '_id': 'geoareas',
    })
    assert cache['value'] == localizations.serialize({
        'some.big.key': {
            'ru': 'luke! am ur father!',
        }
    })
    cache = localizations.deserialize(cache['value'])
    assert cache == {
        'some.big.key': {
            'ru': 'luke! am ur father!',
        }
    }

    response = django_test.Client().post(
        '/api/update_localizations/',
        json.dumps({'keyset': ['geoareas']}),
        content_type='application/json'
    )
    assert response.status_code == 200
    response = django_test.Client().get(
        '/api/update_localizations/keysets_diff/',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {'keysets': []}

    yield update_localizations_cache.do_stuff()

    cache_diff = yield db.localizations_meta.find_one({
        '_id': localizations.KEYSETS_DIFF_CACHE_ID,
    })
    assert not cache_diff['value']
