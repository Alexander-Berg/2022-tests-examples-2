# pylint: disable=unused-variable
import typing

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as test_http

from test_eats_tips_payments import conftest

PLACE_ID_1 = 'eef266b2-09b3-4218-8da9-c90928608d97'
PLACE_ID_2 = '2236ecf3-2cad-4e19-ac18-cfea5c3f8b99'

PARTNER_ID_1 = 'f907a11d-e1aa-4b2e-8253-069c58801727'
PARTNER_ID_2 = '88dce9e6-dff7-4930-8d26-bca7065a68ec'
PARTNER_ID_3 = 'de73ab55-742d-473e-a8d5-382d9dc8024a'
PARTNER_ID_4 = '96efec77-fcd3-40fa-9251-d6b1349f6fcc'
PARTNER_ID_5 = 'f529561b-b713-4f06-a3a0-7b8d1de88095'
PARTNER_ID_6 = 'f529561b-b713-4f06-a3a0-7b8d1de88096'
PARTNER_ID_7 = 'f529561b-b713-4f06-a3a0-7b8d1de88097'
PARTNER_ID_8 = 'f529561b-b713-4f06-a3a0-7b8d1de88098'


def _format_request_params(*, alias='alias'):
    return {'qr': alias}


def _format_recipient(
        *,
        name,
        photo,
        user_id,
        saving_up_for,
        recipient_id,
        recipient_type,
        place_id,
        alias,
        registration_date=None,
):
    result = {
        'name': name,
        'photo': photo,
        'user_id': user_id,
        'saving_up_for': saving_up_for,
        'recipient_id': recipient_id,
        'recipient_type': recipient_type,
        'alias_to_redirect': alias,
    }
    if registration_date:
        result['registration_date'] = registration_date
    if place_id:
        result['place_id'] = place_id
    return result


def _format_expected_response(alias, place_id, recipients):
    if place_id:
        return {'alias': alias, 'place_id': place_id, 'waiters': recipients}
    return {'alias': alias, 'waiters': recipients}


def make_pytest_param(
        *,
        id,  # pylint: disable=redefined-builtin, invalid-name
        params: typing.Any = conftest.SENTINEL,
        expected_status: typing.Any = conftest.SENTINEL,
        expected_response: typing.Any = conftest.SENTINEL,
):
    return pytest.param(
        conftest.value_or_default(params, _format_request_params()),
        conftest.value_or_default(expected_status, 200),
        conftest.value_or_default(expected_response, None),
        id=id,
    )


@pytest.fixture
async def _mock_eats_tips_partners(mock_eats_tips_partners):
    def _format_partner_place(
            *, place_id, roles, confirmed=True, show_in_menu=True, alias=None,
    ):
        return {
            'place_id': place_id,
            'confirmed': confirmed,
            'show_in_menu': show_in_menu,
            'roles': roles,
            'alias': alias,
            'address': '',
            'title': '',
        }

    def _format_partner(
            *,
            partner_id,
            mysql_id,
            display_name,
            photo='',
            saving_up_for='',
            blocked=False,
    ):
        return {
            'id': partner_id,
            'mysql_id': mysql_id,
            'display_name': display_name,
            'photo': photo,
            'full_name': 'ФИО',
            'phone_id': '',
            'saving_up_for': saving_up_for,
            'registration_date': '2022-01-18T00:00:00+00:00',
            'is_vip': True,
            'blocked': blocked,
            'best2pay_blocked': False,
        }

    # pylint: disable=inconsistent-return-statements
    @mock_eats_tips_partners('/v1/alias-to-object')
    def mock_v1_alias_to_object(request: test_http.Request):
        alias = request.query['alias']
        if alias == '0000010':
            return web.json_response(
                {
                    'partner': _format_partner(
                        partner_id=PARTNER_ID_1,
                        mysql_id='1',
                        display_name='Партнёр 1',
                        photo='photo1',
                        saving_up_for='почку',
                    ),
                    'place': {'id': PLACE_ID_1, 'title': 'Заведение 1'},
                },
                status=200,
            )
        if alias == '0000030':
            return web.json_response(
                {'place': {'id': PLACE_ID_2, 'title': 'Заведение 2'}},
                status=200,
            )
        if alias == '0000050':
            return web.json_response(
                {
                    'partner': _format_partner(
                        partner_id=PARTNER_ID_5,
                        mysql_id='5',
                        display_name='Партнёр 5 (без заведения)',
                    ),
                },
                status=200,
            )
        if alias == '0000060':
            return web.json_response(
                {
                    'money_box': {
                        'id': '',
                        'place_id': PLACE_ID_1,
                        'fallback_partner_id': '',
                        'display_name': 'Копилка',
                        'alias': '0000060',
                        'pay_url': '',
                        'caption': 'На корпоратив',
                        'avatar': 'test_avatar',
                        'registration_date': '2022-01-18T00:00:00+00:00',
                    },
                },
                status=200,
            )
        if alias == '0100500':
            return web.json_response({'code': '', 'message': ''}, status=404)
        assert False, f'unexpected alias: {alias}'

    @mock_eats_tips_partners('/v1/partner/list')
    def mock_v1_partner_list(request: test_http.Request):
        places_ids = request.query['places_ids']
        partners = []
        if PLACE_ID_2 in places_ids:
            partners.append(
                {
                    'info': _format_partner(
                        partner_id=PARTNER_ID_3,
                        mysql_id='3',
                        display_name='Партнёр 3',
                    ),
                    'places': [
                        _format_partner_place(
                            place_id=PLACE_ID_2,
                            roles=['recipient'],
                            alias='3000230',
                        ),
                    ],
                },
            )
            partners.append(
                {
                    'info': _format_partner(
                        partner_id=PARTNER_ID_4,
                        mysql_id='4',
                        display_name='Партнёр 4',
                    ),
                    'places': [
                        _format_partner_place(
                            place_id=PLACE_ID_2,
                            roles=['recipient'],
                            alias='3000240',
                        ),
                    ],
                },
            )
            partners.append(
                {
                    'info': _format_partner(
                        partner_id=PARTNER_ID_6,
                        mysql_id='4',
                        display_name='Партнёр 6',
                    ),
                    'places': [
                        _format_partner_place(
                            place_id=PLACE_ID_2,
                            roles=['admin'],
                            alias='3000260',
                        ),
                    ],
                },
            )
            partners.append(
                {
                    'info': _format_partner(
                        partner_id=PARTNER_ID_7,
                        mysql_id='4',
                        display_name='Партнёр 7 (не отображается)',
                    ),
                    'places': [
                        _format_partner_place(
                            place_id=PLACE_ID_2,
                            roles=['recipient'],
                            show_in_menu=False,
                            alias='3000270',
                        ),
                    ],
                },
            )
            partners.append(
                {
                    'info': _format_partner(
                        partner_id=PARTNER_ID_8,
                        mysql_id='4',
                        display_name='Партнёр 8 (админ и получатель)',
                    ),
                    'places': [
                        _format_partner_place(
                            place_id=PLACE_ID_2,
                            roles=['admin', 'recipient'],
                            alias='3000280',
                        ),
                    ],
                },
            )
        else:
            assert False, f'unexpected place_ids: {places_ids}'
        return web.json_response(
            {'partners': partners, 'has_more': False}, status=200,
        )

    @mock_eats_tips_partners('/v1/money-box/list')
    def mock_v1_money_box_list(request: test_http.Request):
        return {'boxes': []}


