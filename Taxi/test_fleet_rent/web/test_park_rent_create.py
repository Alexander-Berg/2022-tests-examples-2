# pylint: disable=too-many-lines
import datetime
import json

import pytest

from fleet_rent.entities import billing as billing_entities
from fleet_rent.entities import order as order_entities


@pytest.fixture(name='mock_int_ext_park_info')
def _mock_int_ext_park_info(patch, park_stub_factory):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(park_id):
        if park_id == 'original_driver_park_id':
            return park_stub_factory(id=park_id, clid='clidClid')
        assert park_id == 'park_id'
        return park_stub_factory(id=park_id, clid='100500')


@pytest.fixture(name='mock_int_ext_billing_data')
def _mock_int_ext_billing_data(patch, park_billing_data_stub_factory):
    @patch(
        'fleet_rent.services.park_info.ParkInfoService.get_park_billing_data',
    )
    async def _get_park_billing_data(clid):
        if clid == 'clidClid':
            return park_billing_data_stub_factory(
                clid=clid,
                inn='inn',
                billing_client_id='bcli2',
                legal_address='legal_address',
                legal_name='legal_name',
            )
        assert clid == '100500'
        return park_billing_data_stub_factory(
            clid=clid,
            inn='inn',
            billing_client_id='bcli',
            legal_address='legal_address',
            legal_name='legal_name',
        )


@pytest.fixture(name='mock_int_ext_park_contract')
def _mock_int_ext_park_contract(patch):
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.get_park_contract',
    )
    async def _get_park_contract(billing_client_data, actual_at):
        if billing_client_data.clid == 'clidClid':
            return billing_entities.Contract(id=124, currency='RUB')
        assert billing_client_data.clid == '100500'
        return billing_entities.Contract(id=222, currency='RUB')


@pytest.fixture(name='mock_park_billing_data_get')
def _mock_park_billing_data_get(patch, park_billing_data_stub_factory):
    @patch(
        'fleet_rent.services.park_info.ParkInfoService.get_park_billing_data',
    )
    async def _get(clid: str):
        return park_billing_data_stub_factory(clid=clid)


