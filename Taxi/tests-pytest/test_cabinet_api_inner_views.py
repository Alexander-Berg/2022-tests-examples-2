# coding: utf-8
import json

import pytest

from django import http

from cabinet_api_inner import views as cabinet_api_inner_views


@pytest.mark.parametrize(
    'park_id,expected_status_code,expected_result',
    [
        (
            '1956789619',
            200,
            {
                'clid': '1956789619',
                'contracts': [{
                    'recommended_payment': 809714.33,
                    'threshold_dynamic': -123584.07,
                    'current_balance': 143237.67,
                    'currency': u'руб.',
                    'current_bonus': 35757.6,
                    'commissions': 3131121.43,
                    'external_id': u'48090/15',
                    'is_prepaid': True,
                    'bonus_left': 30648.4
                }],
                'fetched_contracts': [],
                'is_deactivated': False,
                'update': '2018-04-23T14:51:25+0300'
            }
        ),
        (
            '1956789600',
            200,
            {
                'clid': '1956789600',
                'contracts': [],
                'fetched_contracts': [{
                    'is_suspended': True,
                    'external_id': u'49444/16',
                    'is_signed': True
                }],
                'is_deactivated': True,
                'deactivated_reason': 'active contract is absent',
                'update': '2018-04-23T13:50:18+0300',
            }
        ),
        (
            None,
            400,
            {'error': 'Param clid is missing'}
        ),
        (
            'bad_clid',
            404,
            {'error': 'Park with clid bad_clid not found'}
        ),
        (
            '1234567890',
            404,
            {'error': 'Missing billing_client_id in park with clid 1234567890'}
        ),
    ]
)
@pytest.mark.translations([
    ('tariff', 'currency.rub', 'ru', 'руб.')
])
@pytest.mark.filldb
@pytest.inline_callbacks
def test_get_balance(park_id, expected_status_code, expected_result):
    request = http.HttpRequest()
    request.GET['clid'] = park_id
    response = yield cabinet_api_inner_views.get_balance(request)
    assert response.status_code == expected_status_code
    result = json.loads(response.content)
    assert result == expected_result


def _assert_has_just_header(rows):
    assert len(rows) == 1
