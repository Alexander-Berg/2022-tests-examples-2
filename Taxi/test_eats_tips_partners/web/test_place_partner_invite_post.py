import collections
import datetime
import http

from aiohttp import web
import pytest

from taxi.util import dates

from test_eats_tips_partners import conftest

PHONE_27 = '+79000000027'
PHONE_28 = '+79000000028'
OTHER_PHONE = '+71112223344'
PHONE_ID_27 = 'phone_id_27'
PHONE_ID_28 = 'phone_id_28'
OTHER_PHONE_ID = 'other_phone_id'

PERSONAL_PHONE_MAP = {
    PHONE_27: PHONE_ID_27,
    PHONE_28: PHONE_ID_28,
    OTHER_PHONE: OTHER_PHONE_ID,
}

PLACE_ID_100 = '10000000-0000-0000-0000-000000000100'
PLACE_ID_105 = '10000000-0000-0000-0000-000000000105'
PLACE_ID_108 = '10000000-0000-0000-0000-000000000108'
PLACE_ID_109 = '10000000-0000-0000-0000-000000000109'
PLACE_ID_110 = '10000000-0000-0000-0000-000000000110'
PARTNER_ID_27 = '00000000-0000-0000-0000-000000000027'
PARTNER_ID_28 = '00000000-0000-0000-0000-000000000028'
PARTNER_ID_29 = '00000000-0000-0000-0000-000000000029'

NOW = datetime.datetime(2022, 1, 1, 12, 0)


def _create_place(place_id, roles=None):
    if roles is None:
        roles = ['admin', 'recipient']
    return {'place_id': place_id, 'roles': roles}


