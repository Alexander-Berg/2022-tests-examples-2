# pylint: disable=too-many-lines
import dataclasses
import datetime as dt
import decimal as dec
import json
import typing as tp

import pytest

from fleet_rent.entities import asset as asset_entities
from fleet_rent.entities import car as car_entities
from fleet_rent.entities import charging as charging_entities
from fleet_rent.entities import daily_periodicity as periodicity_ent
from fleet_rent.entities import rent as rent_entities
from fleet_rent.generated.web import web_context as context_module
from fleet_rent.use_cases import park_rent_modify as uc_module


@pytest.fixture(name='patch_parks_information')
def _patch_parks_information(patch, park_stub_factory):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get(park_id: str):
        assert park_id == 'park_id5'
        return park_stub_factory(id=park_id, tz_offset=5)


async def _compare_rent_version(
        rent_id: str,
        context: context_module.Context,
        moment: tp.Optional[dt.datetime] = None,
        last: tp.Optional[bool] = None,
):
    assert moment or last
    assert bool(moment) != bool(last)
    rent_access = context.pg_access.rent
    rent = await rent_access.internal_get_rent(rent_id)
    if moment:
        v_moment = moment
    else:
        # Get time from DB because datetime.now can be monkey patched
        v_moment = await context.pg.slave.fetchval(
            'SELECT CAST(NOW() AS TIMESTAMPTZ);',
        )
    rent_version = await rent_access.internal_get_rent_version(
        rent_id, v_moment,
    )
    rdict = dataclasses.asdict(rent)
    rvdict = dataclasses.asdict(rent_version)
    assert rvdict.pop('modified_at')
    assert rvdict.pop('version')
    assert rdict == rvdict


