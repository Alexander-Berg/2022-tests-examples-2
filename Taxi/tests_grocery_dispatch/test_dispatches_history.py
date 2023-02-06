# flake8: noqa IS001
# pylint: disable=import-only-modules
import copy
import datetime

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch import models
from tests_grocery_dispatch.plugins.models import OrderInfo, PerformerInfo

import pytest
import pytz
from dateutil import parser

NOW = datetime.datetime(2020, 10, 5, 16, 28, 00, tzinfo=datetime.timezone.utc)


@pytest.mark.now(NOW.isoformat())
async def test_dispatches_history_basic(grocery_dispatch_pg):
    dispatch = grocery_dispatch_pg.create_dispatch(
        status='scheduled', performer=PerformerInfo(),
    )
    assert len(dispatch.history()) == 1
    assert dispatch == dispatch.history()[0]

    # Update dispatch
    dispatch.status = 'canceled'
    assert len(dispatch.history()) == 2
    assert dispatch.history()[-1].status == 'canceled'

    # Delete dispatch
    dispatch.delete()
    assert len(dispatch.history()) == 3
    assert dispatch.history()[-1].status is None


@pytest.mark.now(NOW.isoformat())
@configs.MODELER_DECISION_CONFIG_DISABLED
@pytest.mark.parametrize(
    ['req_body'],
    [
        [{'dispatch_id': const.DISPATCH_ID}],
        [{'order_id': const.ORDER_ID}],
        [{'cargo_claim_id': 'claim 1'}],
    ],
)
async def test_dispatches_history_get_200(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        grocery_dispatch_extra_pg,
        cargo_pg,
        req_body,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        status='scheduled',
        performer=PerformerInfo(),
        dispatch_id=const.DISPATCH_ID,
        order=OrderInfo(order_id=const.ORDER_ID),
    )

    dispatch_extra = grocery_dispatch_extra_pg.create_dispatch_extra(
        dispatch_id=dispatch.dispatch_id,
    )

    base_time = parser.parse('2022-01-17T01:26:16.682155+00:00')
    dispatch_extra.eta_timestamp = base_time + datetime.timedelta(seconds=150)
    dispatch_extra.smoothed_eta_timestamp = base_time + datetime.timedelta(
        seconds=200,
    )
    dispatch_extra.smoothed_eta_eval_time = base_time + datetime.timedelta(
        seconds=10,
    )

    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id,
        claim_id='claim 1',
        claim_status='test 0',
        claim_version=101,
        is_current_claim=True,
    )
    assert len(dispatch.history()) == 1
    assert dispatch == dispatch.history()[0]

    # Update dispatch
    dispatch.status = 'canceled'
    assert len(dispatch.history()) == 2
    assert dispatch.history()[-1].status == 'canceled'

    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', req_body,
    )
    assert response.status_code == 200

    expected_eta_timestamp = dispatch_extra.eta_timestamp.astimezone(
        pytz.UTC,
    ).isoformat()
    expected_smoothed_eta_timestamp = (
        dispatch_extra.smoothed_eta_timestamp.astimezone(pytz.UTC).isoformat()
    )
    expected_smoothed_eta_eval_time = (
        dispatch_extra.smoothed_eta_eval_time.astimezone(pytz.UTC).isoformat()
    )

    expected_dispatch_history = [
        {
            'dispatch_id': dispatch.dispatch_id,
            'dispatch_type': 'test',
            'eta': 0,
            'order_id': '123123',
            'performer': {
                'driver_id': 'test_driver_id',
                'eats_profile_id': 'test_eats_profile_id',
                'park_id': 'test_park_id',
                'performer_id': 'test_performer_id',
                'performer_name': 'Тестовый Курьер Иванович',
            },
            'status': 'scheduled',
            'status_meta': {},
            'version': 0,
            'wave': 0,
        },
        {
            'dispatch_id': dispatch.dispatch_id,
            'dispatch_type': 'test',
            'eta': 0,
            'order_id': '123123',
            'performer': {
                'driver_id': 'test_driver_id',
                'eats_profile_id': 'test_eats_profile_id',
                'park_id': 'test_park_id',
                'performer_id': 'test_performer_id',
                'performer_name': 'Тестовый Курьер Иванович',
            },
            'status': 'canceled',
            'status_meta': {},
            'version': 1,
            'wave': 0,
        },
    ]

    expected_eta_history = [
        {},
        {'eta_timestamp': expected_eta_timestamp},
        {
            'eta_timestamp': expected_eta_timestamp,
            'smoothed_eta_timestamp': expected_smoothed_eta_timestamp,
        },
        {
            'eta_timestamp': expected_eta_timestamp,
            'smoothed_eta_timestamp': expected_smoothed_eta_timestamp,
            'smoothed_eta_eval_time': expected_smoothed_eta_eval_time,
        },
    ]

    assert response.json()['version_history'] == expected_dispatch_history
    assert response.json()['eta_history'] == expected_eta_history


