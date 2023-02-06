import http

import pytest

from test_eats_tips_partners import conftest


NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'partner not found'}
PLACE_ADDRESS = {'106': 'ул. Пушкина, д. Колотушкина'}


def _create_place(
        mysql_id,
        confirmed,
        show_in_menu,
        roles,
        alias=None,
        brand_id=None,
        brand_slug=None,
):
    result = {
        'address': PLACE_ADDRESS.get(mysql_id, ''),
        'confirmed': confirmed,
        'place_id': f'10000000-0000-0000-0000-{mysql_id.zfill(12)}',
        'roles': roles,
        'show_in_menu': show_in_menu,
        'title': conftest.PARTNERS[mysql_id]['full_name'],
        'mysql_id': mysql_id,
    }
    if brand_id is not None:
        result['brand_id'] = brand_id
    if brand_slug is not None:
        result['brand_slug'] = brand_slug
    if conftest.PARTNERS[mysql_id].get('photo') is not None:
        result['photo'] = conftest.PARTNERS[mysql_id]['photo']
    if alias:
        result['alias'] = alias
    return result


@pytest.mark.parametrize(
    ('partner_id', 'expected_code', 'expected_response'),
    (
        pytest.param(
            '00000000-0000-0000-0000-000000000010',
            http.HTTPStatus.OK,
            {
                'info': conftest.PARTNERS['10'],
                'places': [
                    _create_place(
                        '100',
                        True,
                        True,
                        ['recipient'],
                        alias='0000100',
                        brand_id='99999999-0000-0000-0000-000000000001',
                        brand_slug='shoko',
                    ),
                    _create_place(
                        '106', True, False, ['recipient'], alias='0000100',
                    ),
                ],
            },
            id='ok-recipient',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000011',
            http.HTTPStatus.OK,
            {
                'info': conftest.PARTNERS['11'],
                'places': [
                    _create_place(
                        '100',
                        True,
                        False,
                        ['recipient'],
                        alias='0000110',
                        brand_id='99999999-0000-0000-0000-000000000001',
                        brand_slug='shoko',
                    ),
                ],
            },
            id='ok-recipient-with-photo',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000018',
            http.HTTPStatus.OK,
            {
                'info': conftest.PARTNERS['18'],
                'places': [
                    _create_place(
                        '104', True, False, ['recipient'], alias='0000180',
                    ),
                    _create_place(
                        '105', False, True, ['recipient'], alias='0000180',
                    ),
                    _create_place(
                        '106',
                        True,
                        False,
                        ['admin', 'unknown'],
                        alias='0000180',
                    ),
                ],
            },
            id='no-data-in-mysql',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000100',
            http.HTTPStatus.OK,
            {
                'info': conftest.PARTNERS['100'],
                'places': [
                    _create_place(
                        '100',
                        True,
                        False,
                        ['admin'],
                        brand_id='99999999-0000-0000-0000-000000000001',
                        brand_slug='shoko',
                    ),
                ],
            },
            id='ok-admin',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000000',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-found',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000024',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='deleted-partner',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000020',
            http.HTTPStatus.OK,
            {
                'info': conftest.PARTNERS['20'],
                'places': [
                    _create_place(
                        '100',
                        True,
                        False,
                        ['recipient'],
                        alias='0000200',
                        brand_id='99999999-0000-0000-0000-000000000001',
                        brand_slug='shoko',
                    ),
                ],
            },
            id='no-mysql-id',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000022',
            http.HTTPStatus.OK,
            {
                'info': conftest.PARTNERS['22'],
                'places': [
                    _create_place(
                        '100',
                        True,
                        False,
                        ['recipient'],
                        alias='0000220',
                        brand_id='99999999-0000-0000-0000-000000000001',
                        brand_slug='shoko',
                    ),
                ],
            },
            id='no-display-name',
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
async def test_v2_partner_get(
        taxi_eats_tips_partners_web,
        mockserver,
        mock_tvm_rules,
        partner_id,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_phones_store(request):
        return {'value': request.json['value'], 'id': '123456'}

    response = await taxi_eats_tips_partners_web.get(
        '/v2/partner', params={'partner_id': partner_id},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
