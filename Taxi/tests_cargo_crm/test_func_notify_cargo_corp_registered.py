import pytest

CORP_CLIENT_ID = 'corp_client_id'
MOCK_NOW = '2021-10-08T07:04:55+00:00'


class TestNotifyCargoCorpRegistered:
    @pytest.mark.now(MOCK_NOW)
    async def test_notify_registered(
            self, mockserver, request_notify_registered,
    ):
        @mockserver.json_handler(
            '/cargo-corp/internal/cargo-corp/v1/client/update-registered',
        )
        def _reg_handler(request):
            assert request.json['registered_ts'] == MOCK_NOW
            assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
            return mockserver.make_response(status=200)

        response = await request_notify_registered()
        assert response.status_code == 200


@pytest.fixture(name='request_notify_registered')
def _request_notify_registered(taxi_cargo_crm):
    async def wrapper():
        url = '/functions/notify-cargo-corp-registered'

        body = {'corp_client_id': CORP_CLIENT_ID}
        response = await taxi_cargo_crm.post(url, json=body)
        return response

    return wrapper
