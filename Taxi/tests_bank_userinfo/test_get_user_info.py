import pytest


def get_user_info(taxi_bank_userinfo):
    return taxi_bank_userinfo.post(
        '/v1/userinfo/v1/get_user_info',
        headers={
            'X-Yandex-BUID': 'buid',
            'X-YaBank-SessionUUID': 'session',
            'X-YaBank-PhoneID': 'phone_id',
            'X-Yandex-UID': 'uid',
            'X-Ya-User-Ticket': 'user_ticket',
        },
    )


def check_request(request):
    assert request.method == 'POST'
    buid = request.headers['X-Yandex-BUID']
    assert buid


async def test_get_userinfo_returns_500_if_client_not_available(
        taxi_bank_userinfo, mockserver,
):
    @mockserver.handler('/bank-core-client/v1/client/info/get')
    def _handler(request):
        check_request(request)
        return mockserver.make_response(status=500)

    response = await get_user_info(taxi_bank_userinfo)
    assert response.status_code == 500


async def test_get_userinfo_returns_404_if_client_returns_404(
        taxi_bank_userinfo, mockserver,
):
    @mockserver.handler('/bank-core-client/v1/client/info/get')
    def _handler(request):
        check_request(request)
        return mockserver.make_response(
            status=404,
            json={'code': 'CLIENT_NOT_FOUND', 'message': 'Client not found'},
        )

    response = await get_user_info(taxi_bank_userinfo)
    assert response.status_code == 404


@pytest.mark.parametrize('buid', ['ANONYMOUS', 'IDENTIFIED', 'KYC', 'KYC_EDS'])
async def test_get_userinfo_returns_auth_status(
        buid, taxi_bank_userinfo, mockserver,
):
    @mockserver.handler('/bank-core-client/v1/client/info/get')
    def _handler(request):
        check_request(request)
        return mockserver.make_response(
            json={
                'auth_level': buid,
                'phone_number': '+79002701232',
                'solar_id': '16425',
                'first_name': None,
                'last_name': None,
                'patronymic': None,
                'birth_date': None,
            },
        )

    response = await get_user_info(taxi_bank_userinfo)
    assert response.status_code == 200
    assert response.json()['auth_status'] == buid
    assert response.json()['phone'] == '+79002701232'
