import datetime as dt
import decimal as dec
import typing as tp

import pytest

from fleet_rent.entities import asset as asset_entities
from fleet_rent.entities import charging as charging_entities
from fleet_rent.entities import daily_periodicity as periodicity_ent
from fleet_rent.entities import rent as rent_entities
from fleet_rent.use_cases import park_rent_modify as prm

_ASSETS = (
    asset_entities.AssetCar(car_id='car_id', car_copy_id='copy_id'),
    asset_entities.AssetOther(subtype='chair', description='chair desc'),
    asset_entities.AssetOther(subtype='device', description=None),
    asset_entities.AssetOther(subtype='misc', description='misc desc'),
    asset_entities.AssetOther(subtype='deposit', description=None),
)

_ASSET_JSONS = (
    {'type': 'car', 'car_id': 'car_id', 'car_copy_id': 'copy_id'},
    {'type': 'other', 'subtype': 'chair', 'description': 'chair desc'},
    {'type': 'other', 'subtype': 'device'},
    {'type': 'other', 'subtype': 'misc', 'description': 'misc desc'},
    {'type': 'other', 'subtype': 'deposit'},
)

_CHARGINGS = (
    charging_entities.ChargingDaily(
        starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        finishes_at=None,
        daily_price=dec.Decimal(100),
        periodicity=periodicity_ent.DailyPeriodicityConstant(),
        total_withhold_limit=None,
        time=dt.time(7, 0),
    ),
    charging_entities.ChargingDaily(
        starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        finishes_at=None,
        daily_price=dec.Decimal(100),
        periodicity=periodicity_ent.DailyPeriodicityISOWeekDays(
            isoweekdays=(1, 2, 3),
        ),
        total_withhold_limit=None,
        time=dt.time(7, 0),
    ),
    charging_entities.ChargingActiveDays(
        starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        finishes_at=None,
        daily_price=dec.Decimal(100),
        total_withhold_limit=None,
    ),
    charging_entities.ChargingActiveDays(
        starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        finishes_at=None,
        daily_price=dec.Decimal(100),
        total_withhold_limit=None,
    ),
    charging_entities.ChargingActiveDays(
        starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        finishes_at=None,
        daily_price=dec.Decimal(100),
        total_withhold_limit=dec.Decimal(2000),
    ),
)

_CHARGING_JSONS = (
    {
        'type': 'daily',
        'daily_price': '100',
        'periodicity': {'type': 'constant'},
        'time': '07:00:00',
    },
    {
        'type': 'daily',
        'daily_price': '100',
        'periodicity': {'type': 'isoweekdays', 'isoweekdays': [1, 2, 3]},
        'time': '07:00:00',
    },
    {'type': 'active_days', 'daily_price': '100'},
    {'type': 'active_days', 'daily_price': '100'},
    {
        'type': 'active_days',
        'daily_price': '100',
        'total_withhold_limit': '2000',
    },
)


@pytest.mark.parametrize(
    'm_asset,m_charging, js_asset, js_charging',
    zip(_ASSETS, _CHARGINGS, _ASSET_JSONS, _CHARGING_JSONS),
)
async def test_ok(
        web_app_client, patch, m_asset, m_charging, js_asset, js_charging,
):
    @patch('fleet_rent.use_cases.park_rent_modify.ParkRentModify.modify')
    async def _modify(
            modification_source: rent_entities.RentModificationSource,
            rent_id: str,
            park_id: str,
            title: tp.Optional[str],
            comment: tp.Optional[str],
            charging: charging_entities.Charging,
            asset: asset_entities.Asset,
    ) -> rent_entities.Rent:
        assert asset == m_asset
        assert charging == m_charging
        assert rent_id == 'basic_rent_id'
        assert park_id == 'park_id5'
        assert (
            modification_source
            == rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='123', ticket_provider='yandex',
            )
        )
        return rent_entities.Rent(
            record_id='basic_rent_id',
            owner_park_id='park_id5',
            owner_serial_id=1,
            driver_id='driver_id',
            affiliation_id=None,
            title='new title',
            comment='new comment',
            balance_notify_limit=None,
            begins_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
            ends_at=None,
            asset=asset,
            charging=charging,
            charging_starts_at=dt.datetime(
                2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc,
            ),
            creator_uid='creator_uid',
            created_at=dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc),
            accepted_at=dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc),
            acceptance_reason=None,
            rejected_at=None,
            rejection_reason=None,
            terminated_at=None,
            termination_reason=None,
            last_seen_at=None,
            transfer_order_number='park_id_1',
            use_event_queue=True,
            use_arbitrary_entries=True,
            start_clid=None,
        )

    response = await web_app_client.post(
        '/fleet/rent/v1/park/rents/modification?rent_id=basic_rent_id',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': 'park_id5',
            'X-Real-IP': '127.0.0.1',
        },
        json={
            'asset': js_asset,
            'charging': js_charging,
            'begins_at': '2020-01-01T07:00+00:00',
        },
    )

    assert response.status == 200, await response.text()
    assert await response.json() == {
        'accepted_at': '2020-01-01T03:00:00+03:00',
        'asset': js_asset,
        'begins_at': '2020-01-01T10:00:00+03:00',
        'charging': js_charging,
        'comment': 'new comment',
        'created_at': '2020-01-01T03:00:00+03:00',
        'driver_id': 'driver_id',
        'owner_park_id': 'park_id5',
        'owner_serial_id': 1,
        'rent_id': 'basic_rent_id',
        'state': 'active',
        'title': 'new title',
    }


