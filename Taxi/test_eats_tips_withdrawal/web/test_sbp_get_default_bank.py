from aiohttp import web
import pytest

from test_eats_tips_withdrawal import conftest


@pytest.mark.parametrize(
    'jwt, phone, b2p_answer, expected_signature, expected_status, '
    'expected_result',
    [
        (
            conftest.JWT_USER_1,
            '11223344556',
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <GetDefaultSBPBank/>""",
            'NmVjOTdlOGQzZTI0YWE5MTcyYTVjYzUzMzNkNmFlMTY=',
            404,
            {'code': 'no_default_bank', 'message': 'No default bank'},
        ),
        (
            conftest.JWT_USER_2,
            '79110000000',
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <GetDefaultSBPBank>
                <bankId>100000000001</bankId>
                <title>Газпромбанк</title>
                <latinTitle>Gazprombank</latinTitle>
                <signature>ZDg2M2NmMWNjNTRlYzINjZWJiZWY2NWNlNDg4MGE=</signature>
            </GetDefaultSBPBank>""",
            'MGRiNjUxNTYwY2FmOGVmZmIzY2E3YTRlNWMyZDdmNTM=',
            200,
            {
                'id': '100000000001',
                'title': 'Газпромбанк',
                'image': 'http://bank.image.ru',
            },
        ),
    ],
)
@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_sbp_get_default_bank(
        mock_best2pay,
        mock_eats_tips_partners,
        taxi_eats_tips_withdrawal_web,
        jwt,
        phone,
        b2p_answer,
        expected_signature,
        expected_status,
        expected_result,
):
    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': '19cf3fc9-98e5-4e3d-8459-179a602bd7a8', 'alias': '1'},
        )

    @mock_best2pay('/webapi/b2puser/GetDefaultSBPBank')
    async def _mock_get_default_sbp_ba(request):
        assert request.query['signature'] == expected_signature
        return web.Response(
            body=b2p_answer,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    response = await taxi_eats_tips_withdrawal_web.get(
        '/v1/sbp/get-default-bank',
        params={'phone': phone},
        headers={'X-Chaevie-Token': jwt},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
