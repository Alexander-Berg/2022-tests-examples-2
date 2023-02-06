# coding: utf-8
from __future__ import unicode_literals

import json

import pytest
from django import test as django_test

from taxiexams.api import phone


@pytest.mark.config(
    EXAMS_BRAND_TO_ROUTE_MAPPING=[
        {
            'brand': 'Yandex.Eda',
            'route': 'sms_routes.eda',
        },
        {
            'brand': 'Яндекс.Такси',
            'route': 'sms_routes.taxi',
        }
    ],
)
@pytest.mark.parametrize('data,expected_route', [
    (
      {
        u'locale': u'ru',
        u'phone': u'+7123456789',
        u'client_ip': u'192.168.0.1'
      },
      u'sms_routes.taxi',
    ),
    (
      {
        u'locale': u'ru',
        u'phone': u'+7123456789',
        u'client_ip': u'192.168.0.1',
        u'brand': 'Yandex.Eda'
      },
      u'sms_routes.eda',
    ),
    (
      {
        u'locale': u'ru',
        u'phone': u'+7123456789',
        u'client_ip': u'192.168.0.1',
        u'brand': 'Яндекс.Такси'
      },
      u'sms_routes.taxi',
    ),
])
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_route_and_brand(patch, data, expected_route):
    @patch('taxi.external.passport_internal.phone_confirm_submit')
    def get_status(number, display_language, client_ip,
                   tvm_src_service, route=None, country=None,
                   track_id=None, consumer=None, log_extra=None):
        if route:
            assert expected_route == route
        return {'status': 'ok',
                'track_id': 'test_track'}

    request = django_test.RequestFactory().post(
        path='',
        data=json.dumps(data),
        content_type='application/json'
    )
    response = yield phone.phone_confirm_submit(request)
    assert response.status_code == 200
