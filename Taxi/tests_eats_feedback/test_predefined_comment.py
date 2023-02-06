# type: ignore[dict-item]

import pytest

SAMPLE_ORDER_NR = '210412-0000001'

SAMPLE_CORE_RESPONSE = {
    'order_nr': SAMPLE_ORDER_NR,
    'eater_id': 'Alice',
    'place_id': '2',
    'type': {'order_type': 'native', 'delivery_type': 'our_delivery'},
}


@pytest.mark.parametrize(
    ['order_nr', 'core_response', 'expected_response'],
    [
        [  # id=regular: regular request
            SAMPLE_ORDER_NR,
            (200, SAMPLE_CORE_RESPONSE),
            (200, 'predefined_comments.json'),
        ],
        [  # id=nonexistent: request for nonexistent order
            SAMPLE_ORDER_NR,
            (404, {'status': 'error', 'message': 'Not found'}),
            (404, None),
        ],
        [  # id=anothers: request for another user's order
            SAMPLE_ORDER_NR,
            (200, {**SAMPLE_CORE_RESPONSE, 'eater_id': 'Bob'}),
            (404, None),
        ],
        [  # id=core_error: invalid core answer
            SAMPLE_ORDER_NR,
            (200, {**SAMPLE_CORE_RESPONSE, 'order_nr': SAMPLE_ORDER_NR + '_'}),
            (500, None),
        ],
    ],
    ids=['regular', 'nonexistent', 'anothers', 'core_error'],
)
@pytest.mark.pgsql('eats_feedback', files=['predefined_comments.sql'])
async def test_get_predefined_comments(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
        mockserver,
        # ---- parameters ----
        order_nr,
        core_response,
        expected_response,
):
    core_code, core_body = core_response
    expected_code, expected_body = expected_response

    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_body, status=core_code)

    response = await taxi_eats_feedback.get(
        '/eats-feedback/v1/predefined-comment',
        headers={'X-Eats-User': 'user_id=Alice'},
        params={'order_nr': order_nr},
    )

    assert response.status_code == expected_code
    if expected_body is not None:
        assert response.json() == load_json(expected_body)

    assert _mock_eda_core.times_called == 1


@pytest.mark.parametrize(
    ['locale', 'expected_body'],
    [
        ['en', 'english_predefined_comments.json'],
        ['ch', 'predefined_comments.json'],
    ],
    ids=['exist_translation', 'nonexistent_translation'],
)
@pytest.mark.pgsql('eats_feedback', files=['predefined_comments.sql'])
async def test_get_predefined_comments_with_locale(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
        mockserver,
        # ---- parameters ----
        locale,
        expected_body,
):
    core_code, core_body = (200, SAMPLE_CORE_RESPONSE)
    expected_code = 200

    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == SAMPLE_ORDER_NR
        return mockserver.make_response(json=core_body, status=core_code)

    response = await taxi_eats_feedback.get(
        '/eats-feedback/v1/predefined-comment',
        headers={'X-Eats-User': 'user_id=Alice', 'X-Request-Language': locale},
        params={'order_nr': SAMPLE_ORDER_NR},
    )

    assert response.status_code == expected_code
    if expected_body is not None:
        assert response.json() == load_json(expected_body)

    assert _mock_eda_core.times_called == 1


@pytest.mark.parametrize(
    [
        'order_nr',
        'core_response',
        'expected_response',
        'header',
        'expected_mock_times_called',
    ],
    [
        [  # id = user_id only
            SAMPLE_ORDER_NR,
            (200, SAMPLE_CORE_RESPONSE),
            200,
            'user_id=Alice',
            1,
        ],
        [  # id = partner_user_id only
            SAMPLE_ORDER_NR,
            (200, SAMPLE_CORE_RESPONSE),
            200,
            'partner_user_id=Alice',
            1,
        ],
        [  # id = empty header
            SAMPLE_ORDER_NR,
            (200, SAMPLE_CORE_RESPONSE),
            401,
            '',
            0,
        ],
        [  # id = both user_id and partner_user_id
            SAMPLE_ORDER_NR,
            (200, SAMPLE_CORE_RESPONSE),
            200,
            'user_id=Bob,partner_user_id=Alice',
            1,
        ],
        [  # id = both user_id and partner_user_id
            SAMPLE_ORDER_NR,
            (200, SAMPLE_CORE_RESPONSE),
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
@pytest.mark.pgsql('eats_feedback', files=['predefined_comments.sql'])
async def test_get_predefined_comments_all_eats_headers(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        # ---- parameters ----
        order_nr,
        core_response,
        expected_response,
        header,
        expected_mock_times_called,
):
    core_code, core_body = core_response
    expected_code = expected_response

    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(json=core_body, status=core_code)

    response = await taxi_eats_feedback.get(
        '/eats-feedback/v1/predefined-comment',
        headers={'X-Eats-User': header},
        params={'order_nr': order_nr},
    )

    assert response.status_code == expected_code
    assert _mock_eda_core.times_called == expected_mock_times_called
