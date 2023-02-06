import http

import pytest

from test_eats_tips_partners import conftest


@pytest.mark.parametrize(
    (
        'invite_ids',
        'jwt_token',
        'expected_code',
        'expected_response',
        'expected_place_partners',
    ),
    (
        pytest.param(
            '21112f1d-4d9b-4aac-80b2-2a037453a4c9,'
            '21112f1d-4d9b-4aac-80b2-2a037453a4ca,'
            '21112f1d-4d9b-4aac-80b2-2a037453a4cc,'
            '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
            conftest.create_jwt('28'),
            http.HTTPStatus.OK,
            {
                'accepted': [
                    '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
                    '21112f1d-4d9b-4aac-80b2-2a037453a4c9',
                    '21112f1d-4d9b-4aac-80b2-2a037453a4ca',
                ],
                'errors': [],
                'need_register_card': False,
            },
            [
                (
                    '10000000-0000-0000-0000-000000000108',
                    '00000000-0000-0000-0000-000000000028',
                    ['recipient'],
                ),
                (
                    '10000000-0000-0000-0000-000000000106',
                    '00000000-0000-0000-0000-000000000028',
                    ['admin', 'recipient'],
                ),
            ],
            id='ok',
        ),
        pytest.param(
            '21112f1d-4d9b-4aac-80b2-2a037453a4ce',
            conftest.create_jwt('14'),
            http.HTTPStatus.OK,
            {
                'accepted': ['21112f1d-4d9b-4aac-80b2-2a037453a4ce'],
                'errors': [],
                'need_register_card': False,
            },
            [
                (
                    '10000000-0000-0000-0000-000000000100',
                    '00000000-0000-0000-0000-000000000014',
                    ['recipient'],
                ),
            ],
            id='deleted',
        ),
        pytest.param(
            (
                '21112f1d-4d9b-4aac-80b2-2a037453a4cd,'
                '21112f1d-4d9b-4aac-80b2-2a037453a4c8'
            ),
            conftest.create_jwt('15'),
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': (
                    'user has no permissions for invitation '
                    '21112f1d-4d9b-4aac-80b2-2a037453a4c8'
                ),
            },
            [],
            id='no-permissions',
        ),
        pytest.param(
            '21112f1d-4d9b-4aac-80b2-2a037453a4cd',
            conftest.create_jwt('15'),
            http.HTTPStatus.OK,
            {
                'accepted': [],
                'errors': [
                    'virtual card required to accept '
                    '21112f1d-4d9b-4aac-80b2-2a037453a4cd',
                ],
                'need_register_card': True,
            },
            [],
            id='no-virtual-card',
        ),
        pytest.param(
            'not-uuid',
            conftest.create_jwt('15'),
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'invite_id is not UUID'},
            [],
            id='not-uuid',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_place_partner_invite_accept(
        taxi_eats_tips_partners_web,
        pgsql,
        invite_ids,
        jwt_token,
        expected_code,
        expected_response,
        expected_place_partners,
):
    response = await taxi_eats_tips_partners_web.post(
        '/v1/place/partner/invite/accept',
        json={},
        params={'invites_ids': invite_ids},
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if not expected_place_partners:
        return
    cursor = pgsql['eats_tips_partners'].cursor()

    for place_partner in expected_place_partners:
        cursor.execute(
            f"""
            SELECT alias, roles, confirmed
            FROM eats_tips_partners.places_partners
            WHERE
                place_id='{place_partner[0]}'
                AND partner_id='{place_partner[1]}'
                AND deleted_at IS NULL
            ;
            """,
        )
        row = cursor.fetchone()
        assert row
        assert place_partner[2] == row[1]
        assert sorted(row[1]) == sorted(set(row[1]))
        assert row[2]
        cursor.execute(
            f"""
            SELECT type
            FROM eats_tips_partners.alias
            WHERE alias='{row[0]}'
            ;
            """,
        )
        alias_type = cursor.fetchone()
        assert alias_type[0] == 'place_partner'