@pytest.mark.now(NOW.isoformat())
async def test_dispatches_history_get_error(taxi_grocery_dispatch, mockserver):
    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/'
        'cold-storage/v1/get/dispatch_history',
    )
    def _cold_storage_response(req):
        return mockserver.make_response(json={'items': []}, status=200)

    request_data = {'dispatch_id': const.DISPATCH_ID}
    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', {'dispatch_id': const.DISPATCH_ID},
    )
    assert response.status_code == 404

    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', {},
    )
    assert response.status_code == 400

    request_data = {
        'dispatch_id': const.DISPATCH_ID,
        'cargo_claim_id': 'claim 1',
    }
    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', request_data,
    )
    assert response.status_code == 400


@pytest.mark.now(NOW.isoformat())
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_dispatch_history_claim_id(
        taxi_grocery_dispatch, cargo, grocery_supply, logistic_dispatcher,
):
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    cargo.check_request(
        route_points=[first_point, models.CLIENT_POINT, models.RETURN_POINT],
        items=cargo.convert_items(models.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
    )

    grocery_supply.add_log_group(const.DEPOT_ID, 'ya_eats_group')

    request_data = copy.deepcopy(models.CREATE_REQUEST_DATA)

    response1 = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', request_data,
    )
    assert response1.status_code == 200
    response1 = response1.json()
    dispatch_id = response1['dispatch_id']
    order_id = response1['order_id']
    claim_id = response1['status_meta']['cargo_dispatch']['claim_id']

    eta_seconds = 900
    eta_timestamp = (NOW + datetime.timedelta(seconds=eta_seconds)).isoformat()

    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', {'dispatch_id': dispatch_id},
    )

    expected_history = {
        'version_history': [
            {
                'dispatch_id': dispatch_id,
                'dispatch_type': 'cargo_sync',
                'eta': 0,
                'order_id': '123123',
                'status': 'idle',
                'status_meta': {},
                'version': 1,
                'wave': 0,
            },
            {
                'dispatch_id': dispatch_id,
                'dispatch_type': 'cargo_sync',
                'eta': 0,
                'failure_reason_type': 'new',
                'order_id': '123123',
                'status': 'scheduled',
                'status_meta': {
                    'cargo_dispatch': {
                        'claim_id': 'claim_1',
                        'dispatch_delivery_type': 'courier',
                    },
                },
                'version': 2,
                'wave': 0,
            },
        ],
        'eta_history': [{'result_eta_timestamp': eta_timestamp}],
    }

    assert response.status_code == 200
    assert response.json() == expected_history

    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', {'order_id': order_id},
    )
    assert response.status_code == 200
    assert response.json() == expected_history

    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', {'cargo_claim_id': claim_id},
    )
    assert response.status_code == 200
    assert response.json() == expected_history


async def test_dispatches_history_from_cold_storage(
        taxi_grocery_dispatch, mockserver, load_json,
):
    request_data = {'dispatch_id': '00035db7-e6cf-4eac-a812-e9da06c5cae8'}

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/'
        'cold-storage/v1/get/dispatch_history',
    )
    def _cold_storage_response(request):
        assert (
            request.json['item_id'] == '00035db7-e6cf-4eac-a812-e9da06c5cae8'
        )
        assert request.json['request_id_type'] == 'dispatch_id'
        return mockserver.make_response(
            json=load_json('cold_storage_response.json'), status=200,
        )

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/'
        'cold-storage/v1/get/dispatch_eta_history',
    )
    def _cold_storage_response(request):
        return mockserver.make_response(
            json=load_json('dispatch_extra_history_response.json'), status=200,
        )

    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', request_data,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'dispatch_history_from_cold_storage.json',
    )


async def test_dispatches_history_status_null(
        grocery_dispatch_pg, taxi_grocery_dispatch,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        status='scheduled', performer=PerformerInfo(),
    )
    assert len(dispatch.history()) == 1
    assert dispatch == dispatch.history()[0]

    dispatch_id = dispatch.dispatch_id

    # Delete dispatch
    dispatch.delete()
    assert len(dispatch.history()) == 2
    assert dispatch.history()[-1].status is None

    # Check detailed-info response 200
    response = await taxi_grocery_dispatch.post(
        '/admin/dispatch/v1/detailed_info', {'dispatch_id': dispatch_id},
    )
    assert response.status_code == 200
