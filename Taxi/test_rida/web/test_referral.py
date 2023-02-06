from typing import List
from typing import Optional
from typing import Tuple

import pytest

from test_rida import experiments_utils
from test_rida import helpers


_USER_GUIDS = [
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
]
_USER_PHONES = ['msisdn1234', 'msisdn5678']

_USER_DATA = list(zip(_USER_GUIDS, _USER_PHONES))


def _get_ref_settings(
        user_guid: str,
        length: int,
        country_id: int = 2,
        target_driver_rides: int = 1,
        target_rider_rides: int = 1,
):
    return experiments_utils.get_referral_settings_exp(
        title_tk='referral.title',
        description=[{'tanker_key': 'referral.text'}],
        app_link='abracadabra',
        sharing_message_tk='referral.sharing_message',
        code_length=length,
        user_guid=user_guid,
        country_id=country_id,
        target_driver_rides=target_driver_rides,
        target_rider_rides=target_rider_rides,
    )


def _get_token(user_guid: str) -> str:
    return f'{user_guid}-token'


async def _insert_user_login_attempts(
        web_context, user_data: List[Tuple[str, str]],
):
    values = [
        f'(\'{user[1]}\', \'{_get_token(user[0])}\', \'0000\', \'1\')'
        for user in user_data
    ]
    async with web_context.pg.ro_pool.acquire() as conn:
        query = (
            'INSERT INTO user_login_attempt '
            '(msisdn, token, sms_code, sms_verified) VALUES'
        )
        query += ','.join(values)
        await conn.execute(query)


def _translations(show_numbers: bool = False):
    numbers_description = (
        ' {invited_riders_count} {invited_drivers_count}'
        ' {invited_users_wo_action}'
        ' {rider_target_rides} {driver_target_orders}'
        ' {money_for_rider} {money_for_driver}'
    )
    return pytest.mark.translations(
        rida={
            'referral.title': {'en': 'Referral program title'},
            'referral.text': {
                'en': (
                    'suggest our app and get some dough. '
                    'Your code: {refcode}'
                    + (numbers_description if show_numbers else '')
                ),
            },
            'referral.sharing_message': {
                'en': 'hey buddy, check out this app {app_link}',
            },
            'referral.non_existing_refcode_error': {
                'en': 'dont even try to duck with me',
            },
            'referral.repeated_code_set': {'en': 'slysh tu umnik herov'},
        },
    )


async def _get_description(taxi_rida_web, user_id: int = 1234):
    return await taxi_rida_web.get(
        '/v1/referral/description',
        headers=helpers.get_auth_headers(user_id=user_id),
    )


async def _post_code(
        taxi_rida_web, code: str, user_guid: str = _USER_GUIDS[0],
):
    return await taxi_rida_web.post(
        '/v1/referral/code',
        headers={'Authorization': f'Bearer: {_get_token(user_guid)}'},
        json={'code': code},
    )


@_get_ref_settings(_USER_GUIDS[0], 4)
@_get_ref_settings(_USER_GUIDS[1], 4)
@_translations()
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_patch.sql'])
async def test_referral_description(taxi_rida_web):
    codes = set()
    user_ids = [1234, 5678]
    for _ in range(2):
        for user_id in user_ids:
            response = await _get_description(taxi_rida_web, user_id)
            assert response.status == 200
            data = await response.json()
            code = data['refcode']

            assert data['title'] == 'Referral program title'
            assert data['description'] == [
                {
                    'type': 1,
                    'data': {
                        'text': (
                            'suggest our app and get some dough. '
                            f'Your code: {code}'
                        ),
                        'color': '#000000',
                    },
                },
            ]
            assert (
                data['sharing_message']
                == 'hey buddy, check out this app abracadabra'
            )
            assert len(code) == 4
            codes.add(code)

    assert len(codes) == len(user_ids)


@_get_ref_settings(_USER_GUIDS[0], 0)
@_get_ref_settings(_USER_GUIDS[1], 0)
@_translations()
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_patch.sql'])
async def test_referral_collision(taxi_rida_web):
    response = await _get_description(taxi_rida_web)
    assert response.status == 200

    response = await _get_description(taxi_rida_web, user_id=5678)
    assert response.status == 500


