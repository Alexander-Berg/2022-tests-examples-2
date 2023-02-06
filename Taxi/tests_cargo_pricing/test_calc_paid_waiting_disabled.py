import pytest

from tests_cargo_pricing import utils


DEFAULT_WAITING_TIME = {
    'waiting_time': 60,
    'waiting_in_transit_time': 0,
    'waiting_in_destination_time': 30,
}

DISABLED_WAITING_TIME = {
    'waiting_time': 0,
    'waiting_in_transit_time': 0,
    'waiting_in_destination_time': 0,
}

PERFORMER = {
    'driver_id': 'uuid0',
    'park_db_id': 'dbid0',
    'assigned_at': utils.from_start(minutes=0),
}


@pytest.fixture(name='configure_paid_waiting_enabled')
def _configure_paid_waiting_enabled(experiments3, taxi_cargo_pricing):
    async def configurate(enabled):
        experiments3.add_config(
            match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
            name='cargo_pricing_paid_waiting_enabled',
            consumers=['cargo-pricing/v1/taxi/calc'],
            clauses=[],
            default_value={'enabled': enabled},
        )
        await taxi_cargo_pricing.invalidate_caches()

    return configurate


def check_waiting(v1_calc_creator, time):
    recalc_req = v1_calc_creator.mock_recalc.request

    user_trip_details = recalc_req['user']['trip_details']
    driver_trip_details = recalc_req['driver']['trip_details']
    assert (
        user_trip_details['waiting_time']
        == driver_trip_details['waiting_time']
        == time['waiting_time']
    )
    assert (
        user_trip_details['waiting_in_transit_time']
        == driver_trip_details['waiting_in_transit_time']
        == time['waiting_in_transit_time']
    )
    assert (
        user_trip_details['waiting_in_destination_time']
        == driver_trip_details['waiting_in_destination_time']
        == time['waiting_in_destination_time']
    )


async def test_calc_paid_waiting_driver_tags_kwargs(
        v1_calc_creator,
        configure_paid_waiting_enabled,
        experiments3,
        v1_drivers_match_profile,
):
    await configure_paid_waiting_enabled(enabled=False)

    v1_calc_creator.payload['performer'] = PERFORMER

    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_paid_waiting_enabled',
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['consumer'] == 'cargo-pricing/v1/taxi/calc'
    assert kwargs['driver_tags'] == ['driver_fix_bad_guy']


async def test_calc_paid_waiting_disabled(
        v1_calc_creator,
        user_options,
        configure_paid_waiting_enabled,
        v1_drivers_match_profile,
):
    await configure_paid_waiting_enabled(enabled=False)

    calc1_response = await v1_calc_creator.execute()
    assert calc1_response.status_code == 200
    check_waiting(v1_calc_creator, DEFAULT_WAITING_TIME)

    calc1_id = calc1_response.json()['calc_id']
    v1_calc_creator.payload['performer'] = PERFORMER
    v1_calc_creator.payload['previous_calc_id'] = calc1_id

    calc2_response = await v1_calc_creator.execute()
    assert calc2_response.status_code == 200
    check_waiting(v1_calc_creator, DISABLED_WAITING_TIME)


async def test_calc_paid_waiting_inherited(
        v1_calc_creator,
        user_options,
        configure_paid_waiting_enabled,
        v1_drivers_match_profile,
):
    await configure_paid_waiting_enabled(enabled=False)

    v1_calc_creator.payload['performer'] = PERFORMER
    calc1_response = await v1_calc_creator.execute()
    assert calc1_response.status_code == 200
    check_waiting(v1_calc_creator, DISABLED_WAITING_TIME)

    v1_calc_creator.payload.pop('performer')
    calc1_id = calc1_response.json()['calc_id']
    v1_calc_creator.payload['previous_calc_id'] = calc1_id

    calc2_response = await v1_calc_creator.execute()
    assert calc2_response.status_code == 200
    check_waiting(v1_calc_creator, DISABLED_WAITING_TIME)


@pytest.mark.config(CARGO_PRICING_ENABLE_DECODING_BINARY_FROM_YT=True)
@pytest.mark.config(
    CARGO_PRICING_DB_SOURCES_FOR_READ={
        'v1/taxi/calc/retrieve': ['pg', 'yt'],
        'v2/taxi/calc/retrieve': ['pg', 'yt'],
        'v1/taxi/calc': ['pg', 'yt'],
    },
)
@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_retrieve_calc_yt_with_paid_waiting_attribute_from_yt(
        yt_apply,
        v1_retrieve_calc,
        v1_calc_creator,
        configure_paid_waiting_enabled,
):
    await configure_paid_waiting_enabled(enabled=False)

    calc_id = 'cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2'
    response = await v1_retrieve_calc(calc_id=calc_id)
    assert response.status_code == 200

    v1_calc_creator.payload['previous_calc_id'] = calc_id
    calc3_response = await v1_calc_creator.execute()
    assert calc3_response.status_code == 200
    check_waiting(v1_calc_creator, DISABLED_WAITING_TIME)


async def test_calc_paid_waiting_enabled(
        v1_calc_creator,
        user_options,
        configure_paid_waiting_enabled,
        v1_drivers_match_profile,
):
    await configure_paid_waiting_enabled(enabled=True)

    calc1_response = await v1_calc_creator.execute()
    assert calc1_response.status_code == 200
    check_waiting(v1_calc_creator, DEFAULT_WAITING_TIME)

    v1_calc_creator.payload['performer'] = PERFORMER
    calc1_id = calc1_response.json()['calc_id']
    v1_calc_creator.payload['previous_calc_id'] = calc1_id

    calc2_response = await v1_calc_creator.execute()
    assert calc2_response.status_code == 200
    check_waiting(v1_calc_creator, DEFAULT_WAITING_TIME)


async def test_calc_paid_waiting_inherited_with_change_exp_value(
        v1_calc_creator,
        user_options,
        configure_paid_waiting_enabled,
        v1_drivers_match_profile,
):
    await configure_paid_waiting_enabled(enabled=True)

    calc1_response = await v1_calc_creator.execute()
    assert calc1_response.status_code == 200
    check_waiting(v1_calc_creator, DEFAULT_WAITING_TIME)

    v1_calc_creator.payload['performer'] = PERFORMER
    calc1_id = calc1_response.json()['calc_id']
    v1_calc_creator.payload['previous_calc_id'] = calc1_id

    calc2_response = await v1_calc_creator.execute()
    assert calc2_response.status_code == 200
    check_waiting(v1_calc_creator, DEFAULT_WAITING_TIME)

    calc2_id = calc2_response.json()['calc_id']

    await configure_paid_waiting_enabled(enabled=False)
    v1_calc_creator.payload['performer'] = PERFORMER
    v1_calc_creator.payload['previous_calc_id'] = calc2_id

    calc3_response = await v1_calc_creator.execute()
    assert calc3_response.status_code == 200
    check_waiting(v1_calc_creator, DEFAULT_WAITING_TIME)
