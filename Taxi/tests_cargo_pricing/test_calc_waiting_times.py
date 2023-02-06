import datetime

import pytest

from tests_cargo_pricing import utils

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        CARGO_PRICING_DB_SOURCES_FOR_READ={
            'v1/taxi/calc/retrieve': ['pg', 'yt'],
            'v2/taxi/calc/retrieve': ['pg', 'yt'],
        },
    ),
]

_ARRIVE_TIME = datetime.datetime(
    2020, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc,
)
_A_FREE_WAIT = 10
_B_FREE_WAIT = 120
_A_PAID_LIMIT = 55
_B_PAID_LIMIT = 5


def _from_arrive(minutes):
    return (_ARRIVE_TIME + datetime.timedelta(minutes=minutes)).isoformat()


@pytest.fixture(name='calc_times')
def _calc_times(taxi_cargo_pricing):
    async def _wrapper(
            calc_id, point_type, eta_minutes=None, due_minutes=None,
    ):
        waypoint = {
            'type': point_type,
            'position': [37.6489887, 55.5737046],
            'first_time_arrived_at': _from_arrive(minutes=0),
        }
        if eta_minutes is not None:
            waypoint['eta'] = _from_arrive(minutes=eta_minutes)
        if due_minutes is not None:
            waypoint['due'] = _from_arrive(minutes=due_minutes)
        resp = await taxi_cargo_pricing.post(
            '/v1/taxi/calc-waiting-times',
            json={'calc_id': calc_id, 'waypoint': waypoint},
        )
        return resp

    return _wrapper


async def _create_calc_with_categories(
        v1_calc_creator, prepare_response, price_for, payment_type,
):
    v1_calc_creator.mock_prepare.categories = prepare_response
    v1_calc_creator.payload['price_for'] = price_for
    v1_calc_creator.payload['payment_info'] = {'type': payment_type}
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    return create_resp.json()['calc_id']


@pytest.fixture(name='create_calc')
def _create_calc(v1_calc_creator, load_json):
    async def _wrapper(price_for='performer', payment_type='corp'):
        prepare_resp = load_json('v2_prepare.json')
        tariff = prepare_resp['cargocorp']['tariff_info']
        tariff['point_a_free_waiting_time'] = _A_FREE_WAIT * 60
        tariff['point_b_free_waiting_time'] = _B_FREE_WAIT * 60
        calc_id = await _create_calc_with_categories(
            v1_calc_creator=v1_calc_creator,
            prepare_response=prepare_resp,
            price_for=price_for,
            payment_type=payment_type,
        )
        return calc_id

    return _wrapper


@pytest.fixture(name='limit_paid_waiting')
def _limit_paid_waiting(experiments3):
    utils.set_limit_paid_waiting(
        experiments3,
        value={
            'max_source_point_paid_waiting': _A_PAID_LIMIT * 60,
            'max_destination_point_paid_waiting': _B_PAID_LIMIT * 60,
        },
    )


async def test_calc_waiting_times(calc_times, create_calc, limit_paid_waiting):
    calc_id = await create_calc()
    response = await calc_times(calc_id=calc_id, point_type='dropoff')
    assert response.status_code == 200
    assert response.json() == {
        'free_waiting_start_ts': _from_arrive(0),
        'paid_waiting_start_ts': _from_arrive(_B_FREE_WAIT),
        'paid_waiting_finish_ts': _from_arrive(_B_FREE_WAIT + _B_PAID_LIMIT),
    }


async def test_calc_waiting_times_no_limit_paid_waiting(
        calc_times, create_calc,
):
    calc_id = await create_calc()
    response = await calc_times(calc_id=calc_id, point_type='pickup')
    assert response.status_code == 200
    assert response.json() == {
        'free_waiting_start_ts': _from_arrive(0),
        'paid_waiting_start_ts': _from_arrive(_A_FREE_WAIT),
    }


async def test_calc_waiting_times_with_eta(
        calc_times, create_calc, limit_paid_waiting,
):
    calc_id = await create_calc()
    eta_shift = 23
    response = await calc_times(
        calc_id=calc_id, point_type='dropoff', eta_minutes=eta_shift,
    )
    assert response.status_code == 200
    assert response.json() == {
        'free_waiting_start_ts': _from_arrive(eta_shift),
        'paid_waiting_start_ts': _from_arrive(_B_FREE_WAIT + eta_shift),
        'paid_waiting_finish_ts': _from_arrive(
            _B_FREE_WAIT + _B_PAID_LIMIT + eta_shift,
        ),
    }


