import http

import pytest

from test_eats_tips_partners import conftest


def _format_eats_tips_partners_sd_response(*, place_id, partner_id):
    return {'place_id': place_id, 'partner_id': partner_id}


@pytest.mark.parametrize(
    ('jwt_token', 'params', 'expected_code'),
    (
        pytest.param(
            conftest.create_jwt(100),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-000000000100',
                partner_id='00000000-0000-0000-0000-000000000010',
            ),
            http.HTTPStatus.OK,
            id='ok-delete',
        ),
        pytest.param(
            conftest.create_jwt(10),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-000000000100',
                partner_id='00000000-0000-0000-0000-000000000010',
            ),
            http.HTTPStatus.OK,
            id='ok-partner-partner-delete',
        ),
        pytest.param(
            conftest.create_jwt(100),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-000000000101',
                partner_id='00000000-0000-0000-0000-000000000010',
            ),
            http.HTTPStatus.FORBIDDEN,
            id='forbidden-delete',
        ),
        pytest.param(
            conftest.create_jwt(100),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-000000000100',
                partner_id='00000000-0000-0000-0000-000000000012',
            ),
            http.HTTPStatus.NOT_FOUND,
            id='partner-not-in-place-delete',
        ),
        pytest.param(
            conftest.create_jwt(11),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-000000000100',
                partner_id='00000000-0000-0000-0000-000000000010',
            ),
            http.HTTPStatus.FORBIDDEN,
            id='partner-not-admin-place-delete',
        ),
        pytest.param(
            conftest.create_jwt(100),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-000000000100',
                partner_id='00000000-0000-0000-0000-000000000100',
            ),
            http.HTTPStatus.CONFLICT,
            id='admin-admin-delete',
        ),
        pytest.param(
            conftest.create_jwt(100),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-000000000100',
                partner_id='00000000-0000-0000-0000-000000000014',
            ),
            http.HTTPStatus.NOT_FOUND,
            id='partner-already-deleted',
        ),
        pytest.param(
            conftest.create_jwt(100),
            _format_eats_tips_partners_sd_response(
                place_id='10000000-0000-0000-0000-15',
                partner_id='00000000-0000-0000-0000-000000000014',
            ),
            http.HTTPStatus.BAD_REQUEST,
            id='place_id-not-uuid',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
async def test_place_partner_delete(
        taxi_eats_tips_partners_web, jwt_token, pgsql, params, expected_code,
):
    response = await taxi_eats_tips_partners_web.delete(
        '/v1/place/partner',
        params=params,
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    assert response.status == expected_code
    if response.status != http.HTTPStatus.OK:
        return None
    with pgsql['eats_tips_partners'].dict_cursor() as cursor:
        cursor.execute(
            f'select place_id '
            f'from eats_tips_partners.places_partners '
            f'where deleted_at is not NULL '
            f'and place_id = %s '
            f'and partner_id = %s;',
            (params['place_id'], params['partner_id']),
        )
        order = cursor.fetchall()[-1]
    assert order['place_id'] == params['place_id']
