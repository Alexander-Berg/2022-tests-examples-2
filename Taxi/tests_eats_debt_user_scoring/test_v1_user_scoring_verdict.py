import typing

import pytest

from tests_eats_debt_user_scoring import helpers

URL = '/internal/eats-debt-user-scoring/v1/user-scoring-verdict'

BASE_REQUEST = {
    'order_nr': 'test_order',
    'yandex_uid': '98765',
    'personal_phone_id': 'test_personal_phone_id',
    'place_id': '12345',
    'business': 'shop',
    'total_amount': '1000.00',
    'debt_amount': '1000.00',
    'currency': 'RUB',
    'request_type': 'common',
    'payment_type': 'card',
    'card_id': '123',
    'region_id': '54321',
}


@pytest.fixture(name='check_v1_user_scoring_verdict')
def _check_v1_user_scoring_verdict(taxi_eats_debt_user_scoring, mockserver):
    async def _inner(request_body, response_status=200, response_body=None):
        request_payload = request_body
        payload: typing.Dict[str, typing.Any] = {**request_payload}

        response = await taxi_eats_debt_user_scoring.post(URL, json=payload)
        assert response.status == response_status
        if response_body is not None:
            response_json = response.json()
            response_json.pop('identity', None)
            response_body.pop('identity', None)
            assert response_json == response_body

    return _inner


@pytest.mark.parametrize(
    'saturn_verdict, user_scoring_verdict, '
    'saturn_response_code, response_code',
    [
        pytest.param('accepted', 'accept', 200, 200, id='Saturn accepted'),
        pytest.param('rejected', 'reject', 200, 200, id='Saturn rejected'),
        pytest.param(None, 'reject', 400, 200, id='Saturn returned 400'),
        pytest.param(None, 'reject', 500, 200, id='Saturn returned 500'),
    ],
)
@pytest.mark.experiments3(filename='eats_user_scoring_debt_stats.json')
async def test_v1_user_scoring_verdict(
        check_v1_user_scoring_verdict,
        mock_saturn,
        mock_debt_collector,
        eats_core_eater,
        eats_order_stats,
        saturn_verdict,
        user_scoring_verdict,
        saturn_response_code,
        response_code,
):
    saturn_mock = mock_saturn(
        status=saturn_verdict, status_code=saturn_response_code,
    )
    mock_debt_collector()
    eats_order_stats()

    request_body = BASE_REQUEST

    verdict_response = None
    if response_code == 200:
        verdict_response = {'verdict': user_scoring_verdict}
    await check_v1_user_scoring_verdict(
        request_body=request_body,
        response_body=verdict_response,
        response_status=response_code,
    )

    assert saturn_mock.times_called == 1


@pytest.mark.parametrize(
    'debts, user_scoring_verdict, debt_collector_response_code, response_code',
    [
        pytest.param([], 'accept', 200, 200, id='No debts'),
        pytest.param(
            [
                helpers.make_debt(
                    debt=[
                        {
                            'payment_type': 'card',
                            'items': [helpers.make_debt_item('id', '1000')],
                        },
                    ],
                ),
            ],
            'reject',
            200,
            200,
            id='Limit exceeded',
        ),
        pytest.param(
            [
                helpers.make_debt(
                    debt=[
                        {
                            'payment_type': 'card',
                            'items': [helpers.make_debt_item('id', '15')],
                        },
                    ],
                ),
            ],
            'accept',
            200,
            200,
            id='Limit is not exceeded',
        ),
        pytest.param(None, None, 500, 500, id='debt-collector returned 500'),
    ],
)
@pytest.mark.experiments3(filename='eats_user_scoring_debt_stats.json')
@pytest.mark.experiments3(filename='eats_user_scoring_order_stats.json')
async def test_v1_user_scoring_verdict_debt_collector(
        check_v1_user_scoring_verdict,
        mock_saturn,
        mock_debt_collector,
        eats_core_eater,
        eats_order_stats,
        debts,
        user_scoring_verdict,
        debt_collector_response_code,
        response_code,
):
    mock_saturn(status='accepted')
    debt_collector_mock = mock_debt_collector(
        status_code=response_code, debts=debts,
    )
    eats_order_stats(
        helpers.make_counters(
            [
                {
                    'place_id': '1234',
                    'brand_id': '2112',
                    'business_type': 'restaurant',
                    'payment_method': 'applepay',
                    'orders_count': 1,
                },
            ],
        ),
    )

    request_body = BASE_REQUEST

    verdict_response = None
    if response_code == 200:
        verdict_response = {'verdict': user_scoring_verdict}
    await check_v1_user_scoring_verdict(
        request_body=request_body,
        response_body=verdict_response,
        response_status=response_code,
    )

    assert debt_collector_mock.times_called == 1


@pytest.mark.experiments3(filename='eats_user_scoring_debt_stats.json')
async def test_user_scoring_bad_request(taxi_eats_debt_user_scoring):
    response = await taxi_eats_debt_user_scoring.post(URL, json=None)
    assert response.status == 400


async def test_order_stats_fail_request(
        check_v1_user_scoring_verdict,
        eats_core_eater,
        mock_saturn,
        mock_debt_collector,
        eats_order_stats,
):
    mock_saturn(status='accepted', status_code=200)
    mock_debt_collector()
    eats_order_stats(status_code=500)
    await check_v1_user_scoring_verdict(
        request_body=BASE_REQUEST,
        response_body={'verdict': 'reject'},
        response_status=200,
    )
