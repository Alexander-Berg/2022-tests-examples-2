import datetime

import pytest

from testsuite.utils import matching

CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG = [
    {
        'scores': [1, 2, 3, 4],
        'reason_id': 'too_long_delivery',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.too_long_delivery',
            'keyset': 'cargo',
        },
    },
    {
        'scores': [1, 2, 3, 4],
        'reason_id': 'some_default_reason',
        'tanker_key': {
            'key': (
                'client_message.feedback_action.reasons.some_default_reason'
            ),
            'keyset': 'cargo',
        },
    },
    {
        'scores': [1, 2, 3, 4],
        'allowed_for': [
            {
                'tariffs': ['courier'],
                'taxi_requirements': ['some_undefined_requirement'],
            },
        ],
        'reason_id': 'unable_to_contact',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.unable_to_contact',
            'keyset': 'cargo',
        },
    },
    {
        'scores': [1],
        'reason_id': 'order_wasnt_delivered',
        'allowed_for': [
            {
                'tariffs': ['courier'],
                'taxi_requirements': ['door_to_door', 'cargo_loaders'],
            },
        ],
        'tanker_key': {
            'key': (
                'client_message.feedback_action.reasons.order_wasnt_delivered'
            ),
            'keyset': 'cargo',
        },
    },
    {
        'scores': [1, 2, 3, 4],
        'allowed_for': [{'has_comment': True}],
        'reason_id': 'comment',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.comment',
            'keyset': 'cargo',
        },
    },
    {
        'scores': [5],
        'reason_id': 'perfect',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.perfect',
            'keyset': 'cargo',
        },
        'icon': {
            'active': 'delivery_perfect_active_icon',
            'inactive': 'delivery_perfect_inactive_icon',
        },
    },
]


def get_proc(order_id):
    return {
        '_id': order_id,
        'order': {
            'status': 'finished',
            'taxi_status': 'complete',
            'request': {
                'class': ['courier'],
                'source': {
                    'uris': ['some uri'],
                    'geopoint': [37.642859, 55.735316],
                    'fullname': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора1',
                    'description': 'Москва, Россия',
                    'porchnumber': '4',
                    'extra_data': {},
                },
                'destinations': [
                    {
                        'uris': ['some uri2'],
                        'geopoint': [37.642859, 55.735316],
                        'fullname': 'Россия, Чебоксары, Крутая улица 83',
                        'short_text': 'БЦ Аврора2',
                        'description': 'Чебоксары, Россия',
                        'porchnumber': '5',
                        'extra_data': {},
                    },
                    {
                        'uris': ['some uri3'],
                        'geopoint': [37.642859, 55.725218],
                        'fullname': 'Россия, Таганрог, Большая улица 18',
                        'short_text': 'БЦ Мармелад',
                        'description': 'Таганрог, Россия',
                        'porchnumber': '6',
                        'extra_data': {},
                    },
                ],
            },
        },
        'candidates': [
            {
                'first_name': 'Иван',
                'name': 'Petr',
                'phone_personal_id': '+7123_id',
                'driver_id': 'clid_driverid1',
                'db_id': 'parkid1',
            },
        ],
        'created': datetime.datetime(2019, 3, 17, 0, 0, 0, 0),
        'performer': {'candidate_index': 0},
        'user_phone_id': 'yataxi_phone_id',
    }


async def test_create(
        taxi_cargo_c2c,
        pgsql,
        create_cargo_claims_orders,
        get_default_order_id,
):
    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT phone_pd_id, roles, order_id, order_provider_id
    FROM cargo_c2c.clients_orders
        """,
    )
    assert list(cursor) == [
        ('phone_pd_id_1', '{sender}', get_default_order_id(), 'cargo-claims'),
        (
            'phone_pd_id_2',
            '{recipient}',
            get_default_order_id(),
            'cargo-claims',
        ),
        (
            'phone_pd_id_3',
            '{recipient}',
            get_default_order_id(),
            'cargo-claims',
        ),
    ]


async def test_create_twice(taxi_cargo_c2c, get_default_order_id):
    request = {
        'orders': [
            {
                'id': {
                    'phone_pd_id': 'phone_pd_id_1',
                    'order_id': get_default_order_id(),
                    'order_provider_id': 'cargo-claims',
                },
                'roles': ['sender'],
            },
        ],
    }

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'additional_delivery_description': {},
                'id': {
                    'order_id': get_default_order_id(),
                    'order_provider_id': 'cargo-claims',
                    'phone_pd_id': 'phone_pd_id_1',
                },
                'roles': ['sender'],
                'sharing_key': matching.AnyString(),
                'user_id': 'user_id_1_2',
            },
        ],
    }

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {'orders': []}


async def test_do_not_show_in_go(taxi_cargo_c2c, pgsql, get_default_order_id):
    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders',
        json={
            'orders': [
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_1',
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'cargo-claims',
                        'do_not_show_in_go': True,
                    },
                    'roles': ['sender'],
                },
            ],
        },
    )
    assert response.status_code == 200


async def test_user_id(taxi_cargo_c2c, pgsql, create_cargo_claims_orders):
    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT user_id
    FROM cargo_c2c.clients_orders
        """,
    )
    assert list(cursor) == [('user_id_1_2',), ('user_id_2_2',), (None,)]


