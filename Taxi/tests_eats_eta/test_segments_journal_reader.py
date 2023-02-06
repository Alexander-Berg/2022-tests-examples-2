import datetime

from . import utils


TASK_NAME = 'segments-journal-reader'
CURSOR = 'whatever'


@utils.eats_eta_settings_config3()
async def test_segments_journal_reader(
        mockserver,
        make_order,
        db_insert_order,
        db_select_orders,
        load_json,
        stq_runner,
        get_segments_journal_cursor,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def mock_cargo_segments_journal(request):
        assert 'cursor' not in request.json
        return mockserver.make_response(
            status=200,
            headers={'X-Polling-Delay-Ms': '10'},
            json={
                'cursor': 'whatever',
                'entries': [
                    *[
                        {
                            'segment_id': f'segment-id-{i}',
                            'created_ts': '2022-04-27T00:00:00.000000+00:00',
                            'revision': 1,
                            'current': {
                                'claim_id': f'claim-id-{i}',
                                'points_user_version': 1,
                            },
                        }
                        for i in range(6)
                    ],
                    *[
                        {
                            'segment_id': f'segment-id-{i}',
                            'created_ts': '2022-04-27T00:00:00.000000+00:00',
                            'revision': 2,
                            'current': {
                                'claim_id': f'claim-id-{i}',
                                'points_user_version': 1,
                            },
                        }
                        for i in range(6)
                    ],
                ],
            },
        )

    @mockserver.json_handler('/cargo-claims/v1/segments/info')
    def mock_cargo_segments_info(request):
        order_id = int(request.query['segment_id'][-1])
        json = load_json('segment_info.json')
        if order_id < 3:
            json['claim_id'] = f'claim-id-{order_id}'
            json['performer_info']['park_id'] = 'chain-park-id'
            json['performer_info']['driver_id'] = 'chain-driver-id'
            json[
                'pickuped_time'
            ] = f'2022-04-27T0{3 - order_id}:00:00.000000+00:00'
        else:
            json['claim_id'] = f'claim-id-{order_id}'
            json['performer_info']['park_id'] = 'chain-park-id'
            json['performer_info']['driver_id'] = f'driver-id-{order_id}'
            json['pickuped_time'] = '2022-04-27T00:00:00.000000+00:00'
        return mockserver.make_response(status=200, json=json)

    chained_orders = [
        make_order(id=i, order_nr=f'order-nr-{i}', claim_id=f'claim-id-{i}')
        for i in range(3)
    ]
    not_chained_orders = [
        make_order(id=i, order_nr=f'order-nr-{i}', claim_id=f'claim-id-{i}')
        for i in range(3, 6)
    ]
    orders = [*chained_orders, *not_chained_orders]
    for order in orders:
        db_insert_order(order)

    await stq_runner.eats_eta_read_segments_journal.call(
        task_id=TASK_NAME, kwargs={},
    )
    assert mock_cargo_segments_journal.times_called == 1
    assert mock_cargo_segments_info.times_called == 6

    for order in chained_orders:
        order_id = order['id']
        order['park_id'] = 'chain-park-id'
        order['driver_id'] = 'chain-driver-id'
        order['segment_pickuped_time'] = utils.parse_datetime(
            f'2022-04-27T0{3 - order_id}:00:00.000000+00:00',
        )
        order['chained_orders'] = [2, 1, 0]
    for order in not_chained_orders:
        order_id = order['id']
        order['park_id'] = 'chain-park-id'
        order['driver_id'] = f'driver-id-{order_id}'
        order['segment_pickuped_time'] = utils.parse_datetime(
            '2022-04-27T00:00:00.000000+00:00',
        )

    assert db_select_orders() == orders
    assert get_segments_journal_cursor() == CURSOR


@utils.eats_eta_settings_config3(max_order_validity_time=30)
async def test_segments_journal_skip_outdated_orders(
        now_utc,
        mockserver,
        make_order,
        db_insert_order,
        db_select_orders,
        load_json,
        stq_runner,
        get_segments_journal_cursor,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def mock_cargo_segments_journal(request):
        assert 'cursor' not in request.json
        return mockserver.make_response(
            status=200,
            headers={'X-Polling-Delay-Ms': '10'},
            json={
                'cursor': CURSOR,
                'entries': [
                    *[
                        {
                            'segment_id': f'segment-id-{i}',
                            'created_ts': '2022-04-27T00:00:00.000000+00:00',
                            'revision': 1,
                            'current': {
                                'claim_id': f'claim-id-{i}',
                                'points_user_version': 1,
                            },
                        }
                        for i in range(4)
                    ],
                ],
            },
        )

    @mockserver.json_handler('/cargo-claims/v1/segments/info')
    def mock_cargo_segments_info(request):
        order_id = int(request.query['segment_id'][-1])
        json = load_json('segment_info.json')
        json['claim_id'] = f'claim-id-{order_id}'
        json['performer_info']['park_id'] = 'chain-park-id'
        json['performer_info']['driver_id'] = 'chain-driver-id'
        json[
            'pickuped_time'
        ] = f'2022-04-27T0{4 - order_id}:00:00.000000+00:00'
        return mockserver.make_response(status=200, json=json)

    orders = [
        make_order(id=i, order_nr=f'order-nr-{i}', claim_id=f'claim-id-{i}')
        for i in range(4)
    ]
    # Устаревший заказ, у которого не обновлялся статус более
    # max_order_validity_time минут
    orders[1]['status_changed_at'] -= datetime.timedelta(minutes=31)
    # Устаревший заказ ко времени
    orders[2]['delivery_date'] = now_utc - datetime.timedelta(minutes=31)
    # Устаревший заказ в слот
    orders[3]['delivery_slot_finished_at'] = now_utc - datetime.timedelta(
        minutes=31,
    )
    for order in orders:
        db_insert_order(order)

    await stq_runner.eats_eta_read_segments_journal.call(
        task_id=TASK_NAME, kwargs={},
    )
    assert mock_cargo_segments_journal.times_called == 1
    assert mock_cargo_segments_info.times_called == 4

    for order in orders:
        order_id = order['id']
        order['park_id'] = 'chain-park-id'
        order['driver_id'] = 'chain-driver-id'
        order['segment_pickuped_time'] = utils.parse_datetime(
            f'2022-04-27T0{4 - order_id}:00:00.000000+00:00',
        )
        order['chained_orders'] = None

    assert db_select_orders() == orders
    assert get_segments_journal_cursor() == CURSOR


@utils.eats_eta_settings_config3()
async def test_segments_journal_reader_complete_orders(
        mockserver,
        make_order,
        db_insert_order,
        db_select_orders,
        load_json,
        stq_runner,
        get_segments_journal_cursor,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def mock_cargo_segments_journal(request):
        assert 'cursor' not in request.json
        return mockserver.make_response(
            status=200,
            headers={'X-Polling-Delay-Ms': '10'},
            json={
                'cursor': CURSOR,
                'entries': [
                    {
                        'segment_id': f'segment-id-{i}',
                        'created_ts': '2022-04-27T00:00:00.000000+00:00',
                        'revision': 1,
                        'current': {
                            'claim_id': f'claim-id-{i}',
                            'points_user_version': 1,
                        },
                    }
                    for i in range(6)
                ],
            },
        )

    @mockserver.json_handler('/cargo-claims/v1/segments/info')
    def mock_cargo_segments_info(request):
        order_id = int(request.query['segment_id'][-1])
        json = load_json('segment_info.json')
        json['claim_id'] = f'claim-id-{order_id}'
        json['performer_info']['park_id'] = 'chain-park-id'
        json['performer_info']['driver_id'] = 'chain-driver-id'
        json[
            'pickuped_time'
        ] = f'2022-04-27T0{6 - order_id}:00:00.000000+00:00'
        return mockserver.make_response(status=200, json=json)

    orders = [
        make_order(id=i, order_nr=f'order-nr-{i}', claim_id=f'claim-id-{i}')
        for i in range(6)
    ]
    for order in orders:
        # default max_order_validity_time diff is 12 hours
        order['created_at'] -= datetime.timedelta(hours=11)
        order['status_changed_at'] -= datetime.timedelta(hours=11)
    orders[5]['order_status'] = 'complete'
    orders[3]['order_status'] = 'cancelled'
    orders[1]['order_status'] = 'auto_complete'
    for order in orders:
        db_insert_order(order)

    await stq_runner.eats_eta_read_segments_journal.call(
        task_id=TASK_NAME, kwargs={},
    )
    assert mock_cargo_segments_journal.times_called == 1
    assert mock_cargo_segments_info.times_called == 6

    for order in orders:
        order_id = order['id']
        order['park_id'] = 'chain-park-id'
        order['driver_id'] = 'chain-driver-id'
        order['segment_pickuped_time'] = utils.parse_datetime(
            f'2022-04-27T0{6 - order_id}:00:00.000000+00:00',
        )
        if order_id in [0, 2, 4]:
            order['chained_orders'] = [4, 2, 0]

    assert db_select_orders() == orders
    assert get_segments_journal_cursor() == CURSOR