@pytest.mark.now('2020-01-01T00:00:00')
async def test_invalid_driver(
        web_app_client, patch, mock_load_park_info, mock_park_billing_data_get,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return False

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data.pop('code') == 'DRIVER_NOT_FOUND'


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
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_invalid_driver_affiliation_external(
        web_app_client, patch, mock_load_park_info, mock_park_billing_data_get,
):
    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_rent',
    )
    async def _push(*args, **kwargs):
        pass

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'some_other_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data.pop('code') == 'DRIVER_NOT_FOUND'


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
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_external(
        web_app_client,
        patch,
        mock_int_ext_park_info,
        mock_int_ext_billing_data,
        mock_int_ext_park_contract,
        web_context,
):
    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_rent',
    )
    async def _push(*args, **kwargs):
        pass

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.driver_can_have_rent_external',
    )
    async def _driver_can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_independent_driver_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_park_internal_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        return 'RUB'

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 201
    data = await response.json()
    rent_id = data.pop('record_id')
    assert rent_id
    assert data.pop('created_at')
    assert not data.pop('accepted_at', None)
    assert data == {
        'affiliation_id': 'affiliation_id',
        'begins_at': '2020-01-01T03:00:00+03:00',
        'asset': {'type': 'car', 'car_id': 'car_id'},
        'owner_park_id': 'park_id',
        'billing_topic': 'taxi/periodic_payment/clid/100500/1',
        'owner_serial_id': 1,
        'charging': {
            'daily_price': '100.321',
            'time': '03:00:00',
            'periodicity': {
                'denominator': 13,
                'numerator': 12,
                'type': 'fraction',
            },
            'type': 'daily',
        },
        'charging_starts_at': '2020-01-01T03:00:00+03:00',
        'creator_uid': 'user_id',
        'driver_id': 'local_driver_id',
        'ends_at': '2020-01-03T03:00:00+03:00',
        'state': 'new',
    }
    rent_times = dict(
        await web_context.pg.master.fetchrow(
            """SELECT created_at, created_at_tz, modified_at, modified_at_tz
            FROM rent.records WHERE record_id = $1""",
            rent_id,
        ),
    )
    utc = datetime.timezone.utc
    assert rent_times['created_at'] == rent_times['modified_at']
    assert rent_times['created_at_tz'] == rent_times['modified_at_tz']
    assert (
        rent_times['created_at'].replace(tzinfo=utc)
        == rent_times['created_at_tz']
    )
    assert (
        rent_times['modified_at'].replace(tzinfo=utc)
        == rent_times['modified_at_tz']
    )
    rent_history = [
        {**x}
        for x in await web_context.pg.master.fetch(
            'SELECT * FROM rent.rent_history WHERE rent_id = $1', rent_id,
        )
    ]
    for rh_ in rent_history:
        assert rh_.pop('created_at')
        assert rh_.pop('modified_at')
        rh_['charging_params'] = json.loads(rh_['charging_params'])
    assert rent_history == [
        {
            'rent_id': rent_id,
            'version': 1,
            'modification_source': '{"uid": "user_id", "kind": "dispatcher"}',
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'driver_id': 'local_driver_id',
            'affiliation_id': 'affiliation_id',
            'title': None,
            'comment': None,
            'balance_notify_limit': None,
            'begins_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'ends_at': datetime.datetime(
                2020, 1, 3, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'asset_type': 'car',
            'asset_params': '{"car_id": "car_id"}',
            'charging_type': 'daily',
            'charging_params': {
                'time': '03:00:00',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'params': {'numerator': 12, 'denominator': 13},
                },
            },
            'charging_starts_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'creator_uid': 'user_id',
            'accepted_at': None,
            'acceptance_reason': None,
            'rejected_at': None,
            'rejection_reason': None,
            'terminated_at': None,
            'termination_reason': None,
            'last_seen_at': None,
            'transfer_order_number': '1',
            'use_event_queue': True,
            'use_arbitrary_entries': True,
            'start_clid': '100500',
        },
    ]


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
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.parametrize('is_park_currency_invalid', [True, False])
async def test_external_invalid_currency(
        web_app_client,
        patch,
        mock_load_park_info,
        mock_park_billing_data_get,
        is_park_currency_invalid,
):
    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_rent',
    )
    async def _push(*args, **kwargs):
        pass

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_independent_driver_currency(park_id: str, now):
        if not is_park_currency_invalid:
            return 'BYN'
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_park_internal_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        if is_park_currency_invalid:
            return 'BYN'
        return 'RUB'

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400


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
    ('affiliation_id', 'accepted',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_external_inactive(
        web_app_client, patch, mock_load_park_info, mock_park_billing_data_get,
):
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'EXTERNAL_RENT_ON_INACTIVE_AFFILIATION',
        'message': 'Can\'t create external rent on inactive affiliation',
        'details': {'current_status': 'accepted'},
    }


@pytest.mark.now('2020-01-01T00:00:00')
async def test_external_not_existing(
        web_app_client, patch, mock_load_park_info, mock_park_billing_data_get,
):
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'EXTERNAL_RENT_ON_NONEXISTENT_AFFILIATION',
        'message': 'Can\'t create external rent on nonexistent affiliation',
    }