async def test_calc_waiting_times_with_due(
        calc_times, create_calc, limit_paid_waiting,
):
    calc_id = await create_calc(price_for='client')
    due_shift = 17
    response = await calc_times(
        calc_id=calc_id, point_type='pickup', due_minutes=due_shift,
    )
    assert response.status_code == 200
    assert response.json() == {
        'free_waiting_start_ts': _from_arrive(due_shift),
        'paid_waiting_start_ts': _from_arrive(_A_FREE_WAIT + due_shift),
        'paid_waiting_finish_ts': _from_arrive(
            _A_FREE_WAIT + _A_PAID_LIMIT + due_shift,
        ),
    }


async def test_calc_waiting_times_without_free_waiting(
        v1_calc_creator, load_json, calc_times, limit_paid_waiting,
):
    prepare_resp = load_json('v2_prepare.json')
    prepare_resp['cargocorp']['tariff_info'].pop('point_b_free_waiting_time')
    calc_id = await _create_calc_with_categories(
        v1_calc_creator=v1_calc_creator,
        prepare_response=prepare_resp,
        price_for='performer',
        payment_type='corp',
    )
    response = await calc_times(calc_id=calc_id, point_type='dropoff')
    assert response.status_code == 200
    assert response.json() == {'free_waiting_start_ts': _from_arrive(0)}


async def test_calc_waiting_times_no_calc(calc_times):
    not_valid_id = 'cargo-pricing/v1/00000000-0000-0000-0000-000000000000'
    response = await calc_times(calc_id=not_valid_id, point_type='pickup')
    assert response.status_code == 404


async def test_calc_waiting_times_no_waypoint_arrive_time(
        create_calc, taxi_cargo_pricing,
):
    calc_id = await create_calc()
    response = await taxi_cargo_pricing.post(
        '/v1/taxi/calc-waiting-times',
        json={
            'calc_id': calc_id,
            'waypoint': {
                'type': 'pickup',
                'position': [37.6489887, 55.5737046],
            },
        },
    )
    assert response.status_code == 400


async def test_calc_waiting_times_for_performer_c2c(
        calc_times, create_calc, limit_paid_waiting,
):
    calc_id = await create_calc(price_for='performer', payment_type='cash')
    eta_shift = 10
    due_shift = 17
    response = await calc_times(
        calc_id=calc_id,
        point_type='pickup',
        eta_minutes=eta_shift,
        due_minutes=due_shift,
    )
    assert response.status_code == 200
    assert response.json() == {
        'free_waiting_start_ts': _from_arrive(due_shift),
        'paid_waiting_start_ts': _from_arrive(_A_FREE_WAIT + due_shift),
        'paid_waiting_finish_ts': _from_arrive(
            _A_FREE_WAIT + _A_PAID_LIMIT + due_shift,
        ),
    }


async def test_calc_waiting_times_without_d2d_and_changed_free_waiting(
        calc_times,
        create_calc,
        limit_paid_waiting,
        v1_calc_creator,
        taxi_config,
        taxi_cargo_pricing,
):
    source_free_waiting = 2
    destination_free_waiting = 3
    taxi_config.set_values(
        {
            'CARGO_TARIFFS_FREE_WAITING': {
                'moscow': {
                    'cargocorp': {
                        'source': {
                            'free_waiting_time': source_free_waiting * 60,
                            'free_waiting_time_with_door_to_door': 600,
                        },
                        'destination': {
                            'free_waiting_time': destination_free_waiting * 60,
                            'free_waiting_time_with_door_to_door': 600,
                        },
                    },
                },
            },
        },
    )
    v1_calc_creator.payload['taxi_requirements'] = {}
    await taxi_cargo_pricing.invalidate_caches()
    calc_id = await create_calc()
    response = await calc_times(calc_id=calc_id, point_type='dropoff')
    assert response.status_code == 200
    assert response.json() == {
        'free_waiting_start_ts': _from_arrive(0),
        'paid_waiting_start_ts': _from_arrive(destination_free_waiting),
        'paid_waiting_finish_ts': _from_arrive(
            destination_free_waiting + _B_PAID_LIMIT,
        ),
    }
