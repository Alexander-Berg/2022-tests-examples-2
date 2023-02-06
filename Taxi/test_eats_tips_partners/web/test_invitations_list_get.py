import http

import pytest

from test_eats_tips_partners import conftest


PARTNER_ID_14 = '00000000-0000-0000-0000-000000000014'
PARTNER_ID_27 = '00000000-0000-0000-0000-000000000027'
PARTNER_ID_28 = '00000000-0000-0000-0000-000000000028'

PLACE_ID_000 = '10000000-0000-0000-0000-000000000000'
PLACE_ID_100 = '10000000-0000-0000-0000-000000000100'
PLACE_ID_105 = '10000000-0000-0000-0000-000000000105'
PLACE_ID_108 = '10000000-0000-0000-0000-000000000108'
PLACE_ID_109 = '10000000-0000-0000-0000-000000000109'

PHONE_14 = '+79000000014'
PHONE_27 = '+79000000027'
PHONE_OTHER = '+79000000028'
PHONE_AWESOME = '+79000000029'
PHONE_4 = '+79000000030'

PERSONAL_PHONE_MAP = {
    'phone_id_14': PHONE_14,
    'phone_id_27': PHONE_27,
    'other_phone_id': PHONE_OTHER,
    'awesome_phone_id': PHONE_AWESOME,
    'phone-id': PHONE_4,
}


def _make_query(places_ids, limit, offset):
    result = {'limit': limit, 'offset': offset}
    if places_ids is not None:
        result['places_ids'] = places_ids
    return result


def _make_invitation(
        invitation_id,
        phone,
        place_id,
        role='recipient',
        partner_id=None,
        title='',
):
    response = {
        'id': invitation_id,
        'phone': phone,
        'place_id': place_id,
        'role': role,
        'status': 'invited',
        'title': title,
    }
    if partner_id is not None:
        response['partner_id'] = partner_id
    return response


INVITATION_2 = _make_invitation(
    '21112f1d-4d9b-4aac-80b2-2a037453a4c2',
    PHONE_27,
    PLACE_ID_109,
    partner_id=PARTNER_ID_27,
)
INVITATION_3 = _make_invitation(
    '21112f1d-4d9b-4aac-80b2-2a037453a4c3', PHONE_OTHER, PLACE_ID_109,
)
INVITATION_4 = _make_invitation(
    '21112f1d-4d9b-4aac-80b2-2a037453a4c4', PHONE_AWESOME, PLACE_ID_109,
)
INVITATION_6 = _make_invitation(
    '21112f1d-4d9b-4aac-80b2-2a037453a4c6', PHONE_AWESOME, PLACE_ID_108,
)
INVITATION_7 = _make_invitation(
    '21112f1d-4d9b-4aac-80b2-2a037453a4c7',
    PHONE_AWESOME,
    PLACE_ID_108,
    role='admin',
)


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            _make_query(PLACE_ID_109, 1, 0),
            http.HTTPStatus.OK,
            {
                'invites': [
                    {'phone': PHONE_AWESOME, 'invites': [INVITATION_4]},
                ],
                'has_more': True,
            },
            id='no-offset',
        ),
        pytest.param(
            _make_query(PLACE_ID_109, 1, 1),
            http.HTTPStatus.OK,
            {
                'invites': [{'phone': PHONE_OTHER, 'invites': [INVITATION_3]}],
                'has_more': True,
            },
            id='with-offset',
        ),
        pytest.param(
            _make_query(PLACE_ID_109, 10, 0),
            http.HTTPStatus.OK,
            {
                'invites': [
                    {'phone': PHONE_AWESOME, 'invites': [INVITATION_4]},
                    {'phone': PHONE_OTHER, 'invites': [INVITATION_3]},
                    {'phone': PHONE_27, 'invites': [INVITATION_2]},
                ],
                'has_more': False,
            },
            id='has-more-false',
        ),
        pytest.param(
            _make_query(PLACE_ID_109, 1, 10),
            http.HTTPStatus.OK,
            {'invites': [], 'has_more': False},
            id='too-big-offset',
        ),
        pytest.param(
            _make_query(f'{PLACE_ID_108},{PLACE_ID_109}', 10, 0),
            http.HTTPStatus.OK,
            {
                'invites': [
                    {
                        'phone': PHONE_AWESOME,
                        'invites': [INVITATION_4, INVITATION_6, INVITATION_7],
                    },
                    {'phone': PHONE_OTHER, 'invites': [INVITATION_3]},
                    {
                        'phone': PHONE_4,
                        'invites': [
                            _make_invitation(
                                '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
                                PHONE_4,
                                PLACE_ID_108,
                                role='recipient',
                                partner_id=PARTNER_ID_28,
                            ),
                        ],
                    },
                    {'phone': PHONE_27, 'invites': [INVITATION_2]},
                ],
                'has_more': False,
            },
            id='few_places',
        ),
        pytest.param(
            _make_query(PLACE_ID_000, 10, 0),
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': f'user has no admin role in place {PLACE_ID_000}',
            },
            id='unexpected-place',
        ),
        pytest.param(
            _make_query('not-uuid', 1, 0),
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'place_id is not UUID'},
            id='not-uuid',
        ),
        pytest.param(
            _make_query(PLACE_ID_105, 1, 0),
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': f'user has no admin role in place {PLACE_ID_105}',
            },
            id='no permissions',
        ),
        pytest.param(
            _make_query(f'{PLACE_ID_105},{PLACE_ID_109}', 1, 0),
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'forbidden',
                'message': f'user has no admin role in place {PLACE_ID_105}',
            },
            id='only-one-permission',
        ),
        pytest.param(
            _make_query(None, 10, 0),
            http.HTTPStatus.OK,
            {
                'invites': [
                    {
                        'phone': PHONE_AWESOME,
                        'invites': [INVITATION_4, INVITATION_6, INVITATION_7],
                    },
                    {'phone': PHONE_OTHER, 'invites': [INVITATION_3]},
                    {
                        'phone': PHONE_4,
                        'invites': [
                            _make_invitation(
                                '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
                                PHONE_4,
                                PLACE_ID_108,
                                role='recipient',
                                partner_id=PARTNER_ID_28,
                            ),
                        ],
                    },
                    {
                        'phone': PHONE_14,
                        'invites': [
                            _make_invitation(
                                '21112f1d-4d9b-4aac-80b2-2a037453a4ce',
                                PHONE_14,
                                PLACE_ID_100,
                                role='recipient',
                                partner_id=PARTNER_ID_14,
                                title='Деревня Вилларибо',
                            ),
                        ],
                    },
                    {'phone': PHONE_27, 'invites': [INVITATION_2]},
                ],
                'has_more': False,
            },
            id='no-query',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_invitations_list_get(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        mockserver,
        params,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _mock_phones_retrieve(request):
        return {
            'items': [
                {'id': item['id'], 'value': PERSONAL_PHONE_MAP[item['id']]}
                for item in request.json['items']
            ],
        }

    response = await taxi_eats_tips_partners_web.get(
        '/v1/place/invites/list/by-phone',
        params=params,
        headers={'X-CHAEVIE-TOKEN': conftest.create_jwt('700')},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
