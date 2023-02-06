import http

import pytest

NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'not found'}


@pytest.mark.parametrize(
    ('place_id', 'expected_code', 'expected_response'),
    (
        pytest.param(
            '10000000-0000-0000-0000-000000000100',
            http.HTTPStatus.OK,
            {
                'id': '10000000-0000-0000-0000-000000000100',
                'title': 'Деревня Вилларибо',
                'alias': '0001000',
                'photo': 'фото_ресторана',
                'mysql_id': '100',
                'brand_id': '99999999-0000-0000-0000-000000000001',
                'brand_slug': 'shoko',
            },
            id='ok-place',
        ),
        pytest.param(
            '10000000-0000-0000-0000-000000999999',
            http.HTTPStatus.NOT_FOUND,
            NOT_FOUND_RESPONSE,
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_partners_get(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        place_id,
        expected_code,
        expected_response,
):
    response = await taxi_eats_tips_partners_web.get(
        '/v1/place', params={'place_id': place_id},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
