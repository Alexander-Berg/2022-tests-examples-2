import http

import pytest

from test_eats_tips_partners import conftest


NOT_FOUND_RESPONSE = {'code': 'not_found', 'message': 'not found'}


@pytest.mark.parametrize(
    ('partner_id', 'expected_code', 'expected_response'),
    (
        pytest.param(
            '00000000-0000-0000-0000-000000000010',
            http.HTTPStatus.OK,
            conftest.PARTNERS['10'],
            id='ok-recipient',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000011',
            http.HTTPStatus.OK,
            conftest.PARTNERS['11'],
            id='ok-recipient-with-photo',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000018',
            http.HTTPStatus.OK,
            conftest.PARTNERS['18'],
            id='no-data-in-mysql',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000100',
            http.HTTPStatus.OK,
            conftest.PARTNERS['100'],
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
            conftest.PARTNERS['20'],
            id='no-mysql-id',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000022',
            http.HTTPStatus.OK,
            conftest.PARTNERS['22'],
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
async def test_partner_get(
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
        '/v1/partner', params={'partner_id': partner_id},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
