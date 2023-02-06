# pylint:disable=redefined-outer-name

import datetime
from unittest import mock

import pytest

from taxi_corp_admin import web

NOW = datetime.datetime.utcnow().replace(microsecond=0)


@pytest.fixture
def web_request(db, taxi_corp_admin_app, taxi_corp_admin_client):
    return mock.MagicMock(db=db, app=taxi_corp_admin_app)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('_id', (None, 'client_tariff_plan_id_2'))
@pytest.mark.parametrize(
    'date_from, date_to, expected',
    [
        # date_from < NOW
        (
            NOW - datetime.timedelta(seconds=1),
            NOW + datetime.timedelta(seconds=1),
            {
                'date_from': [
                    web.errors.Error('date_from must be greater then now'),
                ],
            },
        ),
        # date_to < date_from
        (
            NOW + datetime.timedelta(seconds=2),
            NOW + datetime.timedelta(seconds=1),
            {
                'date_to': [
                    web.errors.Error('date_to must be greater then date_from'),
                ],
            },
        ),
    ],
)
async def test_check_invalid_dates(
        web_request, _id, date_from, date_to, expected,
):
    from taxi_corp_admin.api.common import client_tariff_plans

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id=_id,
        data={
            'client_id': 'client_id_1',
            'date_from': date_from,
            'date_to': date_to,
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    assert details == expected


@pytest.mark.now(NOW.isoformat())
async def test_create_tp_not_exists(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    date_from = NOW + datetime.timedelta(days=1)
    date_to = NOW + datetime.timedelta(days=2)

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id=None,
        data={
            'client_id': 'client_id_1',
            'date_from': date_from,
            'date_to': date_to,
            'description': 'Завтра-послезавтра',
            'tariff_plan_series_id': 'not_exists',
        },
    )

    assert details == {
        'tariff_plan_series_id': [web.errors.Error('Tariff plan not found')],
    }


@pytest.mark.now(NOW.isoformat())
async def test_create_client_not_exists(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    date_from = NOW + datetime.timedelta(days=1)
    date_to = NOW + datetime.timedelta(days=2)

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id=None,
        data={
            'client_id': 'not_exists',
            'date_from': date_from,
            'date_to': date_to,
            'description': 'Завтра-послезавтра',
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )

    assert details == {'client_id': [web.errors.Error('Client not found')]}


@pytest.mark.now(NOW.isoformat())
async def test_create_different_country(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    date_from = NOW + datetime.timedelta(days=1)
    date_to = NOW + datetime.timedelta(days=2)

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id=None,
        data={
            'client_id': 'client_id_1',
            'date_from': date_from,
            'date_to': date_to,
            'description': 'Завтра-послезавтра',
            'tariff_plan_series_id': 'tariff_plan_series_id_4',
        },
    )

    assert details == {
        'tariff_plan_series_id': [
            web.errors.Error(
                'Client\'s country "rus" doesn\'t match '
                'tariff plan\'s country "kaz"',
            ),
        ],
    }


@pytest.mark.now(NOW.isoformat())
async def test_update_different_country(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    date_from = NOW + datetime.timedelta(days=1)
    date_to = NOW + datetime.timedelta(days=2)

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id='client_tariff_plan_id_2',
        data={
            'client_id': 'client_id_1',
            'date_from': date_from,
            'date_to': date_to,
            'description': 'Завтра-послезавтра',
            'tariff_plan_series_id': 'tariff_plan_series_id_4',
        },
    )

    assert details == {
        'tariff_plan_series_id': [
            web.errors.Error(
                'Client\'s country "rus" doesn\'t match '
                'tariff plan\'s country "kaz"',
            ),
        ],
    }


@pytest.mark.now(NOW.isoformat())
async def test_update_past_plan(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id='client_tariff_plan_id_0',
        data={
            'client_id': 'client_id_2',
            'date_from': NOW,
            'date_to': NOW,
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
            'description': 'Новое описание',
        },
    )

    assert details == {
        'client_id': [web.errors.Error('can not change field client_id')],
        'date_from': [web.errors.Error('can not change field date_from')],
        'date_to': [web.errors.Error('can not change field date_to')],
        'tariff_plan_series_id': [
            web.errors.Error('can not change field tariff_plan_series_id'),
        ],
    }


@pytest.mark.now(NOW.isoformat())
async def test_update_now_plan(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id='client_tariff_plan_id_1',
        data={
            'client_id': 'client_id_2',
            'date_from': NOW,
            'date_to': NOW + datetime.timedelta(hours=12),
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
            'description': 'Новое описание',
        },
    )

    assert details == {
        'client_id': [web.errors.Error('can not change field client_id')],
        'date_from': [web.errors.Error('can not change field date_from')],
        'tariff_plan_series_id': [
            web.errors.Error('can not change field tariff_plan_series_id'),
        ],
    }


@pytest.mark.now(NOW.isoformat())
async def test_update_nothing(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    date_from = NOW + datetime.timedelta(days=2)
    date_to = NOW + datetime.timedelta(days=4)

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id='client_tariff_plan_nothing',
        data={
            'client_id': 'client_id_1',
            'date_from': date_from,
            'date_to': date_to,
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
            'description': 'Начинает послезатра, действует 2 дня',
        },
    )

    assert details == {'id': [web.errors.Error('Client plan not found')]}


@pytest.mark.now(NOW.isoformat())
async def test_update_tp_not_exists(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    date_from = NOW + datetime.timedelta(days=2)
    date_to = NOW + datetime.timedelta(days=4)

    details = await client_tariff_plans.validate_client_tariff_plan(
        web_request,
        _id='client_tariff_plan_id_2',
        data={
            'client_id': 'client_id_1',
            'date_from': date_from,
            'date_to': date_to,
            'tariff_plan_series_id': 'not_exists',
            'description': 'Начинает послезатра, действует 2 дня',
        },
    )

    assert details == {
        'tariff_plan_series_id': [web.errors.Error('Tariff plan not found')],
    }


@pytest.mark.now(NOW.isoformat())
async def test_delete_not_found(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    details = await client_tariff_plans.check_remove_client_tariff_plan(
        web_request, _id='client_tariff_plan_id_not_exists',
    )

    assert details == {'id': [web.errors.Error('Client plan not found')]}


@pytest.mark.now(NOW.isoformat())
async def test_delete_plan_in_past(web_request):
    from taxi_corp_admin.api.common import client_tariff_plans

    details = await client_tariff_plans.check_remove_client_tariff_plan(
        web_request, _id='client_tariff_plan_id_1',
    )

    assert details == {'id': [web.errors.Error('Client plan in the past')]}
