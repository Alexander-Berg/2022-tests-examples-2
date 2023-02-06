import http

import pytest


NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'partner not found'}


@pytest.mark.parametrize(
    ('alias', 'expected_status', 'expected_response'),
    (
        pytest.param(
            '100500',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-found',
        ),
        pytest.param(
            '50',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-found-in-pg',
        ),
        pytest.param(
            '51',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-found-in-pg',
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
            '100',
            http.HTTPStatus.OK,
            {'alias': '100', 'id': '00000000-0000-0000-0000-000000000100'},
            id='ok',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
@pytest.mark.now('2022-05-25T14:43:34+03:00')
async def test_partner_alias_to_id_get(
        taxi_eats_tips_partners_web, alias, expected_status, expected_response,
):
    response = await taxi_eats_tips_partners_web.get(
        '/v1/partner/alias-to-id', params={'alias': alias},
    )
    assert response.status == expected_status
    body = await response.json()
    assert body == expected_response
