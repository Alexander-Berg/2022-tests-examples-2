# coding: utf-8

from __future__ import unicode_literals

import json
from copy import copy

from django import test as django_test
import pytest

from taxi.core import async
from taxiadmin import tariff_checks

SAMPLE_GEOAREA = {
    'name': 'sample_area',
    'default_point': [37.52700299554216, 55.41982763489354],
    'geometry': {
      'shell': [
        [37.65823811822285, 55.496752774565095],
        [37.65497655206074, 55.50824999626598],
        [37.64982671075209, 55.48232776358279],
        [37.65823811822285, 55.496752774565095]
      ],
      'holes': []
    },
    'object_type': [],
    'geo_id': 42,
    'country': 'rus',
}

SAMPLE_TRANSLATION = {
    'translations': {
        'ru': {'form': 'пример'},
        'en': {'form': 'xxx'},
    },
    'is_plural': False
}


@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(LOCALES_SUPPORTED=['en', 'ru'])
def test_get_geoareas(areq_request):

    response = django_test.Client().get(
        '/api/get_geoareas/?geoarea_type=subvention',
        content_type='application/json'
    )
    assert response.status_code == 200, response.content
    assert json.loads(response.content) == [{
        'geometry': {
            'shell': [
                [131.904, 43.2258],
                [132.130, 43.1922],
                [131.887, 42.9299],
                [131.823, 42.9299],
                [131.824, 43.0569],
                [131.904, 43.2258],
            ],
            'holes': []
        },
        'default_point': [
            131.9765,
            43.07785
        ],
        'object_type': [],
        'name': 'vladivostok',
        'geo_id': 75,
        'country': 'rus',
    }]


@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(LOCALES_SUPPORTED=['en', 'ru'])
@pytest.mark.translations([
    ('geoareas', 'sample_area', 'en', '_'),
    ('geoareas', 'sample_area', 'ru', '_'),
])
@pytest.mark.parametrize(
    'geoarea_name,ensure_translation,response_code',
    [
        ('sample_area', True, 200),
        ('moscow', False, 200),
        ('moscow', None, 200),
        ('moscow', True, 400)
    ]
)
def test_set_subvention_geoarea(
        areq_request, patch,
        geoarea_name, ensure_translation, response_code
):

    @patch('taxiadmin.tariff_checks._check_tanker_key')
    @async.inline_callbacks
    def check_tanker_key(keyset, keyset_name, tanker_key):
        if tanker_key != 'sample_area':
            raise tariff_checks.UntranslatedTankerKeyError(
                keyset_name, tanker_key, 'ru'
            )

        async.return_value()

    data = copy(SAMPLE_GEOAREA)
    data['geoarea_type'] = 'subvention'
    data['ticket'] = 'TAXIBACKEND-2'
    data['name'] = geoarea_name
    data['ensure_translation'] = ensure_translation

    response = django_test.Client().post(
        '/api/set_geoarea/',
        json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == response_code


@pytest.mark.asyncenv('blocking')
def test_set_geoarea_unknown_country(areq_request):

    data = copy(SAMPLE_GEOAREA)
    data['geoarea_type'] = 'subvention'
    data['country'] = 'unk'

    response = django_test.Client().post(
        '/api/set_geoarea/',
        json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 400
    assert json.loads(response.content) == {
       'status': 'error',
       'message': 'unknown country: unk',
       'code': 'general',
     }
