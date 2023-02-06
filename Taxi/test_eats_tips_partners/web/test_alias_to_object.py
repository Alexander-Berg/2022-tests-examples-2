import http

import pytest

from test_eats_tips_partners import conftest


NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'not found'}


@pytest.mark.parametrize(
    ('alias', 'expected_code', 'expected_response'),
    (
        pytest.param(
            '0000170',
            http.HTTPStatus.OK,
            {'type': 'partner', 'partner': conftest.PARTNERS['17']},
            id='partner-without-attributes',
        ),
        pytest.param(
            '0000230',
            http.HTTPStatus.OK,
            {'type': 'partner', 'partner': conftest.PARTNERS['23']},
            id='partner-with-attributes',
        ),
        pytest.param(
            '0001000',
            http.HTTPStatus.OK,
            {'type': 'place', 'place': conftest.PLACE_100},
            id='place',
        ),
        pytest.param(
            '0001070',
            http.HTTPStatus.OK,
            {'type': 'place', 'place': conftest.PLACE_107},
            id='place-without-attributes',
        ),
        pytest.param(
            '0000100',
            http.HTTPStatus.OK,
            {
                'type': 'place_partner',
                'partner': conftest.PARTNERS['10'],
                'place': conftest.PLACE_100,
            },
            id='partner-and-place_partner',
        ),
        pytest.param(
            '0000110',
            http.HTTPStatus.OK,
            {'type': 'partner', 'partner': conftest.PARTNERS['11']},
            id='alias-with-partner-type',
        ),
        pytest.param(
            '0000120',
            http.HTTPStatus.OK,
            {
                'type': 'place_partner',
                'partner': conftest.PARTNERS['12'],
                'place': conftest.PLACE_100,
            },
            id='alias-with-place_partner-type',
        ),
        pytest.param(
            '0001060',
            http.HTTPStatus.OK,
            {'type': 'place', 'place': conftest.PLACE_106},
            id='alias-with-place-type',
        ),
        pytest.param(
            '0001020',
            http.HTTPStatus.OK,
            {'type': 'place', 'place': conftest.PLACE_102},
            id='alias-with-place-type-2',
        ),
        pytest.param(
            '0001010',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='deleted-place',
        ),
        pytest.param(
            '0000240',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='deleted-partner',
        ),
        pytest.param('1000', http.HTTPStatus.NOT_FOUND, NOT_FOUND_RESPONSE),
        pytest.param(
            '0004040',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-exists',
        ),
        pytest.param(
            'blahblahblah',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='invalid-alias',
        ),
        pytest.param(
            '',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='empty-alias',
        ),
        pytest.param(
            '0000260',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='deleted-alias',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_alias_to_object_get(
        taxi_eats_tips_partners_web,
        mockserver,
        mock_tvm_rules,
        pgsql,
        alias,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_phones_store(request):
        return {'value': request.json['value'], 'id': '123456'}

    response = await taxi_eats_tips_partners_web.get(
        '/v1/alias-to-object', params={'alias': alias},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if response.status != http.HTTPStatus.OK:
        return
    cursor = pgsql['eats_tips_partners'].cursor()
    cursor.execute(
        f"""
            SELECT type
            FROM eats_tips_partners.alias
            WHERE alias = '{alias}'
            ;
        """,
    )
    assert cursor.fetchone()[0] == expected_response['type']
