import pytest


@pytest.mark.parametrize(
    'response_code_authorizer,token', [(200, '000'), (404, '111')],
)
async def test_external_partners_logout(
        taxi_eats_partners, response_code_authorizer, token, mockserver,
):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/session/unset')
    def _mock_authorizer(request):
        return mockserver.make_response(status=response_code_authorizer)

    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/logout', headers={'X-Token': token},
    )

    assert response.status_code == 200
    assert response.json() == {'is_success': True}
