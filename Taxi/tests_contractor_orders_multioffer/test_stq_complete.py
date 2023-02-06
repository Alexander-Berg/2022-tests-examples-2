import pytest

from tests_contractor_orders_multioffer import pg_helpers as pgh

EMPTY_ID = '01234567-89ab-cdef-0123-456789abcdef'
SINGE_REJECT_ID = '11234567-89ab-cdef-0123-456789abcdef'
MULTI_REJECT_ID = '21234567-89ab-cdef-0123-456789abcdef'
MULTI_NO_ANSWER_ID = '31234567-89ab-cdef-0123-456789abcdef'
MULTI_NO_ANSWER_WITH_SEEN_ID = '41234567-89ab-cdef-0123-456789abcdef'
SINGE_ACCEPT_ID = '51234567-89ab-cdef-0123-456789abcdef'
MULTI_ACCEPT_ID = '61234567-89ab-cdef-0123-456789abcdef'

LOOKUP_ENRICHED_EVENT_REQUEST = {
    'status': 'found',
    'candidate': {
        'tags': ['some_tag'],
        'classes': ['econom'],
        'unique_driver_id': '60c9ccf18fe28d5ce431ce88',
        'license_id': '318fb895466a4cd599486ada5c5c0ffa',
        'route_info': {
            'time': 225,
            'distance': 1935,
            'properties': {'toll_roads': False},
            'approximate': False,
        },
        'chain_info': {
            'order_id': '7835cd0325ab2f2dabf7933e2d680a25',
            'left_dist': 767,
            'left_time': 129,
            'destination': [48.5748790393024, 54.38051404037958],
        },
        'metadata': {
            'multioffer': {
                'alias_id': 'alias_id1',
                'multioffer_id': 'multioffer_id',
            },
        },
    },
}


@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=[
        'multioffer_empty.sql',
        'multioffer_single_reject.sql',
        'multioffer_multi_reject.sql',
        'multioffer_multi_no_answer.sql',
        'multioffer_multi_no_answer_with_seen.sql',
    ],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.parametrize(
    'multioffer_id',
    [
        EMPTY_ID,
        SINGE_REJECT_ID,
        MULTI_REJECT_ID,
        MULTI_NO_ANSWER_ID,
        MULTI_NO_ANSWER_WITH_SEEN_ID,
    ],
)
async def test_stq_contractor_orders_multioffer_complete_empty(
        stq_runner,
        mocked_time,
        driver_orders_app_api,
        pgsql,
        multioffer_id,
        lookup,
        taxi_config,
        stq,
        mockserver,
):
    taxi_config.set_values(
        {
            'CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS': {
                'enable': True,
                'freeze_duration': 60,
            },
        },
    )
    order_id = f'order_id_{multioffer_id[0]}'
    callback_url = mockserver.url(
        f'lookup/event?order_id={order_id}&version=1&lookup_mode=multioffer',
    )
    pgh.update_callback_url(
        pgsql,
        multioffer_id,
        {'url': callback_url, 'timeout_ms': 100, 'attempts': 1},
    )
    await stq_runner.contractor_orders_multioffer_complete.call(
        task_id='task-id', args=[multioffer_id], kwargs={}, expect_fail=False,
    )

    cancel_count = int(
        multioffer_id in (MULTI_NO_ANSWER_ID, MULTI_NO_ANSWER_WITH_SEEN_ID),
    )
    assert driver_orders_app_api.bulk_cancel_called == cancel_count
    assert lookup.event_called_winner == 0
    assert stq.contractor_orders_multioffer_finalize.times_called == 0
    assert lookup.event_called_irrelevant == 1

    multioffer = pgh.select_multioffer(pgsql, multioffer_id)
    assert multioffer['id'] == multioffer_id
    assert multioffer['status'] == 'completed'