@pytest.mark.now('2020-03-01T00:00:00')
async def test_internal(
        web_app_client, mock_load_park_info, patch, web_context,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 201
    data = await response.json()
    rent_id = data.pop('record_id')
    assert rent_id
    assert data.pop('created_at')
    assert data.pop('accepted_at')
    assert data == {
        'acceptance_reason': 'Internal rent - needs no approval',
        'begins_at': '2020-01-01T03:00:00+03:00',
        'asset': {'type': 'car', 'car_id': 'car_id'},
        'owner_park_id': 'park_id',
        'owner_serial_id': 1,
        'charging': {
            'daily_price': '100.321',
            'time': '03:00:00',
            'periodicity': {
                'denominator': 13,
                'numerator': 12,
                'type': 'fraction',
            },
            'type': 'daily',
        },
        'charging_starts_at': '2020-01-01T03:00:00+03:00',
        'creator_uid': 'user_id',
        'driver_id': 'some_driver_id',
        'ends_at': '2020-01-03T03:00:00+03:00',
        'state': 'ended',
    }
    rent_times = dict(
        await web_context.pg.master.fetchrow(
            """SELECT created_at, created_at_tz, modified_at, modified_at_tz
            FROM rent.records WHERE record_id = $1""",
            rent_id,
        ),
    )
    utc = datetime.timezone.utc
    assert rent_times['created_at'] == rent_times['modified_at']
    assert rent_times['created_at_tz'] == rent_times['modified_at_tz']
    assert (
        rent_times['created_at'].replace(tzinfo=utc)
        == rent_times['created_at_tz']
    )
    assert (
        rent_times['modified_at'].replace(tzinfo=utc)
        == rent_times['modified_at_tz']
    )
    rent_history = [
        {**x}
        for x in await web_context.pg.master.fetch(
            'SELECT * FROM rent.rent_history WHERE rent_id = $1', rent_id,
        )
    ]
    for rh_ in rent_history:
        assert rh_.pop('created_at')
        assert rh_.pop('modified_at')
        assert rh_.pop('accepted_at')
        rh_['charging_params'] = json.loads(rh_['charging_params'])
    assert rent_history == [
        {
            'modification_source': '{"uid": "user_id", "kind": "dispatcher"}',
            'acceptance_reason': 'Internal rent - needs no approval',
            'affiliation_id': None,
            'asset_params': '{"car_id": "car_id"}',
            'asset_type': 'car',
            'balance_notify_limit': None,
            'begins_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_params': {
                'time': '03:00:00',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'params': {'numerator': 12, 'denominator': 13},
                },
            },
            'charging_starts_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_type': 'daily',
            'comment': None,
            'creator_uid': 'user_id',
            'driver_id': 'some_driver_id',
            'ends_at': datetime.datetime(
                2020, 1, 3, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'last_seen_at': None,
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'rejected_at': None,
            'rejection_reason': None,
            'rent_id': rent_id,
            'terminated_at': None,
            'termination_reason': None,
            'title': None,
            'transfer_order_number': '1',
            'use_arbitrary_entries': True,
            'use_event_queue': True,
            'version': 1,
            'start_clid': '100500',
        },
    ]


async def test_bad_time(web_app_client, mock_load_park_info, patch):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'other', 'subtype': 'misc'},
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-03T00:00:00',
            'ends_at': '2020-01-01T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {
            'reason': 'Rent should end after it starts',
            'fields': ['begins_at', 'ends_at'],
        },
    }


@pytest.mark.now('2020-01-01T00:00:00')
async def test_idempotency_violation(
        web_app_client, mock_load_park_info, patch, web_context,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {
                'type': 'other',
                'subtype': 'misc',
                'description': 'description',
            },
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'another_user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'other', 'subtype': 'misc'},
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 200
    data = await response.json()
    rent_id = data.pop('record_id')
    assert rent_id
    assert data.pop('created_at')
    assert data.pop('accepted_at')
    assert data == {
        'acceptance_reason': 'Internal rent - needs no approval',
        'asset': {
            'description': 'description',
            'subtype': 'misc',
            'type': 'other',
        },
        'begins_at': '2020-01-01T03:00:00+03:00',
        'charging': {
            'daily_price': '100.321',
            'time': '03:00:00',
            'periodicity': {
                'denominator': 13,
                'numerator': 12,
                'type': 'fraction',
            },
            'type': 'daily',
        },
        'charging_starts_at': '2020-01-01T03:00:00+03:00',
        'creator_uid': 'user_id',
        'driver_id': 'some_driver_id',
        'ends_at': '2020-01-03T03:00:00+03:00',
        'owner_park_id': 'park_id',
        'owner_serial_id': 1,
        'state': 'active',
    }
    rent_history = [
        {**x}
        for x in await web_context.pg.master.fetch(
            'SELECT * FROM rent.rent_history WHERE rent_id = $1', rent_id,
        )
    ]
    for rh_ in rent_history:
        assert rh_.pop('created_at')
        assert rh_.pop('modified_at')
        assert rh_.pop('accepted_at')
        rh_['charging_params'] = json.loads(rh_['charging_params'])
    assert rent_history == [
        {
            'modification_source': '{"uid": "user_id", "kind": "dispatcher"}',
            'acceptance_reason': 'Internal rent - needs no approval',
            'affiliation_id': None,
            'asset_params': (
                '{"subtype": "misc", "description": "description"}'
            ),
            'asset_type': 'other',
            'balance_notify_limit': None,
            'begins_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_params': {
                'time': '03:00:00',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'params': {'numerator': 12, 'denominator': 13},
                },
            },
            'charging_starts_at': datetime.datetime(
                2020, 1, 1, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'charging_type': 'daily',
            'comment': None,
            'creator_uid': 'user_id',
            'driver_id': 'some_driver_id',
            'ends_at': datetime.datetime(
                2020, 1, 3, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'last_seen_at': None,
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'rejected_at': None,
            'rejection_reason': None,
            'rent_id': rent_id,
            'terminated_at': None,
            'termination_reason': None,
            'title': None,
            'transfer_order_number': '1',
            'use_arbitrary_entries': True,
            'use_event_queue': True,
            'version': 1,
            'start_clid': '100500',
        },
    ]


@pytest.mark.now('2020-01-01T00:00:00')
async def test_no_billing_contract(
        web_app_client, patch, mock_load_park_info, mock_park_billing_data_get,
):
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return False

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'PARK_BILLING_CONTRACT_ERROR',
        'message': 'Park has no contract with required service',
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
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_external_no_billing_contract(
        web_app_client,
        patch,
        mock_int_ext_park_info,
        mock_int_ext_billing_data,
        mock_int_ext_park_contract,
):
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.driver_can_have_rent_external',
    )
    async def _driver_can_have_rent(*args, **kwargs):
        return False

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )

    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'AFFILIATION_PARK_BILLING_CONTRACT_ERROR',
        'message': 'Affiliation park has no contract with required service',
    }


