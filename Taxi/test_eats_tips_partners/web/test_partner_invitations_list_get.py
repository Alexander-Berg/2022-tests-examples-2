import http

import pytest

from test_eats_tips_partners import conftest


PHONE_17 = '+79000000017'
PHONE_4 = '+79000000030'

PERSONAL_PHONE_MAP = {'phone_id_17': PHONE_17, 'phone-id': PHONE_4}

PARTNER_ID_15 = '00000000-0000-0000-0000-000000000015'
PARTNER_ID_28 = '00000000-0000-0000-0000-000000000028'
PLACE_ID_106 = '10000000-0000-0000-0000-000000000106'
PLACE_ID_108 = '10000000-0000-0000-0000-000000000108'


@pytest.mark.parametrize(
    ('jwt_token', 'params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            conftest.create_jwt(15),
            {},
            http.HTTPStatus.OK,
            {
                'invites': [
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4cd',
                        'phone': PHONE_17,
                        'place_id': PLACE_ID_106,
                        'role': 'recipient',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_15,
                        'title': 'Фиксики inside',
                    },
                ],
                'has_more': False,
            },
            id='OK',
        ),
        pytest.param(
            conftest.create_jwt(10),
            {},
            http.HTTPStatus.OK,
            {'invites': [], 'has_more': False},
            id='no-invites',
        ),
        pytest.param(
            conftest.create_jwt(28),
            {},
            http.HTTPStatus.OK,
            {
                'invites': [
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
                        'phone': PHONE_4,
                        'place_id': PLACE_ID_108,
                        'role': 'recipient',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_28,
                        'title': '',
                    },
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4c9',
                        'phone': PHONE_4,
                        'place_id': PLACE_ID_106,
                        'role': 'admin',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_28,
                        'title': 'Фиксики inside',
                    },
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4ca',
                        'phone': PHONE_4,
                        'place_id': PLACE_ID_106,
                        'role': 'recipient',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_28,
                        'title': 'Фиксики inside',
                    },
                ],
                'has_more': False,
            },
            id='few-invites',
        ),
        pytest.param(
            conftest.create_jwt(28),
            {'limit': 2},
            http.HTTPStatus.OK,
            {
                'invites': [
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4c8',
                        'phone': PHONE_4,
                        'place_id': PLACE_ID_108,
                        'role': 'recipient',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_28,
                        'title': '',
                    },
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4c9',
                        'phone': PHONE_4,
                        'place_id': PLACE_ID_106,
                        'role': 'admin',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_28,
                        'title': 'Фиксики inside',
                    },
                ],
                'has_more': True,
            },
            id='limit',
        ),
        pytest.param(
            conftest.create_jwt(28),
            {'limit': 2, 'offset': 1},
            http.HTTPStatus.OK,
            {
                'invites': [
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4c9',
                        'phone': PHONE_4,
                        'place_id': PLACE_ID_106,
                        'role': 'admin',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_28,
                        'title': 'Фиксики inside',
                    },
                    {
                        'id': '21112f1d-4d9b-4aac-80b2-2a037453a4ca',
                        'phone': PHONE_4,
                        'place_id': PLACE_ID_106,
                        'role': 'recipient',
                        'status': 'invited',
                        'partner_id': PARTNER_ID_28,
                        'title': 'Фиксики inside',
                    },
                ],
                'has_more': False,
            },
            id='offset',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_invitations_list_get(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        mockserver,
        jwt_token,
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
        '/v1/partner/invites',
        params=params,
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