@pytest.mark.parametrize(
    'corrupt_refcode, expected_response',
    [
        pytest.param(None, 200, id='good refcode'),
        pytest.param('lower', 200, id='case insensitivity test'),
        pytest.param('upper', 200, id='case insensitivity test2'),
        pytest.param('change_symbol', 404, id='change symbol'),
        pytest.param('empty', 400, id='empty refcode'),
    ],
)
@_get_ref_settings(_USER_GUIDS[0], 4)
@_translations()
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_patch.sql'])
async def test_referral_set(
        web_app_client,
        web_context,
        corrupt_refcode: Optional[str],
        expected_response: int,
):
    await _insert_user_login_attempts(web_context, _USER_DATA)
    response = await _get_description(web_app_client)
    code = (await response.json())['refcode']
    if corrupt_refcode == 'change_symbol':
        new_code = 'H' if code[0] != 'H' else 'U' + code[1:]
    elif corrupt_refcode == 'empty':
        new_code = ''
    elif corrupt_refcode == 'lower':
        new_code = code.lower()
    elif corrupt_refcode == 'upper':
        new_code = code.upper()
    else:
        new_code = code

    response = await _post_code(web_app_client, new_code)

    assert response.status == expected_response
    if expected_response == 200:
        async with web_context.pg.ro_pool.acquire() as conn:
            record = await conn.fetchrow(
                f'SELECT parent_referral_code FROM users '
                f'WHERE guid=\'{_USER_GUIDS[0]}\'',
            )
            assert record['parent_referral_code'] == code
    elif expected_response == 404:
        assert (await response.json())[
            'message'
        ] == 'dont even try to duck with me'


@_get_ref_settings(_USER_GUIDS[0], 4)
@_get_ref_settings(_USER_GUIDS[1], 4)
@_translations()
@pytest.mark.parametrize(
    'is_same_code, expected_code',
    [
        pytest.param(False, 400, id='trying to set another code'),
        pytest.param(True, 200, id='retrying with the same code'),
    ],
)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_patch.sql'])
async def test_referral_set_second_time(
        web_app_client, web_context, is_same_code: bool, expected_code: int,
):
    await _insert_user_login_attempts(web_context, _USER_DATA)
    response = await _get_description(web_app_client)
    code0 = (await response.json())['refcode']
    response = await _get_description(
        web_app_client, user_id=1234 if is_same_code else 5678,
    )
    code1 = (await response.json())['refcode']

    response = await _post_code(web_app_client, code0)
    assert response.status == 200

    response = await _post_code(web_app_client, code1)
    assert response.status == expected_code
    if expected_code == 400:
        assert (await response.json())['message'] == 'slysh tu umnik herov'


@_get_ref_settings(_USER_GUIDS[0], 4)
@_translations()
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_patch.sql'])
async def test_referral_authentication(taxi_rida_web):
    response = await _get_description(taxi_rida_web)
    code = (await response.json())['refcode']
    response = await taxi_rida_web.post(
        '/v1/referral/code',
        headers={'Authorization': f'Bearer: AAA'},
        json={'code': code},
    )
    assert response.status == 401

    response = await taxi_rida_web.post(
        '/v1/referral/code',
        headers=helpers.get_auth_headers(1234),
        json={'code': code},
    )
    assert response.status == 401

    response = await taxi_rida_web.post(
        '/v1/referral/code', json={'code': code},
    )
    assert response.status == 401


@_get_ref_settings(
    _USER_GUIDS[0], 4, target_rider_rides=2, target_driver_rides=2,
)
@_translations(show_numbers=True)
@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_patch.sql'])
async def test_referral_description_with_numbers(web_app_client, web_context):

    drivers = [
        (1449, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', 2),
        (3457, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q', 2),
        (1450, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5Z', 1),
    ]
    riders = [
        ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', 2),
        ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5Q', 2),
        ('9373F48B-C6B4-4812-A2D0-413F3AFBAD5J', 0),
    ]

    response = await _get_description(web_app_client, 1234)
    assert response.status == 200
    data = await response.json()
    code = data['refcode']

    async with web_context.pg.rw_pool.acquire() as conn:
        all_guids = [x[1] for x in drivers] + [x[0] for x in riders]
        all_guids = ','.join(['\'' + guid + '\'' for guid in all_guids])
        await conn.execute(
            f'UPDATE users SET parent_referral_code=\'{code}\' '
            f'WHERE guid in ({all_guids})',
        )
        for driver in drivers:
            await conn.execute(
                f'UPDATE drivers set number_of_trips={driver[2]} '
                f'WHERE driver_id={driver[0]}',
            )
        for rider in riders:
            await conn.execute(
                f'UPDATE users set number_of_trips={rider[1]} '
                f'WHERE guid=\'{rider[0]}\'',
            )

    response = await _get_description(web_app_client, 1234)
    assert response.status == 200
    data = await response.json()
    assert data['description'] == [
        {
            'type': 1,
            'data': {
                'text': (
                    'suggest our app and get some dough. '
                    f'Your code: {code} '
                    '2 2 2 2 2 1000$ 2000$'  # see numbers_description
                    # from @_translations
                ),
                'color': '#000000',
            },
        },
    ]