@pytest.mark.parametrize('amount', [1, 1000_000])
@pytest.mark.config(
    FLEET_RENT_CHARGING_AMOUNT_LIMITS={
        'lower_limit': '10.00',
        'upper_limit': '100_000.00',
    },
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_charging_out_of_bounds(
        web_app_client, patch, mock_load_park_info, amount,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'local_driver',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': str(amount),
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'CHARGING_AMOUNT_OUT_OF_BOUNDS',
        'message': 'Charging amount must be in range 10.00 to 100000.00',
    }


@pytest.mark.now('2020-01-01T00:00:00')
async def test_internal_limit_exceeded(
        web_app_client, patch, mock_load_park_info,
):
    @patch(
        'fleet_rent.services.confing3.'
        'Configs3Service.get_int_ext_rent_limits',
    )
    async def _get_int_ext_limits(park_info):
        return 0, None

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'local_driver',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'PARK_INTERNAL_LIMIT_EXCEEDED_ERROR',
        'message': 'Park has exceeded it\'s limit on active rents',
        'details': {'limit': 0},
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
    ('affiliation_id', 'active',
     'park_id', 'affiliated_driver',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_external_limit_exceeded(
        web_app_client, patch, mock_load_park_info,
):
    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    @patch(
        'fleet_rent.services.confing3.'
        'Configs3Service.get_int_ext_rent_limits',
    )
    async def _get_int_ext_limits(park_info):
        return None, 0

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'PARK_EXTERNAL_LIMIT_EXCEEDED_ERROR',
        'message': 'Park has exceeded it\'s limit on active rents',
        'details': {'limit': 0},
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
    ('affiliation_id1', 'park_recalled',
     'park_id', 'local_driver_id',
     'original_driver_park_id1', 'original_driver_id1',
     'creator_uid', '2020-01-01+00', '2020-01-01+00'),
    ('affiliation_id2', 'accepted',
     'park_id', 'local_driver_id',
     'original_driver_park_id2', 'original_driver_id2',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_internal_has_affiliation(
        web_app_client, mock_load_park_info, patch,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'INTERNAL_RENT_ON_ACTIVE_AFFILIATION',
        'message': 'Can\'t create internal rent on active affiliation',
    }


@pytest.mark.parametrize(
    'transfer_order_number',
    [
        pytest.param(
            '1',
            marks=pytest.mark.config(
                FLEET_RENT_BILLING_ORDER_ID_FIX={
                    'use_billing_order_id_fix': False,
                },
            ),
            id='dont_use_billing_order_id_fix',
        ),
        pytest.param(
            'park_id_1',
            marks=pytest.mark.config(
                FLEET_RENT_BILLING_ORDER_ID_FIX={
                    'use_billing_order_id_fix': True,
                },
            ),
            id='use_billing_order_id_fix',
        ),
    ],
)
@pytest.mark.now('2020-03-01T00:00:00')
async def test_use_billing_order_id_fix(
        web_app_client,
        web_context,
        mock_load_park_info,
        transfer_order_number,
        patch,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 201
    data = await response.json()
    rent_id = data['record_id']
    res = await web_context.pg_access.rent.internal_get_rent(rent_id)
    assert res.transfer_order_number == transfer_order_number


@pytest.mark.now('2020-03-01T00:00:00')
async def test_rent_flags(
        web_app_client, web_context, mock_load_park_info, patch,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'other', 'subtype': 'deposit'},
            'driver_id': 'some_driver_id',
            'begins_at': '2020-01-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '100.321',
                'total_withhold_limit': '1000',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 201
    data = await response.json()
    rent_id = data['record_id']
    rent = await web_context.pg_access.rent.internal_get_rent(rent_id)
    assert rent.use_event_queue
    assert rent.use_arbitrary_entries
    event = await web_context.pg.master.fetchrow(
        'SELECT * FROM rent.event_queue',
    )
    assert event is not None


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
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_active_days_external(
        web_app_client,
        web_context,
        mock_int_ext_park_info,
        mock_int_ext_billing_data,
        mock_int_ext_park_contract,
        patch,
):
    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_independent_driver_currency',
    )
    async def _get_independent_driver_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_internal_currency',
    )
    async def _get_park_internal_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, now):
        return 'RUB'

    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    @patch(
        'fleet_rent.components.driver_notificator.'
        'ThrottledDriverNotificator.new_rent',
    )
    async def _push(*args, **kwargs):
        pass

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.park_can_have_rent_external',
    )
    async def _can_have_rent(*args, **kwargs):
        return True

    @patch(
        'fleet_rent.services.billing_replication.'
        'BillingReplicationService.driver_can_have_rent_external',
    )
    async def _driver_can_have_rent(*args, **kwargs):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'affiliation_id': 'affiliation_id',
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-02T00:00:00+03:00',
            'ends_at': '2020-01-03T00:00:00+03:00',
            'charging': {'type': 'active_days', 'daily_price': '100.321'},
        },
    )
    assert response.status == 201

    assert not (
        await web_context.pg.master.fetchrow(
            'SELECT * FROM rent.active_day_start_triggers',
        )
    ), 'Event MUST be scheduled only after the rent is accepted'


