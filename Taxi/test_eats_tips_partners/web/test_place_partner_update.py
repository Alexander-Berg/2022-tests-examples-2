import http

import pytest

from test_eats_tips_partners import conftest


@pytest.mark.parametrize(
    ('jwt_token', 'params', 'expected_code'),
    (
        pytest.param(
            conftest.create_jwt(100),
            {
                'place_id': '10000000-0000-0000-0000-000000000100',
                'partner_ids': '00000000-0000-0000-0000-000000000010',
            },
            http.HTTPStatus.OK,
            id='OK',
        ),
        pytest.param(
            conftest.create_jwt(100),
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'partner_ids': '00000000-0000-0000-0000-000000000010',
            },
            http.HTTPStatus.FORBIDDEN,
            id='FORBIDDEN',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_place_partner_update(
        taxi_eats_tips_partners_web, jwt_token, params, expected_code,
):
    response = await taxi_eats_tips_partners_web.put(
        '/v1/place/partner',
        json={'show_in_menu': False},
        params=params,
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    assert response.status == expected_code