@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_single_accept.sql', 'multioffer_multi_accept.sql'],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.parametrize('multioffer_id', [SINGE_ACCEPT_ID, MULTI_ACCEPT_ID])
@pytest.mark.parametrize('enable_push', [True, False])
@pytest.mark.parametrize(
    'order_core_fields, cancel_winner',
    [
        ({'order': {'status': 'cancelled'}}, True),
        ({'order': {'status': 'pending', 'taxi_status': 'cancelled'}}, True),
        ({'order': {'status': 'pending'}}, False),
    ],
)
async def test_stq_contractor_orders_multioffer_complete_with_winner(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        stq_runner,
        driver_orders_app_api,
        pgsql,
        lookup,
        driver_freeze,
        taxi_config,
        multioffer_id,
        enable_push,
        order_core_fields,
        cancel_winner,
        order_proc,
        stq,
        client_notify,
        mockserver,
):
    order_proc.set_response(order_core_fields)
    taxi_config.set_values(
        {
            'CONTRACTOR_ORDERS_MULTIOFFER_SEND_ENRICHED_WINNER_TO_LOOKUP': (
                True
            ),
            'CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS': {
                'enable': True,
                'freeze_duration': 60,
            },
            'CONTRACTOR_ORDERS_MULTIOFFER_FINALIZE_SETTINGS': {
                'enable': True,
                'finalize_timeout': 20,
            },
            'CONTRACTOR_ORDERS_MULTIOFFER_PUSH_SETTINGS': {
                'enable_winner_push': enable_push,
                'enable_loser_push': enable_push,
            },
            'CONTRACTOR_ORDERS_MULTIOFFER_SEND_DRIVER_METRICS_EVENT_TYPES': {
                'reject': True,
                'accept': True,
                'seen_timeout': True,
                'offer_timeout': True,
            },
        },
    )

    order_id = (
        'order_id_6' if multioffer_id == MULTI_ACCEPT_ID else 'order_id_5'
    )
    callback_url = mockserver.url(
        f'lookup/event?order_id={order_id}&version=1&lookup_mode=multioffer',
    )
    pgh.update_callback_url(
        pgsql,
        multioffer_id,
        {'url': callback_url, 'timeout_ms': 100, 'attempts': 1},
    )

    lookup.asserted_event_request = LOOKUP_ENRICHED_EVENT_REQUEST
    lookup.asserted_event_request['candidate']['metadata']['multioffer'][
        'multioffer_id'
    ] = multioffer_id

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    await stq_runner.contractor_orders_multioffer_complete.call(
        task_id='task-id', args=[multioffer_id], kwargs={}, expect_fail=False,
    )

    cancel_called = int(multioffer_id == MULTI_ACCEPT_ID or cancel_winner)
    cancel_count = int(multioffer_id == MULTI_ACCEPT_ID) + int(cancel_winner)
    lookup_winner = not cancel_winner
    assert driver_orders_app_api.bulk_cancel_called == cancel_called
    assert driver_orders_app_api.bulk_cancelled_drivers == cancel_count
    assert lookup.event_called_winner == int(lookup_winner)
    assert lookup.event_called_irrelevant == 0
    push_count = 0
    if enable_push:
        push_count += int(multioffer_id == MULTI_ACCEPT_ID)  # for losers
        push_count += int(lookup_winner)  # for winner
    assert client_notify.times_called == push_count

    multioffer = pgh.select_multioffer(pgsql, multioffer_id)
    assert multioffer['id'] == multioffer_id
    assert multioffer['status'] == 'completed'

    assert stq.contractor_orders_multioffer_defreeze.times_called == int(
        cancel_called,
    )
    assert driver_freeze.defreeze_called == int(lookup_winner)

    # in every case only one non winner
    assert stq.driver_metrics_client.times_called == 1

    orders_metrics = (
        await taxi_contractor_orders_multioffer_monitor.get_metric(
            'multioffer_orders',
        )
    )
    assert orders_metrics['found'] == 1
    assert orders_metrics['no_winners'] == 0
    segment_order_metrics = orders_metrics['moscow']['test_dispatch']
    assert segment_order_metrics['found'] == 1
    assert segment_order_metrics['no_winners'] == 0

    accept_count = 2 if multioffer_id == MULTI_ACCEPT_ID else 1
    decline_count = 0 if multioffer_id == MULTI_ACCEPT_ID else 1
    driver_metrics = (
        await taxi_contractor_orders_multioffer_monitor.get_metric(
            'multioffer_driver',
        )
    )
    assert driver_metrics['accepted'] == accept_count
    assert driver_metrics['declined'] == decline_count
    segment_driver_metrics = driver_metrics['moscow']['test_dispatch']
    assert segment_driver_metrics['accepted'] == accept_count
    assert segment_driver_metrics['declined'] == decline_count