@pytest.mark.now('2020-01-01T00:00:00')
async def test_active_days_internal_next_day(
        web_app_client, web_context, mock_load_park_info, patch,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-02T00:00:00+03:00',
            'ends_at': '2020-01-03T00:00:00+03:00',
            'charging': {'type': 'active_days', 'daily_price': '100.321'},
        },
    )
    assert response.status == 201
    data = await response.json()
    rent_id = data['record_id']

    trigger_record = dict(
        await web_context.pg.master.fetchrow(
            'SELECT * FROM rent.active_day_start_triggers',
        ),
    )
    assert trigger_record.pop('modified_at')
    assert trigger_record == {
        'rent_id': rent_id,
        'event_number': 1,
        'park_id': 'park_id',
        'driver_id': 'local_driver_id',
        'lower_datetime_bound': datetime.datetime(
            2020, 1, 1, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        'upper_datetime_bound': datetime.datetime(
            2020, 1, 2, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        'triggered_at': None,
        'order_id': None,
    }


@pytest.mark.now('2020-01-01T00:00:00')
async def test_active_days_internal_no_order(
        web_app_client, web_context, mock_load_park_info, patch,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    @patch(
        'fleet_rent.services.driver_orders.'
        'DriverOrdersService.get_last_order',
    )
    async def _get_last_order(
            park_id: str,
            driver_profile_id: str,
            time_begin: datetime.datetime,
            time_end: datetime.datetime,
    ):
        timezone = datetime.timezone(offset=datetime.timedelta(hours=3))
        assert time_begin == datetime.datetime(
            2020, 1, 1, 0, 0, tzinfo=timezone,
        )
        assert time_end == datetime.datetime(2020, 1, 1, 3, 0, tzinfo=timezone)
        return None

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-01T00:00:00+03:00',
            'ends_at': '2020-01-03T00:00:00+03:00',
            'charging': {'type': 'active_days', 'daily_price': '100.321'},
        },
    )
    assert response.status == 201
    data = await response.json()
    rent_id = data['record_id']

    trigger_record = dict(
        await web_context.pg.master.fetchrow(
            'SELECT * FROM rent.active_day_start_triggers',
        ),
    )
    assert trigger_record.pop('modified_at')
    assert trigger_record == {
        'rent_id': rent_id,
        'event_number': 1,
        'park_id': 'park_id',
        'driver_id': 'local_driver_id',
        'lower_datetime_bound': datetime.datetime(
            2019, 12, 31, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        'upper_datetime_bound': datetime.datetime(
            2020, 1, 2, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        'triggered_at': None,
        'order_id': None,
    }


@pytest.mark.now('2020-01-01T12:00:00')
async def test_active_days_internal_with_order(
        web_app_client, web_context, mock_load_park_info, patch,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    @patch(
        'fleet_rent.services.driver_orders.'
        'DriverOrdersService.get_last_order',
    )
    async def _get_last_order(
            park_id: str,
            driver_profile_id: str,
            time_begin: datetime.datetime,
            time_end: datetime.datetime,
    ):
        timezone = datetime.timezone(offset=datetime.timedelta(hours=3))
        assert time_begin == datetime.datetime(
            2020, 1, 1, 0, 0, tzinfo=timezone,
        )
        assert time_end == datetime.datetime(
            2020, 1, 1, 15, 0, tzinfo=timezone,
        )
        return order_entities.LastOrderInfo(
            order_id='alias_id',
            complete_at=datetime.datetime.fromisoformat(
                '2020-01-01T09:00:00+01:00',
            ),
        )

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'local_driver_id',
            'begins_at': '2020-01-01T00:00:00+03:00',
            'ends_at': '2020-01-03T00:00:00+03:00',
            'charging': {'type': 'active_days', 'daily_price': '100.321'},
        },
    )
    assert response.status == 201
    data = await response.json()
    rent_id = data['record_id']

    trigger_record = dict(
        await web_context.pg.master.fetchrow(
            'SELECT * FROM rent.active_day_start_triggers',
        ),
    )
    assert trigger_record.pop('modified_at')
    assert trigger_record == {
        'rent_id': rent_id,
        'event_number': 1,
        'park_id': 'park_id',
        'driver_id': 'local_driver_id',
        'lower_datetime_bound': datetime.datetime(
            2019, 12, 31, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        'upper_datetime_bound': datetime.datetime(
            2020, 1, 2, 21, 0, tzinfo=datetime.timezone.utc,
        ),
        'triggered_at': datetime.datetime(
            2020, 1, 1, 8, 0, tzinfo=datetime.timezone.utc,
        ),
        'order_id': 'alias_id',
    }

    events = dict(
        await web_context.pg.master.fetchrow('SELECT * FROM rent.event_queue'),
    )
    assert events.pop('modified_at')
    assert events == {
        'event_at': datetime.datetime(
            2020, 1, 1, 8, 0, tzinfo=datetime.timezone.utc,
        ),
        'event_number': 1,
        'executed_at': None,
        'rent_id': rent_id,
    }


@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.config(FLEET_RENT_CHARGING_START_DAYS_BACK_LIMIT=180)
async def test_charging_start_days_back_limit(
        web_app_client, patch, mock_load_park_info,
):
    @patch(
        'fleet_rent.services.driver_info.'
        'DriverInfoService.is_driver_exists',
    )
    async def _is_driver_exists(*args):
        return True

    response = await web_app_client.post(
        '/v1/park/rents',
        params={'park_id': 'park_id', 'user_id': 'user_id'},
        headers={'X-Idempotency-Token': 'idempotency_token'},
        json={
            'asset': {'type': 'car', 'car_id': 'car_id'},
            'driver_id': 'local_driver',
            'begins_at': '2019-07-01T00:00:00',
            'ends_at': '2020-01-03T00:00:00',
            'charging': {
                'type': 'daily',
                'daily_price': '10',
                'periodicity': {
                    'type': 'fraction',
                    'numerator': 12,
                    'denominator': 13,
                },
            },
        },
    )
    assert response.status == 400
    data = await response.json()
    assert data == {
        'code': 'CHARGING_START_NOT_VALID',
        'message': 'Charging start must not be earlier than 180 days from the current date',  # noqa: E501
    }
