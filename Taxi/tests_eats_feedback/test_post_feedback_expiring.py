import pytest

from tests_eats_feedback import utils


@pytest.mark.parametrize(
    ['order_nr', 'expected_code', 'expected_body'],
    [
        pytest.param(
            '102',
            400,
            {
                'code': 'cancel_feedback_failed',
                'message': 'Can\'t cancel feedback',
            },
            id='expired',
        ),
        pytest.param('103', 204, None, id='success'),
    ],
)
@pytest.mark.pgsql('eats_feedback', files=['database.sql'])
@pytest.mark.config(
    EATS_FEEDBACK_TIME_LIMIT_CONFIGURATION={
        'post_expiration_period_min': 4320,
        'request_expiration_period_min': 1440,
    },
)
@pytest.mark.now('2021-02-14 00:00')
async def test_cancel_expiring(
        taxi_eats_feedback,
        mockserver,
        pgsql,
        taxi_eats_feedback_monitor,
        order_nr,
        expected_code,
        expected_body,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(
            json={
                'order_nr': order_nr,
                'eater_id': '111',
                'place_id': '2',
                'type': {
                    'order_type': 'native',
                    'delivery_type': 'our_delivery',
                },
            },
            status=200,
        )

    assert utils.load_feedbacks_table(pgsql) == []

    statistics_before = await taxi_eats_feedback_monitor.get_metric(
        'cancel-feedback',
    )

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/cancel',
        headers={'X-Eats-User': 'user_id=111'},
        params={'order_nr': order_nr},
    )

    statistics_after = await taxi_eats_feedback_monitor.get_metric(
        'cancel-feedback',
    )

    assert response.status_code == expected_code
    if expected_code == 400:
        assert response.json() == expected_body
    else:
        assert (
            statistics_after['cancelled-feedback']
            - statistics_before['cancelled-feedback']
            == 1
        )
        assert utils.load_feedbacks_table(pgsql) == [
            [1, 3, None, order_nr, 'our_delivery'],
        ]


@pytest.mark.parametrize(
    ['order_nr', 'expected_code', 'expected_body'],
    [
        pytest.param(
            '102',
            400,
            {
                'code': 'feedback_post_failed',
                'message': 'Can\'t post feedback',
            },
            id='expired',
        ),
        pytest.param('103', 200, None, id='success'),
    ],
)
@pytest.mark.pgsql('eats_feedback', files=['database.sql'])
@pytest.mark.config(
    EATS_FEEDBACK_TIME_LIMIT_CONFIGURATION={
        'post_expiration_period_min': 4320,
        'request_expiration_period_min': 1440,
    },
)
@pytest.mark.now('2021-02-14 00:00')
@pytest.mark.config(EATS_FEEDBACK_SEND_TO_CHATTERBOX={'enabled': False})
async def test_feedback_expiring(
        taxi_eats_feedback,
        mockserver,
        pgsql,
        order_nr,
        expected_code,
        expected_body,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(
            json={
                'order_nr': order_nr,
                'eater_id': '111',
                'place_id': '2',
                'type': {
                    'order_type': 'native',
                    'delivery_type': 'our_delivery',
                },
            },
            status=200,
        )

    assert utils.load_feedbacks_table(pgsql) == []

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/feedback',
        headers={'X-Eats-User': 'user_id=111'},
        params={'order_nr': order_nr},
        json={
            'type': 5,
            'contact_requested': False,
            'predefined_comment_ids': [1, 3],
        },
    )

    assert response.status_code == expected_code
    if expected_code == 400:
        assert response.json() == expected_body
    else:
        assert utils.load_feedbacks_table(pgsql) == [
            [1, 5, None, order_nr, 'our_delivery'],
        ]


@pytest.mark.parametrize(
    ['eater_id', 'expected_order_nr'],
    [['112', None], ['111', '104']],  # id=all_expired  # id=have_no_expired
    ids=['all_expired', 'have_no_expired'],
)
@pytest.mark.now('2021-02-14 00:00')
@pytest.mark.pgsql('eats_feedback', files=['database.sql'])
# less than request_expiration_period_min
@pytest.mark.config(
    EATS_FEEDBACK_TIME_LIMIT_CONFIGURATION={
        'post_expiration_period_min': 720,
        'request_expiration_period_min': 1440,
    },
)
async def test_expired_feedbacks_required(
        # ---- fixtures ----
        taxi_eats_feedback,
        # ---- parameters ----
        eater_id,
        expected_order_nr,
):
    response = await taxi_eats_feedback.get(
        '/eats-feedback/v1/feedback-required',
        headers={'X-Eats-User': 'user_id=' + eater_id},
        params={},
    )

    assert response.status_code == 200
    if expected_order_nr:
        assert response.json() == {'order_nr': expected_order_nr}


@pytest.mark.config(
    EATS_FEEDBACK_PG_SELECT_FEEDBACK_LIMIT={'limit': 3},
    EATS_FEEDBACK_TIME_LIMIT_CONFIGURATION={
        'post_expiration_period_min': 4320,
        'request_expiration_period_min': 1440,
    },
)
@pytest.mark.pgsql(
    'eats_feedback', files=['database.sql', 'add_feedbacks.sql'],
)
@pytest.mark.now('2021-02-14 00:00')
async def test_get_feedbacks_for_orders_history(
        # ---- fixtures ----
        load_json,
        taxi_eats_feedback,
):
    response = await taxi_eats_feedback.post(
        '/internal/eats-feedback/v1/get-feedbacks-for-orders-history',
        json={'order_nrs': ['102', '103', '106', '107']},
    )

    assert response.status_code == 200
    # for 102 order not exist feedback, but not ask it
    # for 106 feedback exist, but used wait
    assert response.json() == {
        'feedbacks': [
            {
                'has_feedback': False,
                'order_nr': '102',
                'status': 'wait',
                'is_feedback_needed': False,
            },
            {
                'has_feedback': False,
                'order_nr': '103',
                'status': 'show',
                'is_feedback_needed': True,
            },
            {
                'has_feedback': True,
                'order_nr': '106',
                'status': 'wait',
                'is_feedback_needed': False,
            },
            {
                'has_feedback': True,
                'order_nr': '107',
                'status': 'noshow',
                'is_feedback_needed': False,
            },
        ],
    }