@pytest.mark.parametrize(
    'request_params,expected_status,expected_response',
    [
        make_pytest_param(
            params=_format_request_params(alias='000010'),
            expected_status=200,
            expected_response=_format_expected_response(
                '0000010',
                PLACE_ID_1,
                [
                    _format_recipient(
                        name='Партнёр 1',
                        photo='photo1',
                        user_id='000010',
                        alias='0000010',
                        saving_up_for='Коплю на почку',
                        recipient_id=PARTNER_ID_1,
                        place_id=PLACE_ID_1,
                        recipient_type='partner',
                    ),
                ],
            ),
            id='success',
        ),
        make_pytest_param(
            params=_format_request_params(alias='000030'),
            expected_status=200,
            expected_response=_format_expected_response(
                '0000030',
                PLACE_ID_2,
                [
                    _format_recipient(
                        name='Партнёр 3',
                        photo='',
                        user_id='000030',
                        alias='3000230',
                        saving_up_for='',
                        recipient_id=PARTNER_ID_3,
                        place_id=PLACE_ID_2,
                        recipient_type='partner',
                    ),
                    _format_recipient(
                        name='Партнёр 4',
                        photo='',
                        user_id='000040',
                        alias='3000240',
                        saving_up_for='',
                        recipient_id=PARTNER_ID_4,
                        place_id=PLACE_ID_2,
                        recipient_type='partner',
                    ),
                    _format_recipient(
                        name='Партнёр 8 (админ и получатель)',
                        photo='',
                        user_id='000040',
                        alias='3000280',
                        saving_up_for='',
                        recipient_id=PARTNER_ID_8,
                        place_id=PLACE_ID_2,
                        recipient_type='partner',
                    ),
                ],
            ),
            id='multiple recipients',
        ),
        make_pytest_param(
            params=_format_request_params(alias='000050'),
            expected_status=200,
            expected_response=_format_expected_response(
                '0000050',
                None,
                [
                    _format_recipient(
                        name='Партнёр 5 (без заведения)',
                        photo='',
                        user_id='000050',
                        alias='0000050',
                        saving_up_for='',
                        recipient_id=PARTNER_ID_5,
                        place_id=None,
                        recipient_type='partner',
                    ),
                ],
            ),
            id='recipient without place',
        ),
        make_pytest_param(
            params=_format_request_params(alias='100500'),
            expected_status=404,
            expected_response={
                'code': 'not_found',
                'message': 'recipients are not found',
            },
            id='recipients are not found',
        ),
        make_pytest_param(
            params=_format_request_params(alias='000060'),
            expected_status=200,
            expected_response=_format_expected_response(
                '0000060',
                PLACE_ID_1,
                [
                    _format_recipient(
                        name='Копилка',
                        photo='test_avatar',
                        recipient_id='',
                        recipient_type='money_box',
                        user_id='',
                        alias='0000060',
                        place_id=PLACE_ID_1,
                        saving_up_for='На корпоратив',
                    ),
                ],
            ),
            id='money box success',
        ),
    ],
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
async def test_get_waiter(
        taxi_eats_tips_payments_web,
        _mock_eats_tips_partners,
        # params:
        request_params,
        expected_status,
        expected_response,
):
    response = await taxi_eats_tips_payments_web.get(
        '/v1/users/waiters', params=request_params,
    )
    assert response.status == expected_status
    assert await response.json() == expected_response
