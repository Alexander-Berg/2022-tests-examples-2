import dataclasses
import typing as tp

import pytest


@pytest.fixture(name='currency_provider_fixture')
def _currency_provider_fixture(patch):
    @dataclasses.dataclass
    class Settings:
        park_internal_curr: str
        park_external_curr: tp.Optional[str]
        driver_curr: tp.Optional[str]

    settings = Settings('RUB', 'RUB', 'RUB')

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_independent_driver_currency(park_id: str, now):
        return settings.driver_curr

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_park_internal_currency(park_id: str, now):
        return settings.park_internal_curr

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        return settings.park_external_curr

    return settings


async def test_create(
        web_app_client, patch, mock_load_park_info, currency_provider_fixture,
):
    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_affiliation',
    )
    async def _push(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        json={
            'local_driver_id': 'local_driver_id',
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    assert response.status == 201
    data = await response.json()
    assert data.pop('record_id')
    assert data.pop('created_at')
    assert data.pop('modified_at')
    assert data == {
        'park_id': 'park_id',
        'local_driver_id': 'local_driver_id',
        'original_driver_park_id': 'original_driver_park_id',
        'original_driver_id': 'original_driver_id',
        'creator_uid': 'user_id',
        'state': 'new',
    }


async def test_create_nolocal(
        web_app_client, patch, mock_load_park_info, currency_provider_fixture,
):
    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_affiliation',
    )
    async def _push(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        json={
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    assert response.status == 201
    data = await response.json()
    assert data.pop('record_id')
    assert data.pop('created_at')
    assert data.pop('modified_at')
    assert data == {
        'park_id': 'park_id',
        'original_driver_park_id': 'original_driver_park_id',
        'original_driver_id': 'original_driver_id',
        'creator_uid': 'user_id',
        'state': 'new',
    }


async def test_idempotency_violation(
        web_app_client, currency_provider_fixture,
):
    await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        json={
            'local_driver_id': 'local_driver_id',
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    response = await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id2'},
        json={
            'local_driver_id': 'local_driver_id',
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data.pop('record_id')
    assert data.pop('created_at')
    assert data.pop('modified_at')
    assert data == {
        'park_id': 'park_id',
        'local_driver_id': 'local_driver_id',
        'original_driver_park_id': 'original_driver_park_id',
        'original_driver_id': 'original_driver_id',
        'creator_uid': 'user_id',
        'state': 'new',
    }


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz, modified_at_tz)
    VALUES
    ('affiliation_id', 'cancelled',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
async def test_recreate_cancelled(
        web_app_client, patch, mock_load_park_info, currency_provider_fixture,
):
    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_affiliation',
    )
    async def _push(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        json={
            'local_driver_id': 'local_driver_id',
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    assert response.status == 201
    data = await response.json()
    assert data.pop('created_at')
    assert data.pop('modified_at')
    assert data == {
        'record_id': 'affiliation_id',
        'park_id': 'park_id',
        'local_driver_id': 'local_driver_id',
        'original_driver_park_id': 'original_driver_park_id',
        'original_driver_id': 'original_driver_id',
        'creator_uid': 'creator_uid',
        'state': 'new',
    }


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id,
     affiliation_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz,
     transfer_order_number)
    VALUES ('record_id', 'idempotency_token',
     'park_id', 1, 'other', '{"subtype": "misc"}',
     'local_driver_id',
     NULL,
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00',
     'park_id_1')
        """,
    ],
)
async def test_create_had_rent(
        web_app_client, patch, mock_load_park_info, currency_provider_fixture,
):
    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_affiliation',
    )
    async def _push(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        json={
            'local_driver_id': 'local_driver_id',
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    assert response.status == 201
    data = await response.json()
    assert data.pop('record_id')
    assert data.pop('created_at')
    assert data.pop('modified_at')
    assert data == {
        'park_id': 'park_id',
        'local_driver_id': 'local_driver_id',
        'original_driver_park_id': 'original_driver_park_id',
        'original_driver_id': 'original_driver_id',
        'creator_uid': 'user_id',
        'state': 'new',
    }

    response_rent = await web_app_client.get(
        '/v1/park/rents', params={'serial_id': 1, 'park_id': 'park_id'},
    )
    assert response_rent.status == 200
    data = await response_rent.json()
    assert data.pop('terminated_at')
    assert data == {
        'accepted_at': '2020-01-01T03:00:00+03:00',
        'begins_at': '2020-01-01T03:00:00+03:00',
        'asset': {'type': 'other', 'subtype': 'misc'},
        'owner_park_id': 'park_id',
        'owner_serial_id': 1,
        'charging': {'type': 'free'},
        'charging_starts_at': '2020-01-02T03:00:00+03:00',
        'created_at': '2020-01-01T03:00:00+03:00',
        'creator_uid': 'creator_uid',
        'driver_id': 'local_driver_id',
        'ends_at': '2020-01-31T03:00:00+03:00',
        'record_id': 'record_id',
        'state': 'park_terminated',
        'termination_reason': (
            'Terminated by park, due to affiliation creation'
        ),
    }


@pytest.mark.parametrize('ext_curr', ['BYN', None])
async def test_create_different_curr_park(
        web_app_client, currency_provider_fixture, ext_curr,
):
    currency_provider_fixture.park_external_curr = ext_curr

    response = await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        json={
            'local_driver_id': 'local_driver_id',
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data.pop('code') == 'PARK_CONTRACT_CURRENCY_NOT_VALID'


@pytest.mark.parametrize('driver_curr', ['BYN', None])
async def test_create_different_curr(
        web_app_client, currency_provider_fixture, driver_curr,
):
    currency_provider_fixture.driver_curr = driver_curr

    response = await web_app_client.post(
        '/v1/park/affiliations',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        json={
            'local_driver_id': 'local_driver_id',
            'original_driver_park_id': 'original_driver_park_id',
            'original_driver_id': 'original_driver_id',
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data.pop('code') == 'PARK_DRIVER_CURRENCIES_NOT_MATCH'
