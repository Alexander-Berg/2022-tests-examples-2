import pytest


# deprecated tests
@pytest.mark.parametrize(
    'response_code,email,password',
    [
        (400, 'partner1@partner.com', 'qwerty-123'),
        (400, 'PARTNER1@PARTNER.COM', 'qwerty-123'),
        (400, 'partner1@partner.com', 'qwerty-qwe'),
        (400, 'partner2@partner.com', 'qwerty-123'),
        (400, 'partner3@partner.com', 'qwerty-123'),
        (400, 'partner2@partner.com', 'qwerty-123'),
    ],
)
async def test_external_partners_login(
        taxi_eats_partners, response_code, email, password,
):
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/login',
        json={'email': email},
        headers={'X-Eats-Restapp-Auth-Creds': password},
    )

    assert response.status_code == response_code
