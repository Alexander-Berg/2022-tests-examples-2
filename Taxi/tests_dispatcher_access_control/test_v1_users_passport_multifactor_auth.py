from tests_dispatcher_access_control import utils

ENDPOINT = 'fleet/dac/v1/users/passport/multifactor-auth/enable'


def build_headers(
        user_ticket='ticket_valid1',
        user_ticket_provider='yandex',
        remote_ip='1.2.3.4',
        yandex_uid='100',
        service_ticket=utils.MOCK_SERVICE_TICKET,
):
    headers = {
        'X-Ya-User-Ticket': user_ticket,
        'X-Ya-User-Ticket-Provider': user_ticket_provider,
        'X-Remote-IP': remote_ip,
        'X-Yandex-UID': yandex_uid,
        'X-Ya-Service-Ticket': service_ticket,
    }
    return headers


async def test_success(taxi_dispatcher_access_control, mockserver):
    @mockserver.json_handler('/passport-internal/2/account/options/')
    def _account_options(request):
        assert request.form == {'sms_2fa_on': 'yes'}
        return mockserver.make_response(json={'status': 'ok'}, status=200)

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, headers=build_headers(),
    )

    assert response.status_code == 200, response.text


async def test_fail(taxi_dispatcher_access_control, mockserver):
    @mockserver.json_handler('/passport-internal/2/account/options/')
    def _account_options(request):
        assert request.form == {'sms_2fa_on': 'yes'}
        return mockserver.make_response(
            json={'status': 'fail', 'errors': ['form.invalid']}, status=200,
        )

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, headers=build_headers(),
    )

    assert response.status_code == 500, response.text
