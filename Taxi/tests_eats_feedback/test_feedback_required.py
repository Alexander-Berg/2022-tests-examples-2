# type: ignore[dict-item]

import json

import pytest

MOCK_NOW = '2020-07-24T12:59:59+00:00'
MOCK_NEXT_SECOND = '2020-07-24T13:00:00+00:00'

EMPTY_JSON = '{}'
EXPECTED_ORDER_NR = '210318-000000'
EXPECTED_JSON_RESPONSE = '{"order_nr": "210318-000000"}'


def remove_enabled_config3():
    return pytest.mark.experiments3(
        name='eats_orders_info_remove_feat_enabled',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-feedback/remove-feat-enabled'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict({'enabled': True}),
    )


@pytest.mark.parametrize(
    ['header', 'expected_response'],
    [
        [  # id=regular: regular request
            'user_id=Alice',
            (200, EXPECTED_JSON_RESPONSE),
        ],
        [  # id=partner: regular request for partner
            'partner_user_id=Alice',
            (200, EXPECTED_JSON_RESPONSE),
        ],
        ['', (401, None)],  # id=unauthorized
    ],
    ids=['regular', 'partner', 'unauthorized'],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.pgsql('eats_feedback', files=['orders.sql', 'feedbacks.sql'])
async def test_get_order_to_request_feedback(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
        # ---- parameters ----
        header,
        expected_response,
):
    expected_code, expected_body = expected_response

    response = await taxi_eats_feedback.get(
        '/eats-feedback/v1/feedback-required',
        headers={'X-Eats-User': header},
        params={},
    )

    assert response.status_code == expected_code
    if expected_body is not None:
        assert response.json() == json.loads(expected_body)


@pytest.mark.parametrize(
    ['orders_info_response', 'expected_response'],
    [
        [  # id=not_hidden
            (200, {'removed_order_nrs': []}),
            (200, EXPECTED_JSON_RESPONSE),
        ],
        [  # id=partly_hidden
            (200, {'removed_order_nrs': [EXPECTED_ORDER_NR]}),
            (200, '{"order_nr": "210318-000001"}'),
        ],
        [
            (200, {'removed_order_nrs': ['210318-000000', '210318-000001']}),
            (200, EMPTY_JSON),
        ],  # id=all_hidden
        [(500, None), (500, None)],  # id=orders_info_error
    ],
    ids=['not_hidden', 'partly_hidden', 'all_hidden', 'orders_info_error'],
)
@pytest.mark.now('2020-07-24T11:59:59+00:00')
@pytest.mark.pgsql('eats_feedback', files=['orders.sql', 'feedbacks.sql'])
@pytest.mark.config(
    EATS_FEEDBACK_CHECK_HIDDEN_ORDERS={'enabled': True, 'orders_limit': 10},
)
async def test_hidden_orders(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
        mockserver,
        # ---- parameters ----
        orders_info_response,
        expected_response,
):
    orders_info_code, orders_info_body = orders_info_response
    expected_code, expected_body = expected_response

    @mockserver.json_handler(
        '/eats-orders-info/internal/orders-info/v1/check-orders-removed',
    )
    def mock_orders_hidden(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=orders_info_code, json=orders_info_body,
        )

    response = await taxi_eats_feedback.get(
        '/eats-feedback/v1/feedback-required',
        headers={'X-Eats-User': 'user_id=Alice'},
        params={},
    )

    assert mock_orders_hidden.times_called == 1
    assert response.status_code == expected_code
    if expected_body is not None:
        assert response.json() == json.loads(expected_body)


@pytest.mark.parametrize(
    ['header', 'expected_response'],
    [
        ['user_id=Alice', (200, EMPTY_JSON)],  # id=regular: regular request
        [  # id=partner: regular request for partner
            'partner_user_id=Alice',
            (200, EMPTY_JSON),
        ],
        ['', (401, None)],  # id=unauthorized
    ],
    ids=['regular', 'partner', 'unauthorized'],
)
@pytest.mark.now(MOCK_NEXT_SECOND)
@pytest.mark.pgsql('eats_feedback', files=['orders.sql', 'feedbacks.sql'])
async def test_get_order_to_request_feedback_next_day(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
        # ---- parameters ----
        header,
        expected_response,
):
    expected_code, expected_body = expected_response

    response = await taxi_eats_feedback.get(
        '/eats-feedback/v1/feedback-required',
        headers={'X-Eats-User': header},
        params={},
    )

    assert response.status_code == expected_code
    if expected_body is not None:
        assert response.json() == json.loads(expected_body)
