import datetime

import pytest


TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


@pytest.fixture(name='mock_order_core')
def _mock_order_core(mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock(request):
        assert request.json == {
            'order_id': 'taxi_order_id_1',
            'require_latest': True,
            'fields': ['order.taxi_status'],
            'lookup_flags': 'none',
            'search_archive': False,
        }

        return mockserver.make_response(
            json={
                'order_id': 'taxi_order_id_1',
                'replica': 'master',
                'version': '1',
                'fields': {'order': {'taxi_status': 'waiting'}},
            },
            status=200,
        )

    return _mock


@pytest.fixture(name='mock_order_core_archive')
def _mock_order_core_archive(mockserver, load_json):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock(request):
        if not request.json['search_archive']:
            assert request.json == {
                'order_id': 'taxi_order_id_1',
                'require_latest': True,
                'fields': ['order.taxi_status'],
                'lookup_flags': 'none',
                'search_archive': False,
            }
            return mockserver.make_response(
                json={'code': 'not_found', 'message': 'order not found'},
                status=404,
            )
        assert request.json == {
            'order_id': 'taxi_order_id_1',
            'require_latest': False,
            'fields': ['order.taxi_status'],
            'lookup_flags': 'none',
            'search_archive': True,
        }

        return mockserver.make_response(
            json={
                'order_id': 'taxi_order_id_1',
                'replica': 'archive',
                'version': '1',
                'fields': {'order': {'taxi_status': 'complete'}},
            },
            status=200,
        )

    return _mock


@pytest.fixture(name='mock_xservice_status_change')
def _mock_xservice_status_change(mockserver):
    @mockserver.json_handler('/taximeter-xservice/utils/order/change_status')
    def _mock_xservice_status_change_send(request, *args, **kwargs):
        assert request.query['origin'] == 'cargo'
        assert request.json == {
            'db': 'park_id',
            'driver': 'driver_id',
            'order_alias_id': 'alias_id',
            'reason': 'reason',
            'status': 'transporting',
        }

        return mockserver.make_response(
            json={'status': 'driving', 'cost': 0}, status=200,
        )

    return _mock_xservice_status_change_send


@pytest.fixture(name='mock_driver_orders_app_api_status_change')
def _mock_driver_orders_app_api_status_change(mockserver):
    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/transporting',
    )
    def _mock_xservice_status_change_send(request, *args, **kwargs):
        assert request.json == {
            'park_id': 'park_id',
            'driver_profile_id': 'driver_id',
            'setcar_id': 'alias_id',
            'reason': 'reason',
            'origin': 'cargo',
        }

        return mockserver.make_response(
            json={'status': 'transporting', 'cost': 0}, status=200,
        )

    return _mock_xservice_status_change_send


async def test_stq(
        stq_runner,
        mock_order_core,
        mock_xservice_status_change,
        mockserver,
        state_controller,
):
    await state_controller.apply(target_status='performer_draft')

    now = datetime.datetime.utcnow().strftime(format=TIMESTAMP_FORMAT)
    await stq_runner.cargo_claims_xservice_change_status.call(
        task_id='task_id',
        args=[
            state_controller.get_flow_context().taxi_order_id,
            'park_id',
            'driver_id',
            'alias_id',
            'reason',
            'transporting',
            {'$date': now},
        ],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 1
    assert mock_xservice_status_change.times_called == 1


@pytest.mark.config(
    CARGO_CLAIMS_XSERVICE_CHANGE_STATUS={
        'task_ttl_in_minutes': 60,
        'use_driver_orders_app_api': True,
    },
)
async def test_stq_new_way(
        stq_runner,
        mock_order_core,
        mock_driver_orders_app_api_status_change,
        mockserver,
        state_controller,
):
    await state_controller.apply(target_status='performer_draft')

    now = datetime.datetime.utcnow().strftime(format=TIMESTAMP_FORMAT)
    await stq_runner.cargo_claims_xservice_change_status.call(
        task_id='task_id',
        args=[
            state_controller.get_flow_context().taxi_order_id,
            'park_id',
            'driver_id',
            'alias_id',
            'reason',
            'transporting',
            {'$date': now},
        ],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 1
    assert mock_driver_orders_app_api_status_change.times_called == 1


async def test_change_to_old_status(
        stq_runner, mock_order_core, mock_xservice_status_change, mockserver,
):
    now = datetime.datetime.utcnow().strftime(format=TIMESTAMP_FORMAT)
    await stq_runner.cargo_claims_xservice_change_status.call(
        task_id='task_id',
        args=[
            'taxi_order_id_1',
            'park_id',
            'driver_id',
            'alias_id',
            'reason',
            'waiting',
            {'$date': now},
        ],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 1
    assert mock_xservice_status_change.times_called == 0


async def test_order_from_archive(
        stq_runner,
        mock_order_core_archive,
        mock_xservice_status_change,
        mockserver,
        load_json,
):
    now = datetime.datetime.utcnow().strftime(format=TIMESTAMP_FORMAT)
    await stq_runner.cargo_claims_xservice_change_status.call(
        task_id='task_id',
        args=[
            'taxi_order_id_1',
            'park_id',
            'driver_id',
            'alias_id',
            'reason',
            'waiting',
            {'$date': now},
        ],
        expect_fail=False,
    )
    assert mock_order_core_archive.times_called == 2
    assert mock_xservice_status_change.times_called == 0


@pytest.mark.config(
    CARGO_CLAIMS_XSERVICE_CHANGE_STATUS={
        'task_ttl_in_minutes': 60,
        'use_driver_orders_app_api': True,
    },
)
@pytest.mark.parametrize('claims_should_notify_enabled', [False, True])
@pytest.mark.parametrize('orders_should_notify_enabled', [False, True])
async def test_stq_should_notify(
        stq_runner,
        mock_order_core,
        claims_should_notify_enabled,
        orders_should_notify_enabled,
        mockserver,
        taxi_config,
        taxi_cargo_claims,
):
    taxi_config.set_values(
        {
            'CARGO_DRIVER_ORDERS_APP_API_SHOULD_NOTIFY': {
                'claims_should_notify': claims_should_notify_enabled,
                'orders_should_notify': orders_should_notify_enabled,
            },
        },
    )
    await taxi_cargo_claims.invalidate_caches()

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/cancelled',
    )
    async def _mock_callback(request):
        if claims_should_notify_enabled:
            assert request.json['should_notify']
        else:
            assert 'should_notify' not in request.json

        return mockserver.make_response(
            json={'status': 'cancelled'}, status=200,
        )

    now = datetime.datetime.utcnow().strftime(format=TIMESTAMP_FORMAT)
    await stq_runner.cargo_claims_xservice_change_status.call(
        task_id='task_id',
        args=[
            'taxi_order_id_1',
            'park_id',
            'driver_id',
            'alias_id',
            'reason',
            'cancelled',
            {'$date': now},
        ],
        expect_fail=False,
    )

    assert _mock_callback.times_called == 1
