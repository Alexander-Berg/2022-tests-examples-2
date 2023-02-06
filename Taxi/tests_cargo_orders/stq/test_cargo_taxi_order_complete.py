import pytest


@pytest.mark.parametrize(
    'claims_response',
    (
        {
            'json': {'id': 'some_claim_id', 'status': 'delivered_finish'},
            'status': 200,
        },
        {
            'json': {'message': 'bad request', 'code': 'double_request'},
            'status': 404,
        },
        {
            'json': {'message': 'bad order_id', 'code': 'old_version'},
            'status': 409,
        },
        {
            'json': {
                'message': 'inappropriate_status',
                'code': 'inappropriate_status',
            },
            'status': 409,
        },
        {
            'json': {'message': 'terminal_status', 'code': 'terminal_status'},
            'status': 409,
        },
    ),
)
async def test_dragon(
        stq_runner,
        default_order_id,
        mockserver,
        fetch_order,
        claims_response: dict,
):
    @mockserver.json_handler(
        '/cargo-claims/v1/claims/mark/taxi-order-complete',
    )
    def mock_order_complete(request):
        assert request.query == {
            'segment_id': 'some_segment_id',
            'claim_id': 'some_claim_id',
        }
        assert request.json == {
            'taxi_order_id': 'taxi-order',
            'reason': 'taxi_order_complete',
            'lookup_version': 1,
        }
        return {'id': request.args['claim_id'], 'status': 'delivered_finish'}

    await stq_runner.cargo_taxi_order_complete.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'event_timestamp': '2020-06-17T22:40:00+0300',
        },
        expect_fail=False,
    )

    assert mock_order_complete.times_called == 1

    order_doc = fetch_order(default_order_id)
    assert str(order_doc.complete_time) == '2020-06-17 22:40:00+03:00'


@pytest.mark.parametrize(
    ('claims_response', 'will_retry'),
    (
        (
            {
                'json': {
                    'message': 'bad status',
                    'code': 'inappropriate_status',
                },
                'status': 409,
            },
            True,
        ),
        (
            {
                'json': {'message': 'bad order_id', 'code': 'old_version'},
                'status': 409,
            },
            False,
        ),
        (
            {
                'json': {
                    'message': 'already in terminal status',
                    'code': 'terminal_status',
                },
                'status': 409,
            },
            False,
        ),
    ),
)
@pytest.mark.config(
    CARGO_TAXI_ORDER_COMPLETE_SETTINGS={'retry_after_wrong_status': True},
)
async def test_retry_409(
        stq_runner,
        default_order_id,
        mocker_order_complete,
        claims_response: dict,
        will_retry: bool,
):
    mock_order_complete = mocker_order_complete(**claims_response)

    await stq_runner.cargo_taxi_order_complete.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'event_timestamp': '2020-06-17T22:40:00+0300',
        },
        expect_fail=will_retry,
    )
    assert mock_order_complete.times_called == 1


async def test_basic_order_cancel_statistics(
        stq_runner,
        default_order_id,
        mocker_order_complete,
        insert_performer_order_cancel_statistics,
        query_performer_order_cancel_statistics,
):
    insert_performer_order_cancel_statistics(dbid_uuid_='park_id1_driver_id1')

    mocker_order_complete(
        json={
            'id': 'cc0431b859b94324bb388d55a129a78e',
            'status': 'performer_found',
        },
        status=200,
    )

    await stq_runner.cargo_taxi_order_complete.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'event_timestamp': '2020-06-17T22:40:00+0300',
        },
        expect_fail=False,
    )
    result = query_performer_order_cancel_statistics(
        dbid_uuid_='park_id1_driver_id1',
    )[0]
    assert result.dbid_uuid == 'park_id1_driver_id1'
    assert result.completed_orders == 1
    assert result.cancellation_count == 1


async def test_dragon_performer_cancel_statistics(
        stq_runner,
        default_order_id,
        mockserver,
        insert_performer_order_cancel_statistics,
        query_performer_order_cancel_statistics,
):
    insert_performer_order_cancel_statistics(dbid_uuid_='park_id1_driver_id1')

    @mockserver.json_handler(
        '/cargo-claims/v1/claims/mark/taxi-order-complete',
    )
    def _mock_order_complete(request):
        assert request.query == {
            'segment_id': 'some_segment_id',
            'claim_id': 'some_claim_id',
        }
        assert request.json == {
            'taxi_order_id': 'taxi-order',
            'reason': 'taxi_order_complete',
            'lookup_version': 1,
        }
        return {'id': request.args['claim_id'], 'status': 'delivered_finish'}

    await stq_runner.cargo_taxi_order_complete.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'event_timestamp': '2020-06-17T22:40:00+0300',
        },
        expect_fail=False,
    )

    result = query_performer_order_cancel_statistics(
        dbid_uuid_='park_id1_driver_id1',
    )[0]
    assert result.dbid_uuid == 'park_id1_driver_id1'
    assert result.completed_orders == 1
    assert result.cancellation_count == 1


async def test_use_new_cancellations_counter(
        stq_runner,
        default_order_id,
        mocker_order_complete,
        stq,
        exp_cargo_orders_use_performer_fines_service,
):
    mocker_order_complete(
        json={
            'id': 'cc0431b859b94324bb388d55a129a78e',
            'status': 'performer_found',
        },
        status=200,
    )

    await stq_runner.cargo_taxi_order_complete.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'event_timestamp': '2020-06-17T22:40:00+0300',
        },
        expect_fail=False,
    )

    stq_call = stq.cargo_performer_fines_taxi_order_complete.next_call()
    assert stq_call['id'] == 'test_stq'
    assert stq_call['kwargs']['cargo_order_id'] == default_order_id
    assert stq_call['kwargs']['driver_id'] == 'driver_id1'
    assert stq_call['kwargs']['park_id'] == 'park_id1'
    assert stq_call['kwargs']['tariff_class'] == 'cargo'
