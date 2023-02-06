import pytest

AUTH_PARAMETERS = {
    'provider': 'ez_count',
    'tin': 'park_tin',
    'code': 'code_from_ez',
}
BAD_AUTH_PARAMETERS = {
    'provider': 'ez_count',
    'tin': 'park_tin',
    'code': 'wrong_code_not_from_ez',
}


@pytest.mark.config(EAZY_COUNT_CARGO_URL={'auth_url': 'example.com'})
@pytest.mark.parametrize(
    'response_code,auth_parameters,response_json',
    (
        pytest.param(200, AUTH_PARAMETERS, {}, id='ok request'),
        pytest.param(
            400,
            BAD_AUTH_PARAMETERS,
            {
                'code': 'auth_error',
                'details': {},
                'message': (
                    'Eazy Count rejected auth with supplied credentials.'
                ),
            },
            id='invalid request',
        ),
    ),
)
async def test_auth(
        taxi_cargo_fiscal,
        mock_ez_auth,
        mock_ez_user_type,
        response_code,
        auth_parameters,
        response_json,
):
    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts/delivery/taxiorders/register-token',
        json=auth_parameters,
    )
    assert response.status_code == response_code
    assert response.json() == response_json