@pytest.mark.parametrize(
    'multioffer_id', ('ecc6dc92-6d56-48a3-884d-f31390cd9a3c',),
)
@pytest.mark.parametrize('wave', [1, 2])
@pytest.mark.parametrize('accepted', [True, False])
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_multiwave_1_in_progress.sql'],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_stq_complete_multiwaves(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        stq_runner,
        driver_orders_app_api,
        taxi_config,
        pgsql,
        load,
        lookup,
        stq,
        mockserver,
        multioffer_id,
        wave,
        accepted,
):
    # Arrange
    if wave >= 2:
        pgh.execute(pgsql, load('multioffer_multiwave_complete.sql'))
        pgh.execute(pgsql, load('multioffer_multiwave_2_in_progress.sql'))
    if accepted:
        pgh.execute(pgsql, load('multioffer_multiwave_accept.sql'))

    callback_url = mockserver.url(
        f'lookup/event?order_id=order_id&version=1&lookup_mode=multioffer',
    )
    pgh.update_callback_url(
        pgsql,
        multioffer_id,
        {'url': callback_url, 'timeout_ms': 100, 'attempts': 1},
    )

    # Act
    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    await stq_runner.contractor_orders_multioffer_complete.call(
        task_id='task-id',
        args=[multioffer_id, wave],
        kwargs={},
        expect_fail=False,
    )

    # Assert
    completed = wave == 2 or accepted
    assert driver_orders_app_api.bulk_cancel_called == int(not accepted)
    assert driver_orders_app_api.bulk_cancelled_drivers == int(not accepted)
    assert lookup.event_called_winner == int(completed and accepted)
    assert lookup.event_called_irrelevant == int(completed and not accepted)
    assert stq.contractor_orders_multioffer_finalize.times_called == 0

    multioffer = pgh.select_multioffer(pgsql, multioffer_id)
    assert multioffer['id'] == multioffer_id
    assert multioffer['status'] == 'completed' if accepted else 'in_progress'

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer_id)
    assert len(drivers) == (wave * 2)

    driver_metrics = (
        await taxi_contractor_orders_multioffer_monitor.get_metric(
            'multioffer_driver',
        )
    )
    orders_metrics = (
        await taxi_contractor_orders_multioffer_monitor.get_metric(
            'multioffer_orders',
        )
    )

    expect_accepted = 1 if completed and accepted else 0
    expect_declined = (2 * wave if completed else 0) - expect_accepted
    expect_waves = wave if completed else 0

    assert driver_metrics['accepted'] == expect_accepted
    assert driver_metrics['declined'] == expect_declined
    assert orders_metrics['waves_avg'] == expect_waves
    if completed:
        segment_driver_metrics = driver_metrics['moscow']['test_multioffer']
        segment_order_metrics = orders_metrics['moscow']['test_multioffer']
        assert segment_driver_metrics['accepted'] == expect_accepted
        assert segment_driver_metrics['declined'] == expect_declined
        assert segment_order_metrics['waves_avg'] == expect_waves
    else:
        assert 'moscow' not in driver_metrics
        assert 'moscow' not in orders_metrics