@pytest.fixture
async def _mock_personal_phone(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    async def _mock_phones_store(request):
        phone_id = PERSONAL_PHONE_MAP.get(request.json['value'])
        if phone_id:
            return {'value': request.json['value'], 'id': phone_id}
        return web.json_response({}, status=http.HTTPStatus.NOT_FOUND)


@pytest.mark.parametrize(
    ('data', 'jwt_token', 'expected_code', 'invitations', 'partner_exists'),
    (
        pytest.param(
            {'phone': PHONE_27, 'places': [_create_place(PLACE_ID_100)]},
            conftest.create_jwt('100'),
            http.HTTPStatus.OK,
            [_create_place(PLACE_ID_100, ['admin', 'recipient'])],
            True,
            id='ok',
        ),
        pytest.param(
            {'phone': PHONE_28, 'places': [_create_place(PLACE_ID_100)]},
            conftest.create_jwt('100'),
            http.HTTPStatus.OK,
            [_create_place(PLACE_ID_100, ['admin', 'recipient'])],
            True,
            id='mysql-phone-id',
        ),
        pytest.param(
            {'phone': PHONE_28, 'places': [_create_place(PLACE_ID_108)]},
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            [],
            True,
            id='one-role-exists',
        ),
        pytest.param(
            {
                'phone': PHONE_28,
                'places': [_create_place(PLACE_ID_108, ['recipient'])],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            [],
            True,
            id='same-role',
        ),
        pytest.param(
            {
                'phone': PHONE_28,
                'places': [_create_place(PLACE_ID_108, ['admin'])],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            [],
            True,
            id='different-role',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [_create_place(PLACE_ID_109, ['admin'])],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            [_create_place(PLACE_ID_109, ['admin'])],
            True,
            id='declined-invite',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [_create_place(PLACE_ID_109, ['recipient'])],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            [],
            True,
            id='existing-invite',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [
                    _create_place(PLACE_ID_109, ['admin', 'recipient']),
                ],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            [_create_place(PLACE_ID_109, ['admin'])],
            True,
            id='existing-and-declined-invite',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [
                    _create_place(PLACE_ID_108, ['admin']),
                    _create_place(PLACE_ID_109, ['admin']),
                ],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            [
                _create_place(PLACE_ID_108, ['admin']),
                _create_place(PLACE_ID_109, ['admin']),
            ],
            True,
            id='few-places',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [
                    _create_place(PLACE_ID_109, ['recipient']),
                    _create_place(PLACE_ID_108, ['admin']),
                ],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            [_create_place(PLACE_ID_108, ['admin'])],
            True,
            id='few-places-only-one-ok',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [
                    _create_place(PLACE_ID_109, ['recipient']),
                    _create_place(PLACE_ID_110, ['recipient']),
                ],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            [],
            True,
            id='few-places-no-one-ok',
        ),
        pytest.param(
            {'phone': OTHER_PHONE, 'places': [_create_place(PLACE_ID_100)]},
            conftest.create_jwt('100'),
            http.HTTPStatus.OK,
            [_create_place(PLACE_ID_100, ['admin', 'recipient'])],
            False,
            id='phone-not-exists',
        ),
        pytest.param(
            {
                'phone': OTHER_PHONE,
                'places': [_create_place(PLACE_ID_109, ['recipient'])],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            [],
            False,
            id='phone-not-exists-invitation-exists',
        ),
        pytest.param(
            {
                'phone': OTHER_PHONE,
                'places': [
                    _create_place(PLACE_ID_100, ['recipient']),
                    _create_place(PLACE_ID_109, ['admin']),
                ],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            [
                _create_place(PLACE_ID_100, ['recipient']),
                _create_place(PLACE_ID_109, ['admin']),
            ],
            False,
            id='phone-not-exists-few-places',
        ),
        pytest.param(
            {
                'phone': OTHER_PHONE,
                'places': [
                    _create_place(PLACE_ID_109, ['recipient']),
                    _create_place(PLACE_ID_100, ['recipient']),
                ],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            [_create_place(PLACE_ID_100, ['recipient'])],
            False,
            id='phone-not-exists-few-places-only-one-ok',
        ),
        pytest.param(
            {
                'phone': 'not-existing-phone-id',
                'places': [_create_place(PLACE_ID_100)],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.BAD_REQUEST,
            [],
            None,
            id='phone-not-exists-in-personal',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [
                    _create_place('10000000-0000-0000-0000-000000000999'),
                ],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.FORBIDDEN,
            [],
            None,
            id='place-not-exists',
        ),
        pytest.param(
            {'phone': PHONE_27, 'places': [_create_place('blah-blah-blah')]},
            conftest.create_jwt('700'),
            http.HTTPStatus.BAD_REQUEST,
            [],
            None,
            id='place-id-not-uuid',
        ),
        pytest.param(
            {'phone': PHONE_27, 'places': [_create_place(PLACE_ID_100)]},
            conftest.create_jwt('10'),
            http.HTTPStatus.FORBIDDEN,
            [],
            None,
            id='no-permissions',
        ),
        pytest.param(
            {
                'phone': PHONE_27,
                'places': [
                    _create_place(PLACE_ID_100),
                    _create_place(PLACE_ID_105),
                ],
            },
            conftest.create_jwt('100'),
            http.HTTPStatus.FORBIDDEN,
            [],
            None,
            id='only-one-permission',
        ),
    ),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_place_partner_invite_post(
        taxi_eats_tips_partners_web,
        jwt_token,
        mock_tvm_rules,
        _mock_personal_phone,
        pgsql,
        data,
        expected_code,
        invitations,
        partner_exists,
):
    response = await taxi_eats_tips_partners_web.post(
        '/v1/place/partner/invite',
        json=data,
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    assert response.status == expected_code
    body = await response.json()
    if expected_code == http.HTTPStatus.OK:
        received = [
            {'place_id': d['place_id'], 'roles': sorted(d['roles'])}
            for d in body['invited']
        ]
        assert received == invitations

    cursor = pgsql['eats_tips_partners'].cursor()
    phone_id = PERSONAL_PHONE_MAP.get(data['phone'])
    if phone_id is None:
        return
    cursor.execute(
        f"""
        SELECT role, created_at, partner_id, place_id
        FROM eats_tips_partners.place_invitation
        WHERE
            phone_id = '{phone_id}'
            AND status = 'invited'
            AND created_at >= '{NOW.isoformat()}'
        ORDER BY place_id, role
        """,
    )
    rows = cursor.fetchall()
    response_invites = collections.defaultdict(list)
    for row in rows:
        assert dates.localize(row[1]) == dates.localize(NOW)
        assert bool(row[2]) is partner_exists
        response_invites[row[3]].append(row[0])
    response_invitations = []
    for place_id, roles in response_invites.items():
        response_invitations.append({'place_id': place_id, 'roles': roles})
    assert response_invitations == invitations


@pytest.mark.parametrize(
    ('data', 'jwt_token', 'expected_code', 'expected_id'),
    (
        pytest.param(
            {'phone': PHONE_27, 'places': [_create_place(PLACE_ID_100)]},
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            PARTNER_ID_27,
            id='already-in-pg',
        ),
        pytest.param(
            {'phone': PHONE_28, 'places': [_create_place(PLACE_ID_100)]},
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            PARTNER_ID_28,
            id='only-in-mysql',
        ),
        pytest.param(
            {'phone': PHONE_28, 'places': [_create_place(PLACE_ID_108)]},
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            PARTNER_ID_28,
            id='one-role-exists',
        ),
        pytest.param(
            {
                'phone': PHONE_28,
                'places': [_create_place(PLACE_ID_108, ['recipient'])],
            },
            conftest.create_jwt('700'),
            http.HTTPStatus.CONFLICT,
            PARTNER_ID_28,
            id='conflict-but-update',
        ),
        pytest.param(
            {'phone': OTHER_PHONE, 'places': [_create_place(PLACE_ID_100)]},
            conftest.create_jwt('700'),
            http.HTTPStatus.OK,
            None,
            id='phone-not-exists',
        ),
    ),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    EATS_TIPS_PARTNERS_READ_USER_CONDITION='read_both_return_mysql',
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_place_partner_invite_post_sync(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        _mock_personal_phone,
        pgsql,
        data,
        jwt_token,
        expected_code,
        expected_id,
):
    response = await taxi_eats_tips_partners_web.post(
        '/v1/place/partner/invite',
        json=data,
        headers={'X-CHAEVIE-TOKEN': jwt_token},
    )
    assert response.status == expected_code

    cursor = pgsql['eats_tips_partners'].cursor()
    phone_id = PERSONAL_PHONE_MAP.get(data['phone'])
    cursor.execute(
        f"""
        SELECT id
        FROM eats_tips_partners.partner
        WHERE phone_id = '{phone_id}'
        """,
    )
    row = cursor.fetchone()
    if expected_id is not None:
        assert row[0] == expected_id
    else:
        assert row is None
