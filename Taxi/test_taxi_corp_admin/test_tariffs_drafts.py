# pylint:disable=redefined-outer-name

import datetime

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)


def strftime(item: datetime.datetime):
    return item.strftime('%Y-%m-%dT%H:%M:%SZ')


@pytest.fixture
def validate_tariff_mock(patch):
    @patch('taxi_corp_admin.api.common.tariffs.validate_tariff')
    async def _validate_tariff(request, tariff, countries, areas):
        return []

    return _validate_tariff


@pytest.mark.now(NOW.isoformat())
async def test_check(
        taxi_corp_admin_client, validate_tariff_mock, territories_mock,
):
    data = {
        'country': 'rus',
        'home_zone': 'test_zone',
        'name': 'Test tariff',
        'classes': [
            {
                'name': 'econom',
                'disable_surge': True,
                'policy': {
                    'multiplier': 1.1,
                    'category': None,
                    'transfer': None,
                },
                'inherited': True,
            },
        ],
    }

    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/draft/check', json=data,
    )

    assert response.status == 200
    assert await response.json() == {
        'data': data,
        'change_doc_id': 'corp_tariff_Test tariff',
        'diff': {
            'current': {},
            'new': {
                'classes': [
                    {
                        'inherited': True,
                        'name': 'econom',
                        'disable_surge': True,
                        'policy': {
                            'category': None,
                            'multiplier': 1.1,
                            'transfer': None,
                        },
                    },
                ],
                'country': 'rus',
                'home_zone': 'test_zone',
                'name': 'Test tariff',
            },
        },
    }

    assert len(validate_tariff_mock.calls) == 1


@pytest.mark.now(NOW.isoformat())
async def test_apply_create(
        db,
        patch,
        taxi_corp_admin_client,
        validate_tariff_mock,
        territories_mock,
):
    @patch('taxi_corp_admin.api.common.tariffs.create_id')
    def _create_id():
        return 'test_id'

    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/draft/apply',
        json={
            'country': 'rus',
            'home_zone': 'test_zone',
            'name': 'Test tariff',
            'disable_paid_supply_price': True,
            'classes': [
                {
                    'name': 'econom',
                    'disable_surge': True,
                    'policy': {
                        'multiplier': 1.1,
                        'category': None,
                        'transfer': None,
                    },
                    'inherited': True,
                },
            ],
            'in_use': True,
            'usage_count': 1,
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    assert len(validate_tariff_mock.calls) == 1

    new_tariff = await db.corp_tariffs.find_one(
        {'_id': 'test_id'}, projection={'created': False, 'updated': False},
    )
    assert new_tariff == {
        'country': 'rus',
        '_id': 'test_id',
        'disable_paid_supply_price': True,
        'classes': [
            {
                'name': 'econom',
                'disable_surge': True,
                'policy': {
                    'multiplier': 1.1,
                    'category': None,
                    'transfer': None,
                },
                'inherited': True,
            },
        ],
        'date_from': NOW,
        'date_to': None,
        'home_zone': 'test_zone',
        'name': 'Test tariff',
        'tariff_series_id': 'test_id',
    }


@pytest.mark.now(NOW.isoformat())
async def test_apply_update(
        db,
        patch,
        taxi_corp_admin_client,
        validate_tariff_mock,
        territories_mock,
):
    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/draft/apply',
        json={
            'country': 'rus',
            'home_zone': 'balaha',
            'name': 'Однозонный Балаха 40%',
            'disable_paid_supply_price': False,
            'classes': [
                {
                    'name': 'econom',
                    'disable_surge': True,
                    'policy': {
                        'multiplier': 1.4,
                        'category': None,
                        'transfer': None,
                    },
                    'inherited': True,
                },
            ],
            'tariff_series_id': 'balaha',
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    assert len(validate_tariff_mock.calls) == 1

    old_tariff, new_tariff = (
        await db.corp_tariffs.find(
            {'tariff_series_id': 'balaha'},
            projection={'created': False, 'updated': False},
        )
        .sort('date_from', 1)
        .to_list(None)
    )

    assert old_tariff == {
        '_id': 'balaha',
        'country': 'rus',
        'classes': [
            {
                'name': 'econom',
                'disable_surge': True,
                'policy': {
                    'multiplier': 1.3,
                    'category': None,
                    'transfer': None,
                },
                'inherited': True,
            },
        ],
        'date_from': NOW - datetime.timedelta(days=1),
        'date_to': NOW,
        'home_zone': 'balaha',
        'name': 'Однозонный Балаха 30%',
        'tariff_series_id': 'balaha',
    }

    assert new_tariff['_id'] != 'balaha'
    del new_tariff['_id']

    assert new_tariff == {
        'country': 'rus',
        'disable_paid_supply_price': False,
        'classes': [
            {
                'name': 'econom',
                'disable_surge': True,
                'policy': {
                    'multiplier': 1.4,
                    'category': None,
                    'transfer': None,
                },
                'inherited': True,
            },
        ],
        'date_from': NOW,
        'date_to': None,
        'home_zone': 'balaha',
        'name': 'Однозонный Балаха 40%',
        'tariff_series_id': 'balaha',
    }


@pytest.mark.parametrize(
    'filename', ['test_tariff_custom.json', 'test_tariff_inherited.json'],
)
async def test_schema(
        load_json,
        taxi_corp_admin_client,
        territories_mock,
        validate_tariff_mock,
        filename,
):
    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/draft/check', json=load_json(filename),
    )
    assert response.status == 200, await response.json()
