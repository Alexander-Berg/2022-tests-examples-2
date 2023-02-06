# pylint: disable=redefined-outer-name
import datetime

import pytest

from taxi.util import dates as dates_utils

NOW = datetime.datetime.utcnow().replace(microsecond=0)


def timedelta_dec(**kwargs):
    return dates_utils.localize(NOW - datetime.timedelta(**kwargs)).isoformat()


def timedelta_inc(**kwargs):
    return dates_utils.localize(NOW + datetime.timedelta(**kwargs)).isoformat()


@pytest.mark.now(NOW.isoformat())
async def test_client_tariff_plan_current(web_app_client, cache_shield):
    params = {'client_id': 'client_id_1'}

    response = await web_app_client.get(
        '/v1/client_tariff_plan/current', params=params,
    )
    data = await response.json()

    assert response.status == 200, data
    assert data == {
        'client_id': 'client_id_1',
        'date_from': timedelta_dec(hours=12),
        'date_to': timedelta_inc(hours=12),
        'tariff_plan': {
            'disable_fixed_price': False,
            'disable_tariff_fallback': False,
            'multiplier': 2,
            'name': 'Тарифный план 2',
            'country': 'rus',
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
            'zones': [{'tariff_series_id': 'moscow', 'zone': 'moscow'}],
        },
        'tariff_plan_series_id': 'tariff_plan_series_id_2',
    }


@pytest.mark.parametrize(
    'params, expected',
    [
        (
            {'client_id': 'unknown', 'service': 'taxi'},
            {
                'code': 'NOT_FOUND',
                'message': 'Not found',
                'details': {'reason': 'Client tariff plan not found'},
            },
        ),
    ],
)
async def test_client_tariff_current_failed(
        web_app_client, cache_shield, params, expected,
):
    response = await web_app_client.get(
        '/v1/client_tariff_plan/current', params=params,
    )
    data = await response.json()

    assert response.status == 404, data
    assert data == expected
