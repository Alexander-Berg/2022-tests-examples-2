import pytest

# order_nr for previously existing feedback with rating = 4
EXISTING_ORDER_NR = '100'
CANCELLED_ORDER_NR = '101'
NEW_ORDER_NR = '1'

SAMPLE_REQUEST = {
    'type': 3,
    'contact_requested': False,
    'predefined_comment_ids': [1, 3],
}

SAMPLE_CORE_RESPONSE = {
    'order_nr': NEW_ORDER_NR,
    'eater_id': 'Alice',
    'place_id': '1',
    'type': {'order_type': 'native', 'delivery_type': 'our_delivery'},
}


@pytest.mark.parametrize(
    ['order_nr', 'param_json', 'core_json', 'app_name'],
    [
        [  # id=ios application
            NEW_ORDER_NR,
            {'type': 5, 'contact_requested': False, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            'eda_iphone',
        ],
        [  # id=android application
            NEW_ORDER_NR,
            {'type': 5, 'contact_requested': False, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            'eda_android',
        ],
    ],
    ids=['ios application', 'android application'],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=['predefined_comments.sql', 'feedback.sql', 'add_order.sql'],
)
@pytest.mark.config(
    EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': False},
    EATS_FEEDBACK_RATE_APP_CONFIGURATION={
        'enabled': True,
        'minimum_rating': 1,
        'maximum_rating': 5,
        'feedback_count_limit': 0,
    },
)
@pytest.mark.now('2021-02-12 00:00')
async def test_sent_feedback_suggest_rate_app_metric(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        taxi_eats_feedback_monitor,
        # ---- parameters ----
        order_nr,
        param_json,
        core_json,
        app_name,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core_feedback_context_(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_json, status=200)

    statistics_before = await taxi_eats_feedback_monitor.get_metric(
        'suggest-rate-app',
    )

    await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={
            'X-Eats-User': 'user_id=Alice',
            'X-Request-Application': (
                f'app_name={app_name},app_ver1=10,app_ver2=2,app_brand=yataxi'
            ),
            'X-Platform': 'Platform',
        },
        params={'order_nr': order_nr},
        json=param_json,
    )
    assert _mock_eda_core_feedback_context_.times_called == 1

    statistics_after = await taxi_eats_feedback_monitor.get_metric(
        'suggest-rate-app',
    )

    if app_name not in statistics_before:
        assert statistics_after[app_name] == 1
    else:
        assert statistics_after[app_name] - statistics_before[app_name] == 1


@pytest.mark.parametrize(
    ['order_nr', 'param_json', 'core_json', 'expected_metric_change_name'],
    [
        [  # id=rating is 1
            NEW_ORDER_NR,
            {'type': 1, 'contact_requested': False, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            'rate_1',
        ],
        [  # id=rating is 2
            NEW_ORDER_NR,
            {'type': 2, 'contact_requested': False, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            'rate_2',
        ],
        [  # id=rating is 3
            NEW_ORDER_NR,
            {'type': 3, 'contact_requested': False, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            'rate_3',
        ],
        [  # id=rating is 4
            NEW_ORDER_NR,
            {'type': 4, 'contact_requested': False, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            'rate_4',
        ],
        [  # id=rating is 5
            NEW_ORDER_NR,
            {'type': 5, 'contact_requested': False, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            'rate_5',
        ],
    ],
    ids=[
        'rating is 1',
        'rating is 2',
        'rating is 3',
        'rating is 4',
        'rating is 5',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=['predefined_comments.sql', 'feedback.sql', 'add_order.sql'],
)
@pytest.mark.now('2021-02-12 00:00')
@pytest.mark.config(EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': False})
async def test_sent_feedback_rating_metric(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        taxi_eats_feedback_monitor,
        # ---- parameters ----
        order_nr,
        param_json,
        core_json,
        expected_metric_change_name,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core_feedback_context_(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_json, status=200)

    statistics_before = await taxi_eats_feedback_monitor.get_metric(
        'sent-feedbacks-rating',
    )

    await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={'X-Eats-User': 'user_id=Alice', 'X-Platform': 'Platform'},
        params={'order_nr': order_nr},
        json=param_json,
    )
    assert _mock_eda_core_feedback_context_.times_called == 1

    statistics_after = await taxi_eats_feedback_monitor.get_metric(
        'sent-feedbacks-rating',
    )
    if expected_metric_change_name not in statistics_before:
        assert statistics_after[expected_metric_change_name] == 1
    else:
        assert (
            statistics_after[expected_metric_change_name]
            - statistics_before[expected_metric_change_name]
            == 1
        )


@pytest.mark.parametrize(
    ['order_nr', 'param_json', 'core_json', 'result_status'],
    [
        [  # id=send to chatterbox 200
            NEW_ORDER_NR,
            {
                'type': 3,
                'contact_requested': True,
                'predefined_comment_ids': [1, 3],
            },
            SAMPLE_CORE_RESPONSE,
            200,
        ],
        [  # id=send to chatterbox 400
            NEW_ORDER_NR,
            {'type': 3, 'contact_requested': True, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            400,
        ],
        [  # id=send to chatterbox 500
            NEW_ORDER_NR,
            {'type': 3, 'contact_requested': True, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            500,
        ],
    ],
    ids=[
        'send to chatterbox 200',
        'send to chatterbox 400',
        'send to chatterbox 500',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=['predefined_comments.sql', 'feedback.sql', 'add_order.sql'],
)
@pytest.mark.config(
    EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': True},
    EATS_FEEDBACK_CHATTERBOX_SETTINGS={
        'native_communication_method': 'chat',
        'superapp_communication_method': 'chat',
    },
)
@pytest.mark.now('2021-02-12 00:00')
async def test_post_feedback_send_to_chatterbox_metric(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        testpoint,
        taxi_eats_feedback_monitor,
        # ---- parameters ----
        order_nr,
        param_json,
        core_json,
        result_status,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core_feedback_context_(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_json, status=200)

    @mockserver.json_handler('/support-info/v1/eda/chat_tickets')
    def _mock_eda_chat_tickets_(request):
        return mockserver.make_response(status=result_status)

    @testpoint('send_to_chatterbox')
    def send_to_chatterbox(data):
        return data

    statistics_before = await taxi_eats_feedback_monitor.get_metric(
        'data-to-chatterbox',
    )

    await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={'X-Eats-User': 'user_id=Alice', 'X-Platform': 'ios_app'},
        params={'order_nr': order_nr},
        json=param_json,
    )
    assert _mock_eda_core_feedback_context_.times_called == 1

    await send_to_chatterbox.wait_call()
    assert _mock_eda_chat_tickets_.times_called == 1

    statistics_after = await taxi_eats_feedback_monitor.get_metric(
        'data-to-chatterbox',
    )
    if result_status == 200:
        assert (
            statistics_after['success-sending']
            - statistics_before['success-sending']
            == 1
        )
        assert (
            statistics_after['failed-sending']
            - statistics_before['failed-sending']
            == 0
        )
    else:
        assert (
            statistics_after['success-sending']
            - statistics_before['success-sending']
            == 0
        )
        assert (
            statistics_after['failed-sending']
            - statistics_before['failed-sending']
            == 1
        )