@pytest.mark.parametrize(
    'exception_,error_code,json_error',
    [
        (prm.UnhandleableError(), 500, None),
        (
            prm.RentNotFoundError(),
            404,
            {'code': '404', 'message': 'Rent not found in park'},
        ),
        (
            prm.UnmodifableRentError(),
            409,
            {
                'code': 'UNMODIFIABLE_RENT',
                'message': 'This rent cannot be modified',
            },
        ),
        (
            prm.IndependentDriverError(),
            409,
            {
                'code': 'NOT_PARK_DRIVER',
                'message': 'Only internal rents is modifiable',
            },
        ),
        (
            prm.TerminatedRentError(),
            409,
            {
                'code': 'TERMINATED_RENT',
                'message': 'Finished rents cannot be modified',
            },
        ),
        (
            prm.TimeParameterNotSetError(),
            400,
            {
                'code': 'TIME_PARAMETER_MISSED',
                'message': 'time parameter in charging is required',
            },
        ),
        (
            prm.BeginEndTimesNotValidError(),
            400,
            {
                'code': 'BEGIN_END_NOT_VALID',
                'message': 'ends_at must be bigger than begins_at',
            },
        ),
        (
            prm.BeginTimeAndChargingTimeMismatch(),
            400,
            {
                'code': 'TIME_PARAMETER_NOT_MATCHING_BEGINS_AT',
                'message': (
                    'If begins_at in future, time parameter '
                    'must have same time in park timezone'
                ),
            },
        ),
        (
            prm.BeginTimeCannotBeChangedError(),
            409,
            {
                'code': 'BEGIN_AT_CANNOT_CHANGE',
                'message': 'Cannot change begins_at if rent already started',
            },
        ),
        (
            prm.EndsAtOutOfRangeError(),
            409,
            {
                'code': 'ENDS_AT_OUT_OF_RANGE',
                'message': 'Should use termination to stop rent early',
            },
        ),
        (
            prm.ScheduleChangeUnavailableError(),
            409,
            {
                'code': 'WAIT_TRANSACTIONS_BEFORE_SCHEDULE_CHANGE',
                'message': 'Either some old transactions unprocessed or new transaction would run soon',  # noqa: E501
            },
        ),
        (
            prm.AssetTypeEditError(),
            409,
            {
                'code': 'ASSET_TYPE_CANNOT_BE_CHANGED',
                'message': 'Asset cannot change type',
            },
        ),
        (
            prm.AssetCarInvalidError(),
            409,
            {'code': 'CAR_NOT_FOUND', 'message': 'Failed to find car in park'},
        ),
        (
            prm.DepositChargingMismatchError(),
            400,
            {
                'code': 'DEPOSIT_PARAMS_MISMATCH',
                'message': 'Deposit charging must have deposit asset and total_withhold_limit set',  # noqa: E501
            },
        ),
        (
            prm.DepositChargingPriceError(),
            400,
            {
                'code': 'DEPOSIT_PRICE_CANNOT_CHANGE',
                'message': 'Deposit charging must keep old price',
            },
        ),
        (
            prm.DepositChargingLimitError(),
            400,
            {
                'code': 'DEPOSIT_LIMIT_CANNOT_CHANGE',
                'message': 'Deposit charging must keep old limit',
            },
        ),
        (
            prm.ChargingScheduleChangeDisallowed(),
            409,
            {
                'code': 'SCHEDULE_TYPE_CHANGE_DISALLOWED',
                'message': 'Activity and fraction schedules cannot switch to other types',  # noqa: E501
            },
        ),
        (
            prm.ChargingAmountOutOfRangeError(
                lower_bound=dec.Decimal(12), upper_bound=dec.Decimal('23.00'),
            ),
            400,
            {
                'code': 'CHARGING_PRICE_OUT_OF_BOUNDS',
                'message': 'Charging price must be in range from 12 to 23.00',
            },
        ),
    ],
)
async def test_errors(
        web_app_client, patch, exception_, error_code, json_error,
):
    @patch('fleet_rent.use_cases.park_rent_modify.ParkRentModify.modify')
    async def _modify(*args, **kwargs) -> rent_entities.Rent:
        raise exception_

    response = await web_app_client.post(
        '/fleet/rent/v1/park/rents/modification?rent_id=basic_rent_id',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
            'X-Real-IP': '127.0.0.1',
        },
        json={
            'asset': {
                'type': 'car',
                'car_id': 'car_id',
                'car_copy_id': 'copy_id',
            },
            'charging': {
                'type': 'daily',
                'daily_price': '100',
                'periodicity': {'type': 'constant'},
                'time': '07:00:00',
            },
            'begins_at': '2020-01-01T07:00+00:00',
        },
    )

    assert response.status == error_code, await response.text()
    if json_error is None:
        return
    assert await response.json() == json_error