#  ====== Simpler tests ======


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_simple_changes_ok(
        web_context: context_module.Context, patch_parks_information,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    updated = await ucase.modify(
        modification_source=rent_entities.RentModificationSourceDispatcher(
            dispatcher_uid='dispatcher', ticket_provider='yandex',
        ),
        rent_id='basic_rent_id',
        park_id='park_id5',
        comment='new comment',
        title='new title',
        charging=charging_entities.ChargingDaily(
            starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
            finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+00:00'),
            daily_price=dec.Decimal(200),
            periodicity=periodicity_ent.DailyPeriodicityConstant(),
            total_withhold_limit=None,
            time=dt.time(hour=12, minute=0),
        ),
        asset=asset_entities.AssetOther(
            subtype='misc', description='new descr',
        ),
    )
    await _compare_rent_version('basic_rent_id', web_context, last=True)
    mod_source = await web_context.pg.master.fetchval(
        """SELECT modification_source FROM rent.rent_history
        WHERE rent_id = 'basic_rent_id'
        ORDER BY version DESC LIMIT 1""",
    )
    assert mod_source == {
        'kind': 'dispatcher',
        'ticket_provider': 'yandex',
        'uid': 'dispatcher',
    }
    assert updated == rent_entities.Rent(
        record_id='basic_rent_id',
        owner_park_id='park_id5',
        owner_serial_id=1,
        driver_id='driver_id',
        affiliation_id=None,
        title='new title',
        comment='new comment',
        balance_notify_limit=None,
        begins_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        ends_at=dt.datetime(2020, 1, 31, 0, 0, tzinfo=dt.timezone.utc),
        asset=asset_entities.AssetOther(
            subtype='misc', description='new descr',
        ),
        charging=charging_entities.ChargingDaily(
            starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
            finishes_at=dt.datetime(2020, 1, 31, 0, 0, tzinfo=dt.timezone.utc),
            daily_price=dec.Decimal('200'),
            periodicity=periodicity_ent.DailyPeriodicityConstant(),
            total_withhold_limit=None,
            time=dt.time(12, 0),
        ),
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


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_simple_changes_no_park(
        web_context: context_module.Context, patch,
):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park(park_id: str):
        assert park_id == 'park_id5'
        return None

    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.UnhandleableError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(hour=12, minute=0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_simple_changes_not_found(
        web_context: context_module.Context, patch_parks_information,
):
    with pytest.raises(uc_module.RentNotFoundError):
        ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify  # noqa: E501
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(hour=12, minute=0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_changes_smz_driver.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_simple_changes_not_smz(
        web_context: context_module.Context, patch_parks_information,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    old_state = await web_context.pg_access.rent.internal_get_rent(
        'basic_rent_id',
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.IndependentDriverError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(hour=12, minute=0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )
    await _compare_rent_version('basic_rent_id', web_context, last=True)
    assert old_state == await web_context.pg_access.rent.internal_get_rent(
        'basic_rent_id',
    )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_simple_changes_end_begin_time(
        web_context: context_module.Context, patch, patch_parks_information,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.BeginEndTimesNotValidError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-02-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(hour=12, minute=0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
@pytest.mark.parametrize('price', (1, 1000_000))
@pytest.mark.config(
    FLEET_RENT_CHARGING_AMOUNT_LIMITS={
        'lower_limit': '10.00',
        'upper_limit': '100_000.00',
    },
)
async def test_simple_changes_amount_bounds(
        web_context: context_module.Context,
        patch,
        patch_parks_information,
        price,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.ChargingAmountOutOfRangeError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(price),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(hour=12, minute=0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_simple_changes_no_charging_free(
        web_context: context_module.Context, patch_parks_information,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.UnhandleableError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingFree(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
@pytest.mark.parametrize('is_valid_car', [True, False])
async def test_simple_changes_ok_car_asset_change(
        web_context: context_module.Context,
        patch_parks_information,
        patch,
        is_valid_car,
):
    @patch('fleet_rent.services.car_info.CarInfoService.try_get_car_info')
    async def _get_park(park_id: str, car_id: str):
        assert park_id == 'park_id5'
        assert car_id == 'new_car'
        if is_valid_car:
            return car_entities.Car(park_id=park_id, id=car_id)
        return None

    await web_context.pg.master.execute(
        """WITH upr AS (
            UPDATE rent.records SET asset_type = 'car',
             asset_params = '{"car_id":"old_car"}'
            WHERE record_id = 'basic_rent_id'
        )
        UPDATE rent.rent_history SET asset_type = 'car',
         asset_params = '{"car_id":"old_car"}'
        WHERE rent_id = 'basic_rent_id';""",
    )
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify

    async def _modify_car():
        return await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(hour=12, minute=0),
            ),
            asset=asset_entities.AssetCar(car_id='new_car', car_copy_id=None),
        )

    if is_valid_car:
        updated = await _modify_car()
    else:
        with pytest.raises(uc_module.AssetCarInvalidError):
            await _modify_car()
        await _compare_rent_version(
            'basic_rent_id',
            web_context,
            moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
        )
        return

    await _compare_rent_version('basic_rent_id', web_context, last=True)
    mod_source = await web_context.pg.master.fetchval(
        """SELECT modification_source FROM rent.rent_history
        WHERE rent_id = 'basic_rent_id'
        ORDER BY version DESC LIMIT 1""",
    )
    assert mod_source == {
        'kind': 'dispatcher',
        'ticket_provider': 'yandex',
        'uid': 'dispatcher',
    }
    assert updated == rent_entities.Rent(
        record_id='basic_rent_id',
        owner_park_id='park_id5',
        owner_serial_id=1,
        driver_id='driver_id',
        affiliation_id=None,
        title='new title',
        comment='new comment',
        balance_notify_limit=None,
        begins_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        ends_at=dt.datetime(2020, 1, 31, 0, 0, tzinfo=dt.timezone.utc),
        asset=asset_entities.AssetCar(car_id='new_car', car_copy_id=None),
        charging=charging_entities.ChargingDaily(
            starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
            finishes_at=dt.datetime(2020, 1, 31, 0, 0, tzinfo=dt.timezone.utc),
            daily_price=dec.Decimal('200'),
            periodicity=periodicity_ent.DailyPeriodicityConstant(),
            total_withhold_limit=None,
            time=dt.time(12, 0),
        ),
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


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
@pytest.mark.parametrize('forbidden_by', ['arbitrary_entries', 'event_queue'])
async def test_event_queue_arbit_entries(
        web_context: context_module.Context,
        patch_parks_information,
        forbidden_by,
):
    await web_context.pg.master.execute(
        """WITH upr AS (
            UPDATE rent.records SET use_arbitrary_entries = $1,
             use_event_queue = $2
            WHERE record_id = 'basic_rent_id'
        )
        UPDATE rent.rent_history SET use_arbitrary_entries = $1,
             use_event_queue = $2
        WHERE rent_id = 'basic_rent_id';""",
        forbidden_by != 'arbitrary_entries',
        forbidden_by != 'event_queue',
    )
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.UnmodifableRentError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(hour=12, minute=0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
@pytest.mark.parametrize('charging_type', ['daily', 'active_days'])
@pytest.mark.parametrize('change', ['price', 'total'])
async def test_cannot_change_deposit_amount(
        web_context: context_module.Context,
        patch_parks_information,
        charging_type,
        change,
):
    if change == 'price':
        price = dec.Decimal(200)
        limit = dec.Decimal(1000)
    else:
        price = dec.Decimal(100)
        limit = dec.Decimal(2000)
    if charging_type == 'daily':
        charging_js = {
            'daily_price': '100',
            'time': '12:00',
            'total_withhold_limit': '1000',
            'periodicity': {'type': 'constant', 'params': {}},
        }
        update = charging_entities.ChargingDaily(  # type: ignore
            starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
            finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+00:00'),
            periodicity=periodicity_ent.DailyPeriodicityConstant(),
            daily_price=price,
            total_withhold_limit=limit,
            time=dt.time(hour=12, minute=0),
        )
    else:
        charging_js = {'daily_price': '100', 'total_withhold_limit': '1000'}
        update = charging_entities.ChargingActiveDays(  # type: ignore
            starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
            finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+00:00'),
            daily_price=price,
            total_withhold_limit=limit,
        )
    await web_context.pg.master.execute(
        """WITH upr AS (
            UPDATE rent.records SET asset_type = 'other',
             asset_params = '{"subtype":"deposit"}',
             charging_type = $1,
             charging_params = $2
            WHERE record_id = 'basic_rent_id'
        )
        UPDATE rent.rent_history SET asset_type = 'other',
             asset_params = '{"subtype":"deposit"}',
             charging_type = $1,
             charging_params = $2
        WHERE rent_id = 'basic_rent_id';""",
        charging_type,
        json.dumps(charging_js),
    )
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    if change == 'price':
        exc = uc_module.DepositChargingPriceError  # type: ignore
    else:
        exc = uc_module.DepositChargingLimitError  # type: ignore
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(exc):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=update,
            asset=asset_entities.AssetOther(
                subtype='deposit', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.parametrize(
    'by_condition',
    [
        pytest.param(
            'ends_at', marks=[pytest.mark.now('2020-02-01 05:00+00:00')],
        ),
        pytest.param(
            'terminated_at',
            marks=[
                pytest.mark.now('2020-01-01 05:00+00:00'),
                pytest.mark.pgsql(
                    'fleet_rent',
                    queries=[
                        """UPDATE rent.records
                            SET ends_at = NULL, terminated_at = NOW()
                            WHERE record_id = 'basic_rent_id'""",
                    ],
                ),
            ],
        ),
    ],
)
async def test_time_changes_cannot_change_terminated(
        web_context: context_module.Context,
        patch,
        patch_parks_information,
        by_condition,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.TerminatedRentError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=None,
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(12, 0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


#  ====== Cases with event queue change ======


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2019-12-03 05:00+00:00')
async def test_simple_changes_time_not_match(
        web_context: context_module.Context, patch, patch_parks_information,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.BeginTimeAndChargingTimeMismatch):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(13, 0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_time_changes_cannot_change_begin_in_past(
        web_context: context_module.Context, patch, patch_parks_information,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.BeginTimeCannotBeChangedError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 13:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 00:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(13, 0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-27 05:00+00:00')
@pytest.mark.config(FLEET_RENT_SCHEDULE_MODIFY_TIME_LIMIT=2 * 60 * 60)
async def test_time_changes_ends_at_not_too_close(
        web_context: context_module.Context, patch, patch_parks_information,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.EndsAtOutOfRangeError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-27 06:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(12, 0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 06:59+00')
@pytest.mark.config(FLEET_RENT_SCHEDULE_MODIFY_TIME_LIMIT=300)
async def test_time_changes_next_event_close(
        web_context: context_module.Context, patch, patch_parks_information,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.ScheduleChangeUnavailableError):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 06:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityConstant(),
                total_withhold_limit=None,
                time=dt.time(13, 0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 06:59+00')
@pytest.mark.config(FLEET_RENT_SCHEDULE_MODIFY_TIME_LIMIT=300)
async def test_schedule_type_unchangeable(
        web_context: context_module.Context, patch, patch_parks_information,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.ChargingScheduleChangeDisallowed):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingActiveDays(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 06:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                total_withhold_limit=None,
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 06:59+00')
@pytest.mark.config(FLEET_RENT_SCHEDULE_MODIFY_TIME_LIMIT=300)
async def test_schedule_type_to_fraction(
        web_context: context_module.Context, patch, patch_parks_information,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.ChargingScheduleChangeDisallowed):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 06:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityFraction(
                    numerator=10, denominator=12,
                ),
                total_withhold_limit=None,
                time=dt.time(12, 0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql(
    'fleet_rent',
    files=['test_simple_changes_ok.sql'],
    queries=[
        """UPDATE rent.records SET
                   charging_params='{"daily_price": "100", "time":"12:00",
                   "periodicity": {"type": "fraction", "params": {
                      "numerator": 10,
                      "denominator": 20
                   }}}';""",
    ],
)
@pytest.mark.now('2020-01-03 06:59+00')
@pytest.mark.config(FLEET_RENT_SCHEDULE_MODIFY_TIME_LIMIT=300)
async def test_schedule_type_diff_fraction(
        web_context: context_module.Context, patch, patch_parks_information,
):
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    with pytest.raises(uc_module.ChargingScheduleChangeDisallowed):
        await ucase.modify(
            modification_source=rent_entities.RentModificationSourceDispatcher(
                dispatcher_uid='dispatcher', ticket_provider='yandex',
            ),
            rent_id='basic_rent_id',
            park_id='park_id5',
            comment='new comment',
            title='new title',
            charging=charging_entities.ChargingDaily(
                starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
                finishes_at=dt.datetime.fromisoformat(
                    '2020-01-31 06:00+00:00',
                ),
                daily_price=dec.Decimal(200),
                periodicity=periodicity_ent.DailyPeriodicityFraction(
                    numerator=10, denominator=12,
                ),
                total_withhold_limit=None,
                time=dt.time(12, 0),
            ),
            asset=asset_entities.AssetOther(
                subtype='misc', description='new descr',
            ),
        )


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
@pytest.mark.parametrize(
    'new_time,new_dt',
    [('13:00', '2020-01-03T13:00+05:00'), ('09:00', '2020-01-04T09:00+05:00')],
)
async def test_simple_changes_reschedule_events(
        web_context: context_module.Context,
        patch_parks_information,
        new_time,
        new_dt,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    updated = await ucase.modify(
        modification_source=rent_entities.RentModificationSourceDispatcher(
            dispatcher_uid='dispatcher', ticket_provider='yandex',
        ),
        rent_id='basic_rent_id',
        park_id='park_id5',
        comment='new comment',
        title='new title',
        charging=charging_entities.ChargingDaily(
            starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
            finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+00:00'),
            daily_price=dec.Decimal(100),
            periodicity=periodicity_ent.DailyPeriodicityConstant(),
            total_withhold_limit=None,
            time=dt.time.fromisoformat(new_time),
        ),
        asset=asset_entities.AssetOther(
            subtype='misc', description='new descr',
        ),
    )
    await _compare_rent_version('basic_rent_id', web_context, last=True)
    mod_source = await web_context.pg.master.fetchval(
        """SELECT modification_source FROM rent.rent_history
        WHERE rent_id = 'basic_rent_id'
        ORDER BY version DESC LIMIT 1""",
    )
    assert mod_source == {
        'kind': 'dispatcher',
        'ticket_provider': 'yandex',
        'uid': 'dispatcher',
    }
    assert updated.charging == charging_entities.ChargingDaily(
        starts_at=dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
        finishes_at=dt.datetime(2020, 1, 31, 0, 0, tzinfo=dt.timezone.utc),
        daily_price=dec.Decimal('100'),
        periodicity=periodicity_ent.DailyPeriodicityConstant(),
        total_withhold_limit=None,
        time=dt.time.fromisoformat(new_time),
    )
    events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    events = [dict(x) for x in events]
    assert events == [
        {
            'event_at': dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
            'event_number': 1,
            'executed_at': dt.datetime(
                2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc,
            ),
            'rent_id': 'basic_rent_id',
        },
        {
            'event_at': dt.datetime(2020, 1, 2, 7, 0, tzinfo=dt.timezone.utc),
            'event_number': 2,
            'executed_at': dt.datetime(
                2020, 1, 2, 7, 10, tzinfo=dt.timezone.utc,
            ),
            'rent_id': 'basic_rent_id',
        },
        {
            'event_at': dt.datetime.fromisoformat(new_dt),
            'event_number': 3,
            'executed_at': None,
            'rent_id': 'basic_rent_id',
        },
    ]


@pytest.mark.pgsql('fleet_rent', files=['test_simple_changes_ok.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_simple_changes_to_weekly(
        web_context: context_module.Context, patch_parks_information,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    updated = await ucase.modify(
        modification_source=rent_entities.RentModificationSourceDispatcher(
            dispatcher_uid='dispatcher', ticket_provider='yandex',
        ),
        rent_id='basic_rent_id',
        park_id='park_id5',
        comment='new comment',
        title='new title',
        charging=charging_entities.ChargingDaily(
            starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
            finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+00:00'),
            daily_price=dec.Decimal(100),
            periodicity=periodicity_ent.DailyPeriodicityISOWeekDays(
                isoweekdays=[2, 3, 4],
            ),
            total_withhold_limit=None,
            time=dt.time(hour=18, minute=20),
        ),
        asset=asset_entities.AssetOther(
            subtype='misc', description='new descr',
        ),
    )
    await _compare_rent_version('basic_rent_id', web_context, last=True)
    mod_source = await web_context.pg.master.fetchval(
        """SELECT modification_source FROM rent.rent_history
        WHERE rent_id = 'basic_rent_id'
        ORDER BY version DESC LIMIT 1""",
    )
    assert mod_source == {
        'kind': 'dispatcher',
        'ticket_provider': 'yandex',
        'uid': 'dispatcher',
    }
    assert updated.charging == charging_entities.ChargingDaily(
        starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
        finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+00:00'),
        daily_price=dec.Decimal(100),
        periodicity=periodicity_ent.DailyPeriodicityISOWeekDays(
            isoweekdays=[2, 3, 4],
        ),
        total_withhold_limit=None,
        time=dt.time(hour=18, minute=20),
    )
    events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    events = [dict(x) for x in events]
    assert events == [
        {
            'event_at': dt.datetime(2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc),
            'event_number': 1,
            'executed_at': dt.datetime(
                2020, 1, 1, 7, 0, tzinfo=dt.timezone.utc,
            ),
            'rent_id': 'basic_rent_id',
        },
        {
            'event_at': dt.datetime(2020, 1, 2, 7, 0, tzinfo=dt.timezone.utc),
            'event_number': 2,
            'executed_at': dt.datetime(
                2020, 1, 2, 7, 10, tzinfo=dt.timezone.utc,
            ),
            'rent_id': 'basic_rent_id',
        },
        {
            'event_at': dt.datetime(
                2020,
                1,
                7,
                18,
                20,
                tzinfo=dt.timezone(offset=dt.timedelta(hours=5)),
            ),
            'event_number': 3,
            'executed_at': None,
            'rent_id': 'basic_rent_id',
        },
    ]


@pytest.mark.pgsql(
    'fleet_rent',
    files=['test_schedule_changes_activity.sql'],
    queries=[
        """INSERT INTO rent.active_day_start_triggers(rent_id,
        event_number, park_id, driver_id, lower_datetime_bound,
        upper_datetime_bound, triggered_at, order_id, modified_at)
VALUES
    ('basic_rent_id', 1, 'park_id5', 'driver_id', '2020-01-01 00:00+05',
    '2020-01-31 00:00+05', '2020-01-01 12:00+05',
     'first', '2020-01-01 12:00+05'),
    ('basic_rent_id', 2, 'park_id5', 'driver_id', '2020-01-02 00:00+05',
    '2020-01-31 00:00+05', '2020-01-02 12:00+05',
     'second', '2020-01-01 12:00+05'),
    ('basic_rent_id', 3, 'park_id5', 'driver_id', '2020-01-03 00:00+05',
    '2020-01-31 00:00+05', NULL, NULL, '2020-01-01 12:00+05');""",
        """INSERT INTO rent.event_queue(
            rent_id, event_number, event_at, executed_at)
    VALUES ('basic_rent_id', 1, '2020-01-01 12:00+05',
     '2020-01-01 12:00+05'),
       ('basic_rent_id', 2, '2020-01-02 12:00+05', '2020-01-02 12:10+05');""",
    ],
)
@pytest.mark.now('2020-01-03 05:00+00:00')
@pytest.mark.parametrize(
    'new_finish_at',
    [
        None,
        dt.datetime.fromisoformat('2020-01-25 00:00+05:00'),
        dt.datetime.fromisoformat('2020-02-25 00:00+05:00'),
    ],
)
async def test_activity_change_finish_at(
        web_context: context_module.Context,
        patch_parks_information,
        new_finish_at,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    old_events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    updated = await ucase.modify(
        modification_source=rent_entities.RentModificationSourceDispatcher(
            dispatcher_uid='dispatcher', ticket_provider='yandex',
        ),
        rent_id='basic_rent_id',
        park_id='park_id5',
        comment='new comment',
        title='new title',
        charging=charging_entities.ChargingActiveDays(
            starts_at=dt.datetime.fromisoformat('2020-01-01 00:00+05:00'),
            finishes_at=new_finish_at,
            daily_price=dec.Decimal(100),
            total_withhold_limit=None,
        ),
        asset=asset_entities.AssetOther(
            subtype='misc', description='new descr',
        ),
    )
    await _compare_rent_version('basic_rent_id', web_context, last=True)
    assert updated.charging == charging_entities.ChargingActiveDays(
        starts_at=dt.datetime.fromisoformat('2020-01-01 00:00+05:00'),
        finishes_at=new_finish_at,
        daily_price=dec.Decimal(100),
        total_withhold_limit=None,
    )
    new_events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    assert new_events == old_events
    last_trigger = await web_context.pg.master.fetchrow(
        'SELECT * FROM rent.active_day_start_triggers'
        ' WHERE rent_id = $1 ORDER BY event_number DESC LIMIT 1',
        'basic_rent_id',
    )
    last_trigger = dict(last_trigger)
    assert last_trigger.pop('modified_at') > dt.datetime.fromisoformat(
        '2020-01-01 12:00+05:00',
    )
    assert dict(last_trigger) == {
        'driver_id': 'driver_id',
        'event_number': 3,
        'lower_datetime_bound': dt.datetime.fromisoformat(
            '2020-01-03 00:00+05:00',
        ),
        'order_id': None,
        'park_id': 'park_id5',
        'rent_id': 'basic_rent_id',
        'triggered_at': None,
        'upper_datetime_bound': new_finish_at,
    }


@pytest.mark.pgsql(
    'fleet_rent',
    files=['test_schedule_changes_activity.sql'],
    queries=[
        """INSERT INTO rent.active_day_start_triggers(rent_id,
        event_number, park_id, driver_id, lower_datetime_bound,
        upper_datetime_bound, triggered_at, order_id, modified_at)
VALUES
    ('basic_rent_id', 1, 'park_id5', 'driver_id', '2020-01-01 00:00+05',
    '2020-01-31 00:00+05', '2020-01-01 12:00+05',
    'first', '2020-01-01 12:00+05'),
    ('basic_rent_id', 2, 'park_id5', 'driver_id', '2020-01-02 00:00+05',
    '2020-01-31 00:00+05', '2020-01-02 12:00+05',
    'second', '2020-01-01 12:00+05'),
    ('basic_rent_id', 3, 'park_id5', 'driver_id', '2020-01-03 00:00+05',
    '2020-01-31 00:00+05', '2020-01-03 12:00+05',
    'third', '2020-01-01 12:00+05');""",
        """INSERT INTO rent.event_queue(rent_id, event_number, event_at, executed_at)
    VALUES ('basic_rent_id', 1, '2020-01-01 12:00+05', '2020-01-01 12:00+05'),
       ('basic_rent_id', 2, '2020-01-02 12:00+05', '2020-01-02 12:10+05'),
       ('basic_rent_id', 3, '2020-01-03 12:00+05', NULL);""",
    ],
)
@pytest.mark.now('2020-01-03 05:00+00:00')
@pytest.mark.parametrize(
    'new_finish_at',
    [
        None,
        dt.datetime.fromisoformat('2020-01-25 00:00+05:00'),
        dt.datetime.fromisoformat('2020-02-25 00:00+05:00'),
    ],
)
async def test_activity_change_finish_at_wo_trigger(
        web_context: context_module.Context,
        patch_parks_information,
        new_finish_at,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    old_events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    updated = await ucase.modify(
        modification_source=rent_entities.RentModificationSourceDispatcher(
            dispatcher_uid='dispatcher', ticket_provider='yandex',
        ),
        rent_id='basic_rent_id',
        park_id='park_id5',
        comment='new comment',
        title='new title',
        charging=charging_entities.ChargingActiveDays(
            starts_at=dt.datetime.fromisoformat('2020-01-01 00:00+05:00'),
            finishes_at=new_finish_at,
            daily_price=dec.Decimal(100),
            total_withhold_limit=None,
        ),
        asset=asset_entities.AssetOther(
            subtype='misc', description='new descr',
        ),
    )
    await _compare_rent_version('basic_rent_id', web_context, last=True)
    assert updated.charging == charging_entities.ChargingActiveDays(
        starts_at=dt.datetime.fromisoformat('2020-01-01 00:00+05:00'),
        finishes_at=new_finish_at,
        daily_price=dec.Decimal(100),
        total_withhold_limit=None,
    )
    new_events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    assert new_events == old_events
    last_trigger = await web_context.pg.master.fetchrow(
        'SELECT * FROM rent.active_day_start_triggers'
        ' WHERE rent_id = $1 ORDER BY event_number DESC LIMIT 1',
        'basic_rent_id',
    )
    last_trigger = dict(last_trigger)
    assert last_trigger.pop('modified_at') == dt.datetime.fromisoformat(
        '2020-01-01 12:00+05:00',
    )
    assert dict(last_trigger) == {
        'driver_id': 'driver_id',
        'event_number': 3,
        'lower_datetime_bound': dt.datetime.fromisoformat(
            '2020-01-03 00:00+05:00',
        ),
        'order_id': 'third',
        'park_id': 'park_id5',
        'rent_id': 'basic_rent_id',
        'triggered_at': dt.datetime.fromisoformat('2020-01-03 12:00+05:00'),
        'upper_datetime_bound': dt.datetime.fromisoformat(
            '2020-01-31 00:00+05:00',
        ),
    }


@pytest.mark.pgsql(
    'fleet_rent',
    files=['test_schedule_changes_activity.sql'],
    queries=[
        """INSERT INTO rent.active_day_start_triggers(rent_id,
        event_number, park_id, driver_id, lower_datetime_bound,
        upper_datetime_bound, triggered_at, order_id, modified_at)
VALUES
    ('basic_rent_id', 1, 'park_id5', 'driver_id', '2020-01-01 00:00+05',
    '2020-01-31 00:00+05', NULL, NULL, '2020-01-01 12:00+05');""",
    ],
)
@pytest.mark.now('2019-12-25 05:00+00:00')
async def test_activity_change_begins_at(
        web_context: context_module.Context, patch_parks_information,
):
    await _compare_rent_version(
        'basic_rent_id',
        web_context,
        moment=dt.datetime.fromisoformat('2020-01-03 10:00+05:00'),
    )
    old_events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    ucase: uc_module.ParkRentModify = web_context.use_cases.park_rent_modify
    updated = await ucase.modify(
        modification_source=rent_entities.RentModificationSourceDispatcher(
            dispatcher_uid='dispatcher', ticket_provider='yandex',
        ),
        rent_id='basic_rent_id',
        park_id='park_id5',
        comment='new comment',
        title='new title',
        charging=charging_entities.ChargingActiveDays(
            starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
            finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+05:00'),
            daily_price=dec.Decimal(100),
            total_withhold_limit=None,
        ),
        asset=asset_entities.AssetOther(
            subtype='misc', description='new descr',
        ),
    )
    await _compare_rent_version('basic_rent_id', web_context, last=True)
    assert updated.charging == charging_entities.ChargingActiveDays(
        starts_at=dt.datetime.fromisoformat('2020-01-01 12:00+05:00'),
        finishes_at=dt.datetime.fromisoformat('2020-01-31 00:00+05:00'),
        daily_price=dec.Decimal(100),
        total_withhold_limit=None,
    )
    new_events = await web_context.pg.master.fetch(
        'SELECT rent_id, event_number, event_at, executed_at'
        ' FROM rent.event_queue ORDER BY event_number ASC',
    )
    assert new_events == old_events
    last_trigger = await web_context.pg.master.fetchrow(
        'SELECT * FROM rent.active_day_start_triggers'
        ' WHERE rent_id = $1 ORDER BY event_number DESC LIMIT 1',
        'basic_rent_id',
    )
    last_trigger = dict(last_trigger)
    assert last_trigger.pop('modified_at') > dt.datetime.fromisoformat(
        '2020-01-01 12:00+05:00',
    )
    assert dict(last_trigger) == {
        'driver_id': 'driver_id',
        'event_number': 1,
        'lower_datetime_bound': dt.datetime.fromisoformat(
            '2020-01-01 12:00+05:00',
        ),
        'order_id': None,
        'park_id': 'park_id5',
        'rent_id': 'basic_rent_id',
        'triggered_at': None,
        'upper_datetime_bound': dt.datetime.fromisoformat(
            '2020-01-31 00:00+05:00',
        ),
    }
