# type: ignore[dict-item]

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

ADDED = 'added'
NOT_ADDED = 'not_added'

PLATFORMS = {
    'native': ['ios_app', 'android_app', 'mobile_web', 'desktop_web'],
    'superapp': [
        'superapp_taxi_web',
        'magnit_app_web',
        'superapp_bro_web',
        'superapp_pp_web',
        'superapp_eats_web',
        'superapp_zapravki_web',
    ],
}

RATE_APP_CONFIGURATION = {
    'feedback_count_limit': 2,
    'minimum_rating': 5,
    'maximum_rating': 5,
    'enabled': True,
}


@pytest.mark.parametrize(
    [
        'order_nr',
        'param_json',
        'core_json',
        'result_json',
        'result_status',
        'added',
    ],
    [
        [  # id=without_comment
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            SAMPLE_CORE_RESPONSE,
            'feedback_added_default.json',
            200,
            ADDED,
        ],
        [  # id=int_contact_requested
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            {**SAMPLE_CORE_RESPONSE, 'contact_requested': 0},
            'feedback_added_default.json',
            200,
            ADDED,
        ],
        [  # id=canceled_without_comment
            CANCELLED_ORDER_NR,
            SAMPLE_REQUEST,
            {**SAMPLE_CORE_RESPONSE, 'order_nr': CANCELLED_ORDER_NR},
            'feedback_rewrite_cancelled.json',
            200,
            ADDED,
        ],
        [  # id=prefix_without_comment
            NEW_ORDER_NR,
            {**SAMPLE_REQUEST, 'comment': 'lbd:'},
            SAMPLE_CORE_RESPONSE,
            'feedback_added_default.json',
            200,
            ADDED,
        ],
        [  # id=android_format
            NEW_ORDER_NR,
            {**SAMPLE_REQUEST, 'feedback_status': 'noshow'},
            SAMPLE_CORE_RESPONSE,
            'feedback_added_default.json',
            200,
            ADDED,
        ],
        [  # id=retail
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            {
                **SAMPLE_CORE_RESPONSE,
                'type': {
                    'order_type': 'retail',
                    'delivery_type': 'our_delivery',
                },
            },
            'feedback_added_default.json',
            200,
            ADDED,
        ],
        [  # id=order_nr_idempotent
            EXISTING_ORDER_NR,  # existing order_nr
            SAMPLE_REQUEST,
            {**SAMPLE_CORE_RESPONSE, 'order_nr': EXISTING_ORDER_NR},
            'feedback_no_changes.json',
            200,
            NOT_ADDED,
        ],
        [  # id=with_comment
            NEW_ORDER_NR,
            {
                'type': 5,
                'contact_requested': False,
                'predefined_comment_ids': [5],
                'comment': 'Thank you!',
            },
            SAMPLE_CORE_RESPONSE,
            'feedback_added_comment.json',
            200,
            ADDED,
        ],
        [  # id=with_max_length_comment
            NEW_ORDER_NR,
            {
                'type': 5,
                'contact_requested': False,
                'predefined_comment_ids': [5],
                'comment': (
                    '11111111111111111111111111111111111111111111111111'
                    '22222222222222222222222222222222222222222222222222'
                    '33333333333333333333333333333333333333333333333333'
                    '44444444444444444444444444444444444444444444444444'
                    '55555555555555555555555555555555555555555555555555'
                    '66666666666666666666666666666666666666666666666666'
                ),
            },
            SAMPLE_CORE_RESPONSE,
            'feedback_added_comment.json',
            200,
            ADDED,
        ],
        [  # id=damaged
            NEW_ORDER_NR,
            {
                'type': 2,
                'contact_requested': False,
                'predefined_comment_ids': [5],
            },
            SAMPLE_CORE_RESPONSE,
            'feedback_no_changes.json',
            200,
            ADDED,
        ],
        [  # id=damaged_marketplace
            NEW_ORDER_NR,
            {
                'type': 2,
                'contact_requested': False,
                'predefined_comment_ids': [5],
            },
            {
                **SAMPLE_CORE_RESPONSE,
                'type': {
                    'order_type': 'native',
                    'delivery_type': 'marketplace',
                },
            },
            'feedback_5.json',
            200,
            ADDED,
        ],
        [  # id=food_and_damaged
            NEW_ORDER_NR,
            {
                'type': 2,
                'contact_requested': False,
                'predefined_comment_ids': [1, 5],
            },
            SAMPLE_CORE_RESPONSE,
            'feedback_3.json',
            200,
            ADDED,
        ],
        [  # id=wrong
            NEW_ORDER_NR,
            {
                'type': 1,
                'contact_requested': False,
                'predefined_comment_ids': [3],
            },
            SAMPLE_CORE_RESPONSE,
            'feedback_4.json',
            200,
            ADDED,
        ],
        [  # id=wrong_retail
            NEW_ORDER_NR,
            {
                'type': 1,
                'contact_requested': False,
                'predefined_comment_ids': [3],
            },
            {
                **SAMPLE_CORE_RESPONSE,
                'type': {
                    'order_type': 'retail',
                    'delivery_type': 'our_delivery',
                },
            },
            'feedback_no_changes.json',
            200,
            ADDED,
        ],
        [  # id=no_predefined_comments
            NEW_ORDER_NR,
            {**SAMPLE_REQUEST, 'predefined_comment_ids': []},
            SAMPLE_CORE_RESPONSE,
            'feedback_6.json',
            200,
            ADDED,
        ],
        [  # id=bad_predefined_comment
            NEW_ORDER_NR,
            {
                'type': 3,
                'contact_requested': False,
                'predefined_comment_ids': [1, 2, 3],
            },
            SAMPLE_CORE_RESPONSE,
            'feedback_no_changes.json',
            400,
            NOT_ADDED,
        ],
        [  # id=nonexistent, trying to add feedback to nonexistent order
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            (404, {'message': 'Not found', 'status': 'error'}),
            'feedback_no_changes.json',
            404,
            NOT_ADDED,
        ],
        [  # id=anothers, trying to add feedback to other user's order
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            {**SAMPLE_CORE_RESPONSE, 'eater_id': 'Bob'},
            'feedback_no_changes.json',
            404,
            NOT_ADDED,
        ],
        [  # id=with_too_long_comment
            NEW_ORDER_NR,
            {
                'type': 5,
                'contact_requested': False,
                'predefined_comment_ids': [5],
                'comment': (
                    '11111111111111111111111111111111111111111111111111'
                    '22222222222222222222222222222222222222222222222222'
                    '33333333333333333333333333333333333333333333333333'
                    '44444444444444444444444444444444444444444444444444'
                    '55555555555555555555555555555555555555555555555555'
                    '66666666666666666666666666666666666666666666666666'
                    '7'
                ),  # length = 301
            },
            SAMPLE_CORE_RESPONSE,
            'feedback_no_changes.json',
            400,
            NOT_ADDED,
        ],
        [  # id=core_error, core returned incorrect order_nr
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            {**SAMPLE_CORE_RESPONSE, 'order_nr': NEW_ORDER_NR + '_'},
            'feedback_no_changes.json',
            500,
            NOT_ADDED,
        ],
    ],
    ids=[
        'without_comment',
        'int_contact_requested',
        'canceled_without_comment',
        'prefix_without_comment',
        'android_format',
        'retail',
        'order_nr_idempotent',
        'with_comment',
        'with_max_length_comment',
        'damaged',
        'damaged_marketplace',
        'food_and_damaged',
        'wrong',
        'wrong_retail',
        'no_predefined_comments',
        'bad_predefined_comment',
        'nonexistent',
        'anothers',
        'with_too_long_comment',
        'core_error',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedback.sql',
        'order.sql',
        'add_order.sql',
    ],
)
@pytest.mark.config(EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': False})
@pytest.mark.now('2021-02-12 00:00')
async def test_sent_feedback(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
        mockserver,
        stq,
        # ---- parameters ----
        order_nr,
        param_json,
        core_json,
        result_json,
        result_status,
        added,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core_feedback_context_(request):
        assert request.query.get('order_nr') == order_nr
        if isinstance(core_json, tuple):
            code, payload = core_json
            return mockserver.make_response(json=payload, status=code)
        return mockserver.make_response(json=core_json, status=200)

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={'X-Eats-User': 'user_id=Alice', 'X-Platform': 'Platform'},
        params={'order_nr': order_nr},
        json=param_json,
    )
    assert response.status_code == result_status
    if response.status_code != 400:
        assert _mock_eda_core_feedback_context_.times_called == 1

    if added == ADDED:
        assert stq.eats_ordershistory_add_feedback.times_called == 1
        call = stq.eats_ordershistory_add_feedback.next_call()
        del call['eta']
        del call['kwargs']
        assert call == {
            'queue': 'eats_ordershistory_add_feedback',
            'id': order_nr,
            'args': [
                {
                    'rating': param_json['type'],
                    'comment': (
                        param_json['comment']
                        if 'comment' in param_json
                        else ''
                    ),
                },
            ],
        }

    if added == NOT_ADDED:
        assert stq.eats_ordershistory_add_feedback.times_called == 0

    response = await taxi_eats_feedback.get(
        '/internal/eats-feedback/v1/feedbacks',
        params={'place_id': 1, 'user_locale': 'ru'},
    )
    assert response.status_code == 200
    expected_json = load_json(result_json)

    response_json = response.json()
    response_json['feedbacks'].sort(key=lambda x: x['id'])
    assert len(response_json['feedbacks']) == len(expected_json['feedbacks'])
    for pair in zip(response_json['feedbacks'], expected_json['feedbacks']):
        if 'feedback_filled_at' in pair[0]:
            pair[1]['feedback_filled_at'] = pair[0]['feedback_filled_at']
    assert response_json == expected_json


@pytest.mark.parametrize(
    [
        'order_nr',
        'param_json',
        'core_json',
        'result_status',
        'header',
        'expected_mock_times_called',
    ],
    [
        [  # id=user_id only
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            SAMPLE_CORE_RESPONSE,
            200,
            'user_id=Alice',
            1,
        ],
        [  # id=partner_user_id only
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            SAMPLE_CORE_RESPONSE,
            200,
            'partner_user_id=Alice',
            1,
        ],
        [  # id=empty header
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            SAMPLE_CORE_RESPONSE,
            401,
            '',
            0,
        ],
        [  # id=both user_id and partner_user_id
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            SAMPLE_CORE_RESPONSE,
            200,
            'user_id=Bob,partner_user_id=Alice',
            1,
        ],
        [  # id=wrong both user_id and partner_user_id
            NEW_ORDER_NR,
            SAMPLE_REQUEST,
            SAMPLE_CORE_RESPONSE,
            404,
            'user_id=Alice,partner_user_id=Bob',
            1,
        ],
    ],
    ids=[
        'user_id only',
        'partner_user_id only',
        'empty header',
        'both user_id and partner_user_id',
        'wrong both user_id and partner_user_id',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedback.sql',
        'order.sql',
        'add_order.sql',
    ],
)
@pytest.mark.config(EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': False})
@pytest.mark.now('2021-02-12 00:00')
async def test_sent_feedback_all_eats_headers(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        # ---- parameters ----
        order_nr,
        param_json,
        core_json,
        result_status,
        header,
        expected_mock_times_called,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core_feedback_context_(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_json, status=200)

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={'X-Eats-User': header, 'X-Platform': 'Platform'},
        params={'order_nr': order_nr},
        json=param_json,
    )

    assert response.status_code == result_status
    assert (
        _mock_eda_core_feedback_context_.times_called
        == expected_mock_times_called
    )


@pytest.mark.parametrize(
    ['order_nr', 'param_json', 'core_json', 'result_status'],
    [
        [  # id=without_predefined_comment_ids
            NEW_ORDER_NR,
            {'type': 3, 'contact_requested': False},
            SAMPLE_CORE_RESPONSE,
            200,
        ],
        [NEW_ORDER_NR, {'type': 3}, SAMPLE_CORE_RESPONSE, 200],  # id=only_type
        [  # id=type_true
            NEW_ORDER_NR,
            {'type': True, 'contact_requested': False},
            SAMPLE_CORE_RESPONSE,
            200,
        ],
        [  # id=type_false
            NEW_ORDER_NR,
            {'type': False, 'contact_requested': False},
            SAMPLE_CORE_RESPONSE,
            400,
        ],
    ],
    ids=[
        'without_predefined_comment_ids',
        'only_type',
        'type_true',
        'type_false',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedback.sql',
        'order.sql',
        'add_order.sql',
    ],
)
@pytest.mark.config(EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': False})
@pytest.mark.now('2021-02-12 00:00')
async def test_sent_feedback_with_variant_params(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
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

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={'X-Eats-User': 'user_id=Alice', 'X-Platform': 'Platform'},
        params={'order_nr': order_nr},
        json=param_json,
    )
    assert response.status_code == result_status
    assert _mock_eda_core_feedback_context_.times_called == 1


@pytest.mark.parametrize(
    [
        'order_nr',
        'param_json',
        'core_json',
        'async_times_called',
        'support_info_times_called',
        'core_times_called',
        'platform',
        'expected_app_type',
    ],
    [
        [  # id=without comments and predefined comments
            NEW_ORDER_NR,
            {'type': 3, 'contact_requested': True},
            SAMPLE_CORE_RESPONSE,
            0,
            0,
            0,
            'ios_app',
            None,
        ],
        [  # id=with comment native
            NEW_ORDER_NR,
            {'type': 3, 'contact_requested': True, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            1,
            1,
            0,
            'ios_app',
            'native',
        ],
        [  # id=with comment superapp
            NEW_ORDER_NR,
            {'type': 3, 'contact_requested': True, 'comment': 'Nice food'},
            SAMPLE_CORE_RESPONSE,
            1,
            0,
            1,
            'superapp_taxi_web',
            'superapp',
        ],
        [  # id=with predefined comments native
            NEW_ORDER_NR,
            {
                'type': 3,
                'contact_requested': True,
                'predefined_comment_ids': [1, 3],
            },
            SAMPLE_CORE_RESPONSE,
            1,
            1,
            0,
            'ios_app',
            'native',
        ],
        [  # id=with predefined comments superapp
            NEW_ORDER_NR,
            {
                'type': 3,
                'contact_requested': True,
                'predefined_comment_ids': [1, 3],
            },
            SAMPLE_CORE_RESPONSE,
            1,
            0,
            1,
            'superapp_taxi_web',
            'superapp',
        ],
        [  # id=no platform
            NEW_ORDER_NR,
            {
                'type': 3,
                'contact_requested': True,
                'predefined_comment_ids': [1, 3],
            },
            SAMPLE_CORE_RESPONSE,
            1,
            0,
            1,
            None,
            None,
        ],
    ],
    ids=[
        'without comments and predefined comments',
        'with comment native',
        'with comment superapp',
        'with predefined comments native',
        'with predefined comments superapp',
        'no platform',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedback.sql',
        'order.sql',
        'add_order.sql',
    ],
)
@pytest.mark.config(
    EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': True},
    EATS_FEEDBACK_PLATFORMS=PLATFORMS,
    EATS_FEEDBACK_CHATTERBOX_SETTINGS={
        'native_communication_method': 'chat',
        'superapp_communication_method': 'mail',
    },
)
@pytest.mark.now('2021-02-12 00:00')
async def test_sent_feedback_with_different_input_params_to_chatterbox(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        testpoint,
        # ---- parameters ----
        order_nr,
        param_json,
        core_json,
        async_times_called,
        support_info_times_called,
        core_times_called,
        platform,
        expected_app_type,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core_feedback_context_(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_json, status=200)

    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/feedback/send-to-chatterbox',
    )
    def _mock_eda_core_mail_tickets_(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/support-info/v1/eda/chat_tickets')
    def _mock_eda_chat_tickets_(request):
        assert request.json['app'] == expected_app_type
        return mockserver.make_response(status=200)

    @testpoint('send_to_chatterbox')
    def send_to_chatterbox(data):
        return data

    await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={'X-Eats-User': 'user_id=Alice', 'X-Platform': platform},
        params={'order_nr': order_nr},
        json=param_json,
    )

    assert _mock_eda_core_feedback_context_.times_called == 1

    if async_times_called != 0:
        await send_to_chatterbox.wait_call()
    assert _mock_eda_chat_tickets_.times_called == support_info_times_called
    assert _mock_eda_core_mail_tickets_.times_called == core_times_called


@pytest.mark.parametrize(
    [
        'eater_id',
        'param_json',
        'core_json',
        'app_name',
        'expected_result_status',
        'expected_show_rate_app',
    ],
    [
        [  # id=showed_rate_app
            'Alice',
            {'type': 5},
            SAMPLE_CORE_RESPONSE,
            'eda_iphone',
            200,
            False,
        ],
        [  # id=need_show_rate_app_with_another_platform
            'Alice',
            {'type': 5},
            SAMPLE_CORE_RESPONSE,
            'eda_android',
            200,
            True,
        ],
        [  # id=not_enough_to_show_rate_app
            'Jojo',
            {'type': 5},
            {
                'order_nr': NEW_ORDER_NR,
                'eater_id': 'Jojo',
                'place_id': '1',
                'type': {
                    'order_type': 'native',
                    'delivery_type': 'our_delivery',
                },
            },
            'eda_iphone',
            200,
            False,
        ],
        [  # id=small_rate
            'Alice',
            {'type': 3},
            SAMPLE_CORE_RESPONSE,
            'eda_iphone',
            200,
            False,
        ],
        [  # id=need_show_rate_app
            'Batman',
            {'type': 5},
            {
                'order_nr': NEW_ORDER_NR,
                'eater_id': 'Batman',
                'place_id': '1',
                'type': {
                    'order_type': 'native',
                    'delivery_type': 'our_delivery',
                },
            },
            'eda_iphone',
            200,
            True,
        ],
        [  # id=not_need_for_not_mobile_app
            'Batman',
            {'type': 5},
            {
                'order_nr': NEW_ORDER_NR,
                'eater_id': 'Batman',
                'place_id': '1',
                'type': {
                    'order_type': 'native',
                    'delivery_type': 'our_delivery',
                },
            },
            'web',
            200,
            False,
        ],
    ],
    ids=[
        'showed_rate_app',
        'not_enough_to_show_rate_app',
        'small_rate',
        'need_show_rate_app',
        'need_show_rate_app_with_another_platform',
        'not_need_for_not_mobile_app',
    ],
)
@pytest.mark.pgsql(
    'eats_feedback',
    files=[
        'predefined_comments.sql',
        'feedback.sql',
        'showed_rate_app_suggestions.sql',
        'add_feedbacks.sql',
        'add_eater_feedback_stats.sql',
        'order.sql',
        'add_order.sql',
    ],
)
@pytest.mark.config(
    EATS_FEEDBACK_RATE_APP_CONFIGURATION=RATE_APP_CONFIGURATION,
)
@pytest.mark.now('2021-02-12 00:00')
async def test_sent_feedback_show_rate_app(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        # ---- parameters ----
        eater_id,
        param_json,
        core_json,
        app_name,
        expected_result_status,
        expected_show_rate_app,
):
    order_nr = NEW_ORDER_NR

    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core_feedback_context_(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_json, status=200)

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={
            'X-Eats-User': ('user_id=' + eater_id),
            'X-Request-Application': (
                f'app_name={app_name},app_ver1=10,app_ver2=2,app_brand=yataxi'
            ),
            'X-Platform': 'Platform',
        },
        params={'order_nr': order_nr},
        json=param_json,
    )
    assert response.status_code == expected_result_status
    if response.status_code == 200:
        assert response.json()['show_rate_app'] == expected_show_rate_app
    assert _mock_eda_core_feedback_context_.times_called == 1
