# flake8: noqa F811
import datetime

import pytest
import pytz

from tests_grocery_dispatch.plugins import grocery_dispatch_pg as pg
from tests_grocery_dispatch.plugins.parse_timestamp import parse_timestamp

SMOOTHING_PERIOD = 20
SMOOTHING_FACTOR = 0.15

ETA_SETTINGS = pytest.mark.experiments3(
    name='grocery_dispatch_eta_settings',
    consumers=['grocery_dispatch/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Performer matched',
            'predicate': {
                'init': {
                    'set': [
                        'matched',
                        'delivering',
                        'delivery_arrived',
                        'ready_for_delivering_confirmation',
                    ],
                    'arg_name': 'dispatch_status',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {
                'primary_calculator': 'smoothed',
                'smoothed': {
                    'eta_smoothing_factor': SMOOTHING_FACTOR,
                    'eta_smoothing_period': SMOOTHING_PERIOD,
                },
            },
        },
    ],
    is_config=True,
)


@ETA_SETTINGS
async def test_basic_smoothing(
        mocked_time,
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        grocery_dispatch_extra_pg,
        testpoint,
):
    now = mocked_time.now()
    eta_seconds = 100500
    expected_eta_timestamp = now + datetime.timedelta(seconds=eta_seconds)
    initial_eta_timestamp = pytz.utc.localize(
        mocked_time.now()
        + datetime.timedelta(seconds=SMOOTHING_PERIOD * 2000),
    )

    @testpoint('test_dispatch_status')
    def _test_dispatch_status_cb(data):
        return {'eta_timestamp': initial_eta_timestamp.isoformat()}

    dispatch = grocery_dispatch_pg.create_dispatch(
        status_meta=pg.StatusMeta(),
        status='matched',
        performer=pg.PerformerInfo(),
        eta_timestamp=expected_eta_timestamp,
    )
    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
    )

    await taxi_grocery_dispatch.invalidate_caches()

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200

    assert dispatch_extra.eta_timestamp == initial_eta_timestamp
    assert dispatch_extra.smoothed_eta_eval_time is not None
    assert dispatch_extra.smoothed_eta_timestamp == initial_eta_timestamp
    assert dispatch_extra.result_eta_timestamp != expected_eta_timestamp

    prev_eval_time = dispatch_extra.smoothed_eta_eval_time
    next_eta_timestamp = initial_eta_timestamp - datetime.timedelta(
        seconds=SMOOTHING_PERIOD * 20,
    )

    @testpoint('test_dispatch_status')
    def _test_dispatch_status_cb(data):
        return {'eta_timestamp': next_eta_timestamp.isoformat()}

    mocked_time.sleep(SMOOTHING_PERIOD * 10)
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200

    assert dispatch_extra.eta_timestamp == next_eta_timestamp
    assert dispatch_extra.smoothed_eta_eval_time > prev_eval_time
    assert dispatch_extra.smoothed_eta_timestamp > next_eta_timestamp
    assert dispatch_extra.smoothed_eta_timestamp < initial_eta_timestamp
    assert dispatch_extra.result_eta_timestamp != expected_eta_timestamp

    prev_eval_time = dispatch_extra.smoothed_eta_eval_time

    # если давно не трекали статус, то сглаженное время сбрасывается
    mocked_time.sleep(SMOOTHING_PERIOD * 1001 + 1)

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert dispatch_extra.eta_timestamp == next_eta_timestamp
    assert dispatch_extra.smoothed_eta_timestamp == next_eta_timestamp
    assert dispatch_extra.smoothed_eta_eval_time > prev_eval_time


# Кейс когда первые несколько апдейтов не приходит eta_timestamp от карго
@ETA_SETTINGS
async def test_smoothing_eta_unavailable(
        mocked_time,
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        grocery_dispatch_extra_pg,
        testpoint,
):
    await taxi_grocery_dispatch.invalidate_caches()

    @testpoint('test_dispatch_status')
    def _test_dispatch_status_cb(data):
        return {'eta_timestamp': None}

    now = mocked_time.now()
    dispatch = grocery_dispatch_pg.create_dispatch(
        order=pg.OrderInfo(created=pytz.utc.localize(now), max_eta=600),
        status_meta=pg.StatusMeta(),
        status='matched',
        performer=pg.PerformerInfo(),
        eta_timestamp=pytz.utc.localize(now),
    )
    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200

    assert dispatch_extra.smoothed_eta_eval_time is None
    assert dispatch_extra.eta_timestamp is None

    promise = dispatch.order.created + datetime.timedelta(
        seconds=dispatch.order.max_eta,
    )
    expected_eta = promise - pytz.utc.localize(mocked_time.now())
    assert datetime.timedelta(seconds=response.json()['eta']) == expected_eta

    expected_eta_timestamp = promise
    assert (
        parse_timestamp(response.json()['eta_timestamp'])
        == expected_eta_timestamp
    )
