# pylint:disable=redefined-outer-name

import datetime

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)


def strftime(item: datetime.datetime):
    return item.strftime('%Y-%m-%dT%H:%M:%SZ')


@pytest.fixture
def validate_tariff_plan_mock(patch):
    @patch('taxi_corp_admin.api.common.tariff_plans.validate_tariff_plan')
    async def _validate_tariff_plan(
            request, tariff_plan, tariff_plan_series_id,
    ):
        return []

    return _validate_tariff_plan


@pytest.mark.now(NOW.isoformat())
async def test_check(taxi_corp_admin_client, validate_tariff_plan_mock):
    data = {
        'country': 'rus',
        'disable_fixed_price': True,
        'disable_tariff_fallback': False,
        'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
        'application_multipliers': [
            {'application': 'callcenter', 'multiplier': 100},
        ],
        'name': 'Тарифный план 1',
        'multiplier': 1.2,
    }

    response = await taxi_corp_admin_client.post(
        '/v1/tariff-plans/draft/check', json=data,
    )

    json_response = await response.json()
    assert response.status == 200, json_response
    assert json_response == {
        'data': data,
        'change_doc_id': 'corp_tariff_plan_Тарифный план 1',
    }

    assert len(validate_tariff_plan_mock.calls) == 1


@pytest.mark.now(NOW.isoformat())
async def test_apply_create(
        db, patch, taxi_corp_admin_client, validate_tariff_plan_mock,
):
    @patch('taxi_corp_admin.api.common.tariff_plans.create_id')
    def _create_id():
        return 'test_id'

    response = await taxi_corp_admin_client.post(
        '/v1/tariff-plans/draft/apply',
        json={
            'country': 'rus',
            'disable_fixed_price': True,
            'disable_tariff_fallback': True,
            'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
            'application_multipliers': [
                {'application': 'callcenter', 'multiplier': 100},
            ],
            'name': 'Тарифный план 1',
            'multiplier': 1.2,
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    assert len(validate_tariff_plan_mock.calls) == 1

    new_plan = await db.corp_tariff_plans.find_one(
        {'tariff_plan_series_id': 'test_id'},
        projection={'created': False, 'updated': False},
    )

    assert new_plan == {
        '_id': 'test_id',
        'country': 'rus',
        'disable_fixed_price': True,
        'disable_tariff_fallback': True,
        'tariff_plan_series_id': 'test_id',
        'date_from': NOW,
        'date_to': None,
        'name': 'Тарифный план 1',
        'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
        'application_multipliers': [
            {'application': 'callcenter', 'multiplier': 100},
        ],
        'multiplier': 1.2,
    }


@pytest.mark.now(NOW.isoformat())
async def test_apply_update(
        db, taxi_corp_admin_client, validate_tariff_plan_mock,
):
    response = await taxi_corp_admin_client.post(
        '/v1/tariff-plans/draft/apply',
        json={
            'country': 'rus',
            'disable_fixed_price': True,
            'disable_tariff_fallback': True,
            'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
            'application_multipliers': [
                {'application': 'callcenter', 'multiplier': 100},
            ],
            'name': 'Тарифный план 2 (новый)',
            'tariff_plan_series_id': 'tariff_plan_series_id_2',
            'multiplier': 1.3,
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    assert len(validate_tariff_plan_mock.calls) == 1

    old_tariff_plan, new_tariff_plan = (
        await db.corp_tariff_plans.find(
            {'tariff_plan_series_id': 'tariff_plan_series_id_2'},
            projection={'created': False, 'updated': False},
        )
        .sort('date_from', 1)
        .to_list(None)
    )

    assert old_tariff_plan == {
        '_id': 'tariff_plan_2',
        'country': 'rus',
        'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
        'name': 'Тарифный план 2',
        'date_from': NOW - datetime.timedelta(days=1),
        'date_to': NOW,
        'default_tariff_series_id': 'moscow',
        'disable_fixed_price': False,
        'disable_tariff_fallback': False,
        'tariff_plan_series_id': 'tariff_plan_series_id_2',
        'multiplier': 1,
    }

    assert new_tariff_plan['_id'] != 'tariff_plan_2'
    del new_tariff_plan['_id']

    assert new_tariff_plan == {
        'country': 'rus',
        'disable_fixed_price': True,
        'disable_tariff_fallback': True,
        'zones': [{'zone': 'moscow', 'tariff_series_id': 'moscow'}],
        'application_multipliers': [
            {'application': 'callcenter', 'multiplier': 100},
        ],
        'name': 'Тарифный план 2 (новый)',
        'date_from': NOW,
        'date_to': None,
        'tariff_plan_series_id': 'tariff_plan_series_id_2',
        'multiplier': 1.3,
    }
