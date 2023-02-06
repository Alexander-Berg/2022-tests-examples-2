# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import test as django_test
import pytest

from taxi.core import db


@pytest.mark.config(EXTRA_EXAMS_INFO={
    'business': {
            'description': 'Допуск к классу Бизнес',
            'requires': [{'course': 'base', 'min_result': 3}],
            'permission': ['vip']
        },
        'kids': {
            'description': 'Допуск к классу Детский',
            'requires': [{'course': 'base', 'min_result': 3}],
            'permission': ['kids']
         }
})
@pytest.mark.parametrize('payload,code,expected', [
    (
        {
            'licenses': ['test_license'],
            'city': 'moscow',
            'scores': [
                {'course': 'kids', 'result': 1},
                {'course': 'business', 'result': 5}
            ]
        }, 200,
        [
            {
                'city': 'moscow',
                'center': 'admin',
                'license': 'TEST_LICENSE',
                'license_id': 'TEST_LICENSE_pd_id',
                'course': 'kids',
                'updated_by': 'dmkurilov',
                'result': 1,
            },
            {
                'city': 'moscow',
                'center': 'admin',
                'license': 'TEST_LICENSE',
                'license_id': 'TEST_LICENSE_pd_id',
                'course': 'business',
                'updated_by': 'dmkurilov',
                'result': 5,
            },
        ]
    ),
    (
        {
            'licenses': ['test_license', 'undefined'],
            'city': 'moscow',
            'scores': [
                {'course': 'kids', 'result': 1},
                {'course': 'business', 'result': 5}
            ]
        }, 404, None
    ),
    (
        {
            'licenses': ['test_license'],
            'city': 'moscow',
            'scores': [
                {'course': 'fake', 'result': 1},
                {'course': 'business', 'result': 5}
            ]
        }, 400, None
    ),
    (
        {
            'licenses': ['test_license'],
            'city': 'moscow',
            'scores': [
                {'course': 'kids', 'result': 1},
                {'course': 'business', 'result': 1000}
            ]
        }, 400, None
    ),
    (
        {
            'licenses': [],
            'city': 'moscow',
            'scores': [
                {'course': 'kids', 'result': 1},
                {'course': 'business', 'result': 5}
            ]
        }, 400, None
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_extra_exams(patch, payload, code, expected):
    @patch('taxi.internal.personal.find')
    def license_find(data_type, value, log_extra=None):
        return {'id': value + '_pd_id', 'license': value}

    response = django_test.Client().post(
        '/api/driver_card/bulk_exams/', json.dumps(payload),
        'application/json')
    assert response.status_code == code
    if code == 200:
        results = yield db.exam_results.find({'license': 'TEST_LICENSE'}).run()
        for result in results:
            exam_results_id = result.pop('_id')
            assert isinstance(exam_results_id, (str, unicode))
            result.pop('updated')
            result.pop('exam_date')
        assert sorted(results) == sorted(expected)
