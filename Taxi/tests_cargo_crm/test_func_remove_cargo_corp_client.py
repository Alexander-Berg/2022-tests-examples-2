import pytest


CORP_CLIENT_ID = 'some_long_id_string_of_length_32'


@pytest.mark.parametrize(
    'corp_client_id',
    (
        pytest.param(CORP_CLIENT_ID, id='ok'),
        pytest.param(CORP_CLIENT_ID[::-1], id='ok-wrong corp_client_id'),
    ),
)
async def test_func_remove_cargo_corp(
        taxi_cargo_crm, mockserver, corp_client_id,
):
    @mockserver.json_handler('cargo-corp/internal/cargo-corp/v1/client/remove')
    def _handler(request):
        assert request.headers['X-B2B-Client-Id'] == corp_client_id
        return mockserver.make_response(status=200, json={})

    for _ in range(2):
        response = await taxi_cargo_crm.post(
            '/functions/remove-cargo-corp-client',
            json={
                'corp_client_id': corp_client_id,
                'yandex_uid': 'yandex_uid',
            },
        )
        assert response.status_code == 200
