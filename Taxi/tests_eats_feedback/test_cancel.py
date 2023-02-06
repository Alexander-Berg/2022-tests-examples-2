# type: ignore[dict-item]

import pytest

from tests_eats_feedback import utils

SAMPLE_ORDER_NR = '210318-483588'

SAMPLE_CORE_RESPONSE = {
    'order_nr': SAMPLE_ORDER_NR,
    'eater_id': 'Alice',
    'place_id': '2',
    'type': {'order_type': 'native', 'delivery_type': 'our_delivery'},
}


@pytest.mark.pgsql('eats_feedback', files=['order.sql'])
@pytest.mark.now('2021-02-11 00:00')
async def test_cancel_success(
        taxi_eats_feedback, mockserver, pgsql, taxi_eats_feedback_monitor,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == SAMPLE_ORDER_NR
        return mockserver.make_response(json=SAMPLE_CORE_RESPONSE, status=200)

    assert utils.load_feedbacks_table(pgsql) == []

    statistics_before = await taxi_eats_feedback_monitor.get_metric(
        'cancel-feedback',
    )

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/cancel',
        headers={'X-Eats-User': 'user_id=Alice'},
        params={'order_nr': SAMPLE_ORDER_NR},
    )

    statistics_after = await taxi_eats_feedback_monitor.get_metric(
        'cancel-feedback',
    )

    assert response.status_code == 204
    assert _mock_eda_core.times_called == 1
    assert (
        statistics_after['cancelled-feedback']
        - statistics_before['cancelled-feedback']
        == 1
    )

    assert utils.load_feedbacks_table(pgsql) == [
        [1, 3, None, SAMPLE_ORDER_NR, 'our_delivery'],
    ]


@pytest.mark.parametrize(
    ['header', 'result_status', 'expected_mock_times_called'],
    [
        ['user_id=Alice', 204, 1],  # id = user_id only
        ['partner_user_id=Alice', 204, 1],  # id = partner_user_id only
        ['', 401, 0],  # id = empty header
        [  # id = both user_id and partner_user_id
            'user_id=Bob,partner_user_id=Alice',
            204,
            1,
        ],
        [  # id = wrong both user_id and partner_user_id
            'user_id=Alice,partner_user_id=Bob',
            404,
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
@pytest.mark.pgsql('eats_feedback', files=['order.sql'])
@pytest.mark.now('2021-02-11 00:00')
async def test_cancel_success_all_eats_headers(
        # ---- fixtures ----
        taxi_eats_feedback,
        mockserver,
        # ---- parameters ----
        header,
        result_status,
        expected_mock_times_called,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == SAMPLE_ORDER_NR
        return mockserver.make_response(json=SAMPLE_CORE_RESPONSE, status=200)

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/cancel',
        headers={'X-Eats-User': header},
        params={'order_nr': SAMPLE_ORDER_NR},
    )

    assert response.status_code == result_status
    assert _mock_eda_core.times_called == expected_mock_times_called


@pytest.mark.parametrize(
    ['order_nr', 'expected_status_code'], [['100', 204], ['101', 204]],
)
@pytest.mark.pgsql('eats_feedback', files=['feedback.sql', 'order.sql'])
@pytest.mark.now('2021-02-11 00:00')
async def test_cancel_existing(
        taxi_eats_feedback, mockserver, pgsql, order_nr, expected_status_code,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == order_nr
        return mockserver.make_response(
            json={**SAMPLE_CORE_RESPONSE, 'order_nr': order_nr}, status=200,
        )

    rows = [
        [100, 5, 'Previously filled feedback', '100', None],
        [101, 3, None, '101', None],
    ]

    assert utils.load_feedbacks_table(pgsql) == rows

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/cancel',
        headers={'X-Eats-User': 'user_id=Alice'},
        params={'order_nr': order_nr},
    )
    assert response.status_code == expected_status_code
    assert _mock_eda_core.times_called == 1
    assert utils.load_feedbacks_table(pgsql) == rows


@pytest.mark.parametrize(
    ['core_code', 'core_json'],
    [
        [404, {'status': 'error', 'message': 'Not found'}],
        [200, {**SAMPLE_CORE_RESPONSE, 'eater_id': 'Bob'}],
    ],
)
@pytest.mark.pgsql('eats_feedback', files=['order.sql'])
@pytest.mark.now('2021-02-11 00:00')
async def test_bad_context(
        taxi_eats_feedback, mockserver, pgsql, core_code, core_json,
):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert request.query.get('order_nr') == SAMPLE_ORDER_NR
        return mockserver.make_response(json=core_json, status=core_code)

    assert utils.load_feedbacks_table(pgsql) == []

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/cancel',
        headers={'X-Eats-User': 'user_id=Alice'},
        params={'order_nr': SAMPLE_ORDER_NR},
    )
    assert response.status_code == 404
    assert _mock_eda_core.times_called == 1

    assert utils.load_feedbacks_table(pgsql) == []


@pytest.mark.pgsql('eats_feedback', files=['order.sql'])
@pytest.mark.now('2021-02-11 00:00')
async def test_cancel_unauthorized(taxi_eats_feedback, mockserver, pgsql):
    @mockserver.json_handler(
        '/eats-core-feedback/internal-api/v1/order/feedback-context',
    )
    def _mock_eda_core(request):
        assert False

    assert utils.load_feedbacks_table(pgsql) == []

    response = await taxi_eats_feedback.post(
        '/eats-feedback/v1/cancel', params={'order_nr': SAMPLE_ORDER_NR},
    )
    assert response.status_code == 401
    assert _mock_eda_core.times_called == 0

    assert utils.load_feedbacks_table(pgsql) == []
