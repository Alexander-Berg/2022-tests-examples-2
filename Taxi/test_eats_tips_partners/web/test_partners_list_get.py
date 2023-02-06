import http

import pytest

from test_eats_tips_partners import conftest


NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'not found'}
ADDRESS_106 = 'ул. Пушкина, д. Колотушкина'


def _create_place(
        place_id, roles, confirmed, show_in_menu, alias=None, address='',
):
    result = {
        'confirmed': confirmed,
        'place_id': f'10000000-0000-0000-0000-{place_id.zfill(12)}',
        'roles': roles,
        'show_in_menu': show_in_menu,
        'title': conftest.PARTNERS[place_id]['full_name'],
        'address': address,
        'mysql_id': place_id,
    }
    if alias:
        result['alias'] = alias
    if conftest.PARTNERS[place_id].get('photo'):
        result['photo'] = conftest.PARTNERS[place_id]['photo']
    return result


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            {'places_ids': '10000000-0000-0000-0000-000000000000'},
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-found-place',
        ),
        pytest.param(
            {'places_ids': '10000000-0000-0000-0000-000000000100'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'partners': [
                    {
                        'info': conftest.PARTNERS['10'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], True, True, '0000100',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['11'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], True, False, '0000110',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['12'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], False, True, '0000120',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['13'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], False, False, '0000130',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['15'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], True, False, '0000150',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['16'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], True, False, '0000160',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['20'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], True, False, '0000200',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['21'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], True, False, '0000210',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['22'],
                        'places': [
                            _create_place(
                                '100', ['recipient'], True, False, '0000220',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['700'],
                        'places': [
                            _create_place('100', ['admin'], True, True),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['100'],
                        'places': [
                            _create_place('100', ['admin'], True, False),
                        ],
                    },
                ],
            },
            id='correct-place',
        ),
        pytest.param(
            {'places_ids': '10000000-0000-0000-0000-000000000101'},
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='deleted-place',
        ),
        pytest.param(
            {'places_ids': '10000000-0000-0000-0000-000000000102'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'partners': [
                    {
                        'info': conftest.PARTNERS['102'],
                        'places': [
                            _create_place('102', ['admin'], True, False),
                        ],
                    },
                ],
            },
            id='place-with-only-admin',
        ),
        pytest.param(
            {'places_ids': '10000000-0000-0000-0000-000000000103'},
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='place-with-no-members',
        ),
        pytest.param(
            {
                'places_ids': (
                    '10000000-0000-0000-0000-000000000104,'
                    '10000000-0000-0000-0000-000000000105'
                ),
            },
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'partners': [
                    {
                        'info': conftest.PARTNERS['18'],
                        'places': [
                            _create_place(
                                '104', ['recipient'], True, False, '0000180',
                            ),
                            _create_place(
                                '105', ['recipient'], False, True, '0000180',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['104'],
                        'places': [
                            _create_place('104', ['admin'], False, True),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['105'],
                        'places': [
                            _create_place('105', ['admin'], False, True),
                        ],
                    },
                ],
            },
            id='few-places',
        ),
        pytest.param(
            {
                'places_ids': (
                    '10000000-0000-0000-0000-000000000105,'
                    '10000000-0000-0000-0000-000000000106'
                ),
            },
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'partners': [
                    {
                        'info': conftest.PARTNERS['10'],
                        'places': [
                            _create_place(
                                '106',
                                ['recipient'],
                                True,
                                False,
                                '0000100',
                                ADDRESS_106,
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['18'],
                        'places': [
                            _create_place(
                                '105', ['recipient'], False, True, '0000180',
                            ),
                            _create_place(
                                '106',
                                ['admin', 'unknown'],
                                True,
                                False,
                                '0000180',
                                ADDRESS_106,
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['105'],
                        'places': [
                            _create_place('105', ['admin'], False, True),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['106'],
                        'places': [
                            _create_place(
                                '106',
                                ['admin', 'recipient'],
                                False,
                                True,
                                '0001060',
                                address=ADDRESS_106,
                            ),
                        ],
                    },
                ],
            },
            id='partners-in-different-roles-in-different-places',
        ),
        pytest.param(
            {'places_ids': '10000000-0000-0000-0000-000000000106'},
            http.HTTPStatus.OK,
            {
                'has_more': False,
                'partners': [
                    {
                        'info': conftest.PARTNERS['10'],
                        'places': [
                            _create_place(
                                '106',
                                ['recipient'],
                                True,
                                False,
                                '0000100',
                                ADDRESS_106,
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['18'],
                        'places': [
                            _create_place(
                                '106',
                                ['admin', 'unknown'],
                                True,
                                False,
                                '0000180',
                                ADDRESS_106,
                            ),
                        ],
                    },
                    {
                        'info': conftest.PARTNERS['106'],
                        'places': [
                            _create_place(
                                '106',
                                ['admin', 'recipient'],
                                False,
                                True,
                                '0001060',
                                address=ADDRESS_106,
                            ),
                        ],
                    },
                ],
            },
            id='another-ok',
        ),
        pytest.param(
            {'places_ids': '10000000-0000-0000-0000-000000000106', 'limit': 1},
            http.HTTPStatus.OK,
            {
                'has_more': True,
                'partners': [
                    {
                        'info': conftest.PARTNERS['10'],
                        'places': [
                            _create_place(
                                '106',
                                ['recipient'],
                                True,
                                False,
                                '0000100',
                                ADDRESS_106,
                            ),
                        ],
                    },
                ],
            },
            id='limit-1-offset-0',
        ),
        pytest.param(
            {
                'places_ids': '10000000-0000-0000-0000-000000000106',
                'limit': 1,
                'offset': 1,
            },
            http.HTTPStatus.OK,
            {
                'has_more': True,
                'partners': [
                    {
                        'info': conftest.PARTNERS['18'],
                        'places': [
                            _create_place(
                                '106',
                                ['admin', 'unknown'],
                                True,
                                False,
                                '0000180',
                                ADDRESS_106,
                            ),
                        ],
                    },
                ],
            },
            id='limit-1-offset-1',
        ),
        pytest.param(
            {'places_ids': 'blah-blah-blah'},
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'bad place_id format'},
            id='invalid-uuid',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_partners_list_get(
        taxi_eats_tips_partners_web,
        mockserver,
        mock_tvm_rules,
        params,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_phones_bulk_store(request):
        return {
            'items': [
                {'value': item['value'], 'id': '123456'}
                for item in request.json['items']
            ],
        }

    response = await taxi_eats_tips_partners_web.get(
        '/v1/partner/list', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
