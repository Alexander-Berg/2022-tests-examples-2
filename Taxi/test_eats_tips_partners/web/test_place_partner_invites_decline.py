import http

import pytest

from test_eats_tips_partners import conftest


@pytest.mark.parametrize(
    (
        'token',
        'invites_ids',
        'initiator',
        'expected_code',
        'expected_response',
        'expected_invites',
    ),
    (
        pytest.param(
            conftest.create_jwt('28'),
            '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
            'partner',
            http.HTTPStatus.OK,
            {'declined': ['21112f1d-4d9b-4aac-80b2-2a037453a4c8']},
            [],
            id='owned-by-partner',
        ),
        pytest.param(
            conftest.create_jwt('106'),
            '21112f1d-4d9b-4aac-80b2-2a037453a4c9',
            'place',
            http.HTTPStatus.OK,
            {'declined': ['21112f1d-4d9b-4aac-80b2-2a037453a4c9']},
            [],
            id='owned-by-place',
        ),
        pytest.param(
            conftest.create_jwt('28'),
            '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
            'place',
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': 'user has no places with admin role',
            },
            ['21112f1d-4d9b-4aac-80b2-2a037453a4c8'],
            id='not-owned-by-place',
        ),
        pytest.param(
            conftest.create_jwt('106'),
            '21112f1d-4d9b-4aac-80b2-2a037453a4c9',
            'partner',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'not_found',
                'message': 'not found invites for specified parameters',
            },
            ['21112f1d-4d9b-4aac-80b2-2a037453a4c9'],
            id='not-owned-by-partner',
        ),
        pytest.param(
            conftest.create_jwt('106'),
            'not-uuid',
            'partner',
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'invite_id is not UUID'},
            None,
            id='not-uuid',
        ),
        pytest.param(
            conftest.create_jwt('106'),
            '21112f1d-4d9b-4aac-80b2-2a037453a4cb',
            'partner',
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'not_found',
                'message': 'not found invites for specified parameters',
            },
            [],
            id='already-declined',
        ),
        pytest.param(
            conftest.create_jwt('28'),
            (
                '21112f1d-4d9b-4aac-80b2-2a037453a4ca,'
                '21112f1d-4d9b-4aac-80b2-2a037453a4c9'
            ),
            'partner',
            http.HTTPStatus.OK,
            {
                'declined': [
                    '21112f1d-4d9b-4aac-80b2-2a037453a4c9',
                    '21112f1d-4d9b-4aac-80b2-2a037453a4ca',
                ],
            },
            [],
            id='few-invites',
        ),
        pytest.param(
            conftest.create_jwt('28'),
            (
                '21112f1d-4d9b-4aac-80b2-2a037453a4ca,'
                '21112f1d-4d9b-4aac-80b2-2a037453a4cb'
            ),
            'partner',
            http.HTTPStatus.OK,
            {'declined': ['21112f1d-4d9b-4aac-80b2-2a037453a4ca']},
            [],
            id='few-invites-decline-only-one',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_place_partner_invites_decline(
        taxi_eats_tips_partners_web,
        pgsql,
        token,
        invites_ids,
        initiator,
        expected_code,
        expected_response,
        expected_invites,
):
    response = await taxi_eats_tips_partners_web.post(
        '/v1/place/partner/invite/decline',
        params={'invites_ids': invites_ids, 'initiator': initiator},
        headers={'X-CHAEVIE-TOKEN': token},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if expected_invites is None:
        return
    cursor = pgsql['eats_tips_partners'].cursor()
    cursor.execute(
        f"""
            SELECT id
            FROM eats_tips_partners.place_invitation
            WHERE
                id in (%s)
                AND status = 'invited'
            ORDER BY place_id, role
            """
        % ','.join(
            [f'\'{invite_id}\'' for invite_id in invites_ids.split(',')],
        ),
    )
    assert [row[0] for row in cursor.fetchall()] == expected_invites
