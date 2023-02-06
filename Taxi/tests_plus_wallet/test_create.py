import pytest


def make_request(yandex_uid, currency):
    request = {
        'yandex_uid': yandex_uid,
        'currency': currency,
        'user_ip': 'some_remote_ip',
    }
    return request


@pytest.mark.parametrize(
    'trust_response_code, expected_create_response_code',
    [(200, 200), (201, 200), (400, 500), (500, 500)],
)
async def test_create(
        taxi_plus_wallet,
        mockserver,
        trust_response_code,
        expected_create_response_code,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/trust-payments/v2/account')
    def handler(request):
        return mockserver.make_response(
            status=trust_response_code, json={'id': 'new_wallet_id'},
        )

    response = await taxi_plus_wallet.post(
        '/v1/create', make_request('some_yandex_uid', 'KZT'),
    )

    assert response.status_code == expected_create_response_code
    if expected_create_response_code == 200:
        content = response.json()
        assert content['wallet_id'] == 'new_wallet_id'
