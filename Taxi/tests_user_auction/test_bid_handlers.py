import json

import pytest

HEADERS = {
    'X-Yandex-UID': '4003514353',
    'X-Request-Language': 'ru',
    'X-Idempotency-Token': '123',
}


@pytest.mark.parametrize(
    'status_code,response',
    [
        pytest.param(200, None),
        pytest.param(
            404, json.dumps({'code': 'not_found', 'message': 'Not found'}),
        ),
    ],
)
async def test_bid_accept(
        taxi_user_auction, mockserver, status_code, response,
):
    @mockserver.handler(
        '/contractor-orders-multioffer/internal/v1/orders-auction/bid/accept',
    )
    async def _mock_multioffer(request, *args, **kwargs):
        return mockserver.make_response(
            status=status_code,
            content_type='application/json',
            response=response,
        )

    res = await taxi_user_auction.post(
        '/4.0/user-auction/v1/bid/accept',
        headers=HEADERS,
        json={
            'multioffer_id': 'b5d8c6fa-c891-4306-924f-0db1c217eb28',
            'bid_id': '72bcbde8-eaed-460f-8f88-eeb4e056c317',
        },
    )
    assert res.status == status_code
    if response is not None:
        r_json = res.json()
        assert r_json == json.loads(response)


@pytest.mark.parametrize(
    'status_code,response',
    [
        pytest.param(
            200,
            {
                'bids_statuses': [
                    {
                        'bid_id': '72bcbde8-eaed-460f-8f88-eeb4e056c317',
                        'success': True,
                    },
                ],
            },
        ),
        pytest.param(404, {'code': 'not_found', 'message': 'Not found'}),
    ],
)
async def test_bid_reject(
        taxi_user_auction, mockserver, status_code, response,
):
    @mockserver.handler(
        '/contractor-orders-multioffer/internal/v1/orders-auction/bid/reject',
    )
    async def _mock_multioffer(request, *args, **kwargs):
        return mockserver.make_response(
            status=status_code,
            content_type='application/json',
            response=json.dumps(response),
        )

    res = await taxi_user_auction.post(
        '/4.0/user-auction/v1/bid/reject',
        headers=HEADERS,
        json={
            'multioffer_id': 'b5d8c6fa-c891-4306-924f-0db1c217eb28',
            'bids': [{'bid_id': '72bcbde8-eaed-460f-8f88-eeb4e056c317'}],
        },
    )
    assert res.status == status_code
    assert res.json() == response
