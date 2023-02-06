import http

import pytest

from test_eats_tips_partners import conftest


NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'not found'}


def _partner_by_alias(user_id, roles, confirmed, show_in_menu, alias=None):
    response = {
        'partner_id': f'00000000-0000-0000-0000-{user_id.zfill(12)}',
        'roles': roles,
        'confirmed': confirmed,
        'show_in_menu': show_in_menu,
    }
    if alias:
        response['alias'] = alias
    return response


@pytest.mark.parametrize(
    ('partners_ids', 'expected_code', 'expected_response'),
    (
        pytest.param(
            '00000000-0000-0000-0000-000000000011',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias(
                                '11', ['recipient'], True, False, '0000110',
                            ),
                        ],
                    },
                ],
            },
            id='partner-with-1-place',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000100',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias('100', ['admin'], True, False),
                        ],
                    },
                ],
            },
            id='partner-admin',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000010',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias(
                                '10', ['recipient'], True, True, '0000100',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PLACE_106,
                        'partners': [
                            _partner_by_alias(
                                '10', ['recipient'], True, False, '0000100',
                            ),
                        ],
                    },
                ],
            },
            id='partner-with-more-than-1-place',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000018',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_104,
                        'partners': [
                            _partner_by_alias(
                                '18', ['recipient'], True, False, '0000180',
                            ),
                        ],
                    },
                    {
                        'info': conftest.place_by_alias('105', '', None),
                        'partners': [
                            _partner_by_alias(
                                '18', ['recipient'], False, True, '0000180',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PLACE_106,
                        'partners': [
                            _partner_by_alias(
                                '18',
                                ['admin', 'unknown'],
                                True,
                                False,
                                '0000180',
                            ),
                        ],
                    },
                ],
            },
            id='partner-with-more-than-1-place-2',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000011,'
            '00000000-0000-0000-0000-000000000011',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias(
                                '11', ['recipient'], True, False, '0000110',
                            ),
                        ],
                    },
                ],
            },
            id='same-partner-2-times',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000012,'
            '00000000-0000-0000-0000-000000000013',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias(
                                '12', ['recipient'], False, True, '0000120',
                            ),
                            _partner_by_alias(
                                '13', ['recipient'], False, False, '0000130',
                            ),
                        ],
                    },
                ],
            },
            id='few-partners-in-same-place',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000102,'
            '00000000-0000-0000-0000-000000000104',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.place_by_alias(
                            '102', 'Сам себе ресторан', None,
                        ),
                        'partners': [
                            _partner_by_alias('102', ['admin'], True, False),
                        ],
                    },
                    {
                        'info': conftest.PLACE_104,
                        'partners': [
                            _partner_by_alias('104', ['admin'], False, True),
                        ],
                    },
                ],
            },
            id='few-partners-in-different-places',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000010,'
            '00000000-0000-0000-0000-000000000016',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias(
                                '10', ['recipient'], True, True, '0000100',
                            ),
                            _partner_by_alias(
                                '16', ['recipient'], True, False, '0000160',
                            ),
                        ],
                    },
                    {
                        'info': conftest.PLACE_106,
                        'partners': [
                            _partner_by_alias(
                                '10', ['recipient'], True, False, '0000100',
                            ),
                        ],
                    },
                ],
            },
            id='few-partners-in-same-and-different-places',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000017,'
            '00000000-0000-0000-0000-000000000019',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='few-partners-with-no-place',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000017',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='partner-without-places',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000000',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='partner-not-exist',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000103',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='deleted-partner',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000020',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias(
                                '20', ['recipient'], True, False, '0000200',
                            ),
                        ],
                    },
                ],
            },
            id='no-mysql-id',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000020,'
            '00000000-0000-0000-0000-000000000021',
            http.HTTPStatus.OK,
            {
                'places': [
                    {
                        'info': conftest.PLACE_100,
                        'partners': [
                            _partner_by_alias(
                                '20', ['recipient'], True, False, '0000200',
                            ),
                            _partner_by_alias(
                                '21', ['recipient'], True, False, '0000210',
                            ),
                        ],
                    },
                ],
            },
            id='no-mysql-id-2',
        ),
        pytest.param(
            'blah-blah-blah',
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'partner_id is not UUID'},
            id='invalid-uuid',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_places_list_get(
        taxi_eats_tips_partners_web,
        mockserver,
        mock_tvm_rules,
        partners_ids,
        expected_code,
        expected_response,
):
    response = await taxi_eats_tips_partners_web.get(
        '/v1/place/list', params={'partners_ids': partners_ids},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