async def test_mark_order_terminated(
        taxi_cargo_c2c,
        pgsql,
        create_cargo_claims_orders,
        get_default_order_id,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/mark-order-terminated',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'resolution': 'succeed',
        },
    )
    assert response.status_code == 200
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/mark-order-terminated',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'resolution': 'succeed',
        },
    )
    assert response.status_code == 200
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/mark-order-terminated',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_3',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'resolution': 'failed',
        },
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT terminated_at IS NOT NULL
    FROM cargo_c2c.clients_orders
        """,
    )
    assert list(cursor) == [(True,), (True,), (True,)]


@pytest.mark.parametrize(
    'feedback_type, score, query_args, result, overlapped_result',
    [
        (
            'order_feedback',
            4,
            'score, comment, reasons',
            (4, 'some comment', ['too_long_delivery', 'some_default_reason']),
            (4, 'another comment', None),
        ),
        (
            'cancel_feedback',
            None,
            'cancel_comment, cancel_reasons',
            ('some comment', ['too_long_delivery', 'some_default_reason']),
            ('another comment', None),
        ),
    ],
)
@pytest.mark.config(
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
)
async def test_save_feedback(
        taxi_cargo_c2c,
        pgsql,
        create_cargo_c2c_orders,
        get_default_order_id,
        feedback_type,
        score,
        query_args,
        result,
        overlapped_result,
):
    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': feedback_type,
            'score': score,
            'comment': 'some comment',
            'reasons': [
                {'reason_id': 'too_long_delivery'},
                {'reason_id': 'some_default_reason'},
            ],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        f"""
    SELECT {query_args}
    FROM cargo_c2c.clients_feedbacks
        """,
    )
    assert list(cursor) == [result]

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': feedback_type,
            'score': score,
            'comment': 'another comment',
        },
    )
    assert response.status_code == 200
    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        f"""
    SELECT {query_args}
    FROM cargo_c2c.clients_feedbacks
        """,
    )
    assert list(cursor) == [overlapped_result]


@pytest.mark.config(
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
)
async def test_cancel_with_order_feedbacks(
        taxi_cargo_c2c, pgsql, create_cargo_c2c_orders, get_default_order_id,
):
    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
            'score': 4,
            'comment': 'some comment',
            'reasons': [
                {'reason_id': 'too_long_delivery'},
                {'reason_id': 'some_default_reason'},
            ],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT score, comment, reasons, cancel_comment, cancel_reasons
    FROM cargo_c2c.clients_feedbacks
        """,
    )
    assert list(cursor) == [
        (
            4,
            'some comment',
            ['too_long_delivery', 'some_default_reason'],
            None,
            None,
        ),
    ]

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'cancel_feedback',
            'comment': 'some cancel comment',
            'reasons': [{'reason_id': 'c'}, {'reason_id': 'd'}],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT score, comment, reasons, cancel_comment, cancel_reasons
    FROM cargo_c2c.clients_feedbacks
        """,
    )
    assert list(cursor) == [
        (
            4,
            'some comment',
            ['too_long_delivery', 'some_default_reason'],
            'some cancel comment',
            ['c', 'd'],
        ),
    ]


async def test_save_feedback404(
        taxi_cargo_c2c,
        pgsql,
        create_cargo_claims_orders,
        get_default_order_id,
):
    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': 'abacaba',
                'order_provider_id': 'cargo-claims',
            },
            'type': 'order_feedback',
            'score': 4,
            'reasons': [{'reason_id': 'a'}, {'reason_id': 'b'}],
        },
    )
    assert response.status_code == 404


async def test_send_taxi_feedback_c2c(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        mock_claims_full,
        order_archive_mock,
        mockserver,
        mock_passenger_feedback,
        stq_runner,
        stq,
):

    order_id = await create_cargo_c2c_orders()
    order_archive_mock.set_order_proc(get_proc('some_taxi_order_id'))

    # FIRST TAXI FEEDBACK SEND

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
            'score': 4,
        },
    )
    assert response.status_code == 200

    # sender sent 4

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
            'score': 3,
        },
    )
    assert response.status_code == 200

    # recipient sent 3

    mock_passenger_feedback.expected_rating = 3
    await stq_runner.cargo_c2c_send_taxi_feedback.call(
        task_id='2',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            {'type': 'percent', 'decimal_value': '0'},
            3,
        ],
    )
    assert mock_passenger_feedback.times_called == 1

    # SECOND TAXI FEEDBACK SEND

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
            'score': 1,
        },
    )
    assert response.status_code == 200

    # sender sent 1

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
            'score': 5,
        },
    )
    assert response.status_code == 200

    # recipient sent 5

    mock_passenger_feedback.expected_rating = 3
    await stq_runner.cargo_c2c_send_taxi_feedback.call(
        task_id='3',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            {'type': 'percent', 'decimal_value': '0'},
            3,
        ],
    )
    assert mock_passenger_feedback.times_called == 2


async def test_send_taxi_feedback_claims(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        mock_claims_full,
        order_archive_mock,
        mockserver,
        mock_passenger_feedback,
        stq_runner,
        stq,
        get_default_order_id,
):
    order_archive_mock.set_order_proc(get_proc('some_taxi_order_id'))

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'type': 'order_feedback',
            'score': 5,
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'type': 'order_feedback',
            'score': 1,
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_3',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'type': 'order_feedback',
            'score': 3,
        },
    )
    assert response.status_code == 200

    mock_passenger_feedback.expected_rating = 3
    await stq_runner.cargo_c2c_send_taxi_feedback.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            {'type': 'percent', 'decimal_value': '0'},
            3,
        ],
    )
    assert mock_passenger_feedback.times_called == 1


async def test_send_taxi_feedback_logistic_platform(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        mock_claims_full,
        order_archive_mock,
        mockserver,
        mock_passenger_feedback,
        mock_logistic_platform,
        mock_order_statuses_history,
        stq_runner,
        stq,
        get_default_order_id,
):
    await create_logistic_platform_orders()
    order_archive_mock.set_order_proc(get_proc('some_taxi_order_id'))
    mock_logistic_platform.file_name = 'delivered.json'
    mock_order_statuses_history.file_name = 'delivered.json'

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
            },
            'type': 'order_feedback',
            'score': 5,
        },
    )
    assert response.status_code == 200

    mock_passenger_feedback.expected_rating = 5
    await stq_runner.cargo_c2c_send_taxi_feedback.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
            },
            {'type': 'percent', 'decimal_value': '0'},
            5,
        ],
    )
    assert mock_passenger_feedback.times_called == 1


@pytest.mark.parametrize(
    'user_choice, times_called, phone_pd_id, selected_tips, tips_sent',
    [
        (
            {'decimal_value': '200.00', 'type': 'flat'},
            0,
            'phone_pd_id_1',
            ('0', 'flat'),
            None,
        ),
        (
            {'decimal_value': '200.00', 'type': 'flat'},
            0,
            'phone_pd_id_2',
            ('0', 'flat'),
            None,
        ),
        (
            {'decimal_value': '200.00', 'type': 'flat'},
            1,
            'phone_pd_id_3',
            ('200.00', 'flat'),
            {'decimal_value': '200.00', 'type': 'flat'},
        ),
        (
            {'decimal_value': '0', 'type': 'flat'},
            1,
            'phone_pd_id_3',
            ('0', 'flat'),
            {'decimal_value': '0', 'type': 'flat'},
        ),
    ],
)
async def test_send_taxi_tips(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        mock_claims_full,
        mockserver,
        stq_runner,
        stq,
        create_cargo_c2c_orders,
        user_choice,
        phone_pd_id,
        times_called,
        selected_tips,
        pgsql,
        order_archive_mock,
        tips_sent,
):
    @mockserver.json_handler('/api-proxy/3.0/feedback')
    def mock_api_proxy_feedback(request):
        assert request.json == {
            'id': 'some_user_id',
            'orderid': 'some_taxi_order_id',
            'tips': tips_sent,
            'choices': {},
            'created_time': matching.AnyString(),
        }
        return {}

    order_archive_mock.set_order_proc(get_proc('some_taxi_order_id'))
    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': phone_pd_id,
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
        },
    )
    assert response.status_code == 200

    await stq_runner.cargo_c2c_send_taxi_feedback.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': phone_pd_id,
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            user_choice,
            None,
        ],
    )
    assert mock_api_proxy_feedback.times_called == times_called

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
    SELECT selected_tips, selected_tips_type
    FROM cargo_c2c.clients_feedbacks
        """,
    )
    assert list(cursor) == [selected_tips]