@pytest.mark.parametrize(
    'multioffer_id', ('72bcbde8-eaed-460f-8f88-eeb4e056c317',),
)
@pytest.mark.parametrize('accepted', (True, False), ids=('accepted', ''))
@pytest.mark.parametrize('rejected', (True, False), ids=('rejected', ''))
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_bid_create.sql', 'multioffer_bid_create_bids.sql'],
)
@pytest.mark.now('2022-05-30T12:00:00.000000Z')
async def test_stq_complete_auction(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        stq_runner,
        driver_orders_app_api,
        pgsql,
        load,
        lookup,
        stq,
        mockserver,
        multioffer_id,
        accepted,
        rejected,
):
    # Arrange
    if accepted:
        pgh.execute(pgsql, load('multioffer_bid_accept_bid.sql'))
    if rejected:
        pgh.execute(pgsql, load('multioffer_bid_reject_bid.sql'))

    callback_url = mockserver.url(
        f'lookup/event?order_id=order_id&version=1&lookup_mode=multioffer',
    )
    pgh.update_callback_url(
        pgsql,
        multioffer_id,
        {'url': callback_url, 'timeout_ms': 100, 'attempts': 1},
    )

    # Act
    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    await stq_runner.contractor_orders_multioffer_complete.call(
        task_id='task-id',
        args=[multioffer_id, 1],
        kwargs={},
        expect_fail=False,
    )

    # Assert
    expect_cancel = 1 if accepted else 0
    expect_winner = 1 if accepted else 0
    assert driver_orders_app_api.bulk_cancel_called == expect_cancel
    assert driver_orders_app_api.bulk_cancelled_drivers == expect_cancel
    assert lookup.event_called_winner == expect_winner
    assert lookup.event_called_irrelevant == 0
    assert stq.contractor_orders_multioffer_finalize.times_called == 0

    multioffer = pgh.select_multioffer(pgsql, multioffer_id)
    assert multioffer['id'] == multioffer_id
    assert multioffer['status'] == 'completed' if accepted else 'in_progress'

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer_id)
    assert len(drivers) == 2

    bids = pgh.select_multioffer_bids(pgsql, multioffer_id)
    assert len(bids) == 3

    if accepted:
        assert lookup.candidate['uuid'] == 'driver_profile_id_1'
        assert lookup.candidate['auction']['accepted_driver_price'] == 1000.0
    else:
        assert lookup.candidate is None

    def get_status(collection, driver_id, field, prohibited_values):
        return next(
            x
            for x in collection
            if x['driver_profile_id'] == driver_id
            and x[field] not in prohibited_values
        )[field]

    driver_1_status = get_status(
        drivers, 'driver_profile_id_1', 'offer_status', set(),
    )
    driver_2_status = get_status(
        drivers, 'driver_profile_id_2', 'offer_status', set(),
    )
    bid_1_status = get_status(
        bids, 'driver_profile_id_1', 'status', {'rejected', 'cancelled'},
    )
    bid_2_status = get_status(bids, 'driver_profile_id_2', 'status', set())

    assert driver_1_status == 'win' if accepted else 'accepted'
    assert driver_2_status == 'lose' if accepted else 'accepted'
    assert bid_1_status == 'won' if accepted else 'created'
    assert bid_2_status == (
        'rejected' if rejected else 'lost' if accepted else 'created'
    )

    driver_metrics = (
        await taxi_contractor_orders_multioffer_monitor.get_metric(
            'multioffer_driver',
        )
    )
    orders_metrics = (
        await taxi_contractor_orders_multioffer_monitor.get_metric(
            'multioffer_orders',
        )
    )

    if accepted:
        assert driver_metrics['accepted'] == 2
        assert driver_metrics['declined'] == 0

        segment_driver_metrics = driver_metrics['moscow']['auction']
        assert segment_driver_metrics['accepted'] == 2
        assert segment_driver_metrics['declined'] == 0
    else:
        assert driver_metrics['accepted'] == 0
        assert driver_metrics['declined'] == 0
        assert 'moscow' not in driver_metrics
        assert 'moscow' not in orders_metrics
