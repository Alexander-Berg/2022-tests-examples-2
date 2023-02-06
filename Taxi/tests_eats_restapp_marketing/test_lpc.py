# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import pytest

from eats_restapp_marketing_plugins import *  # noqa: F403 F401


TEST_PARTNER_ID = '123'
TEST_TEMPLATE_NODE_ID = 456
TEST_TEMPLATE_NODE_ID2 = 789

LPC_GET_SITES_200_RESPONSE = {
    'status': '200',
    'json': [
        {
            'name': 'Test1',
            'mainPageScreenshot': (
                'https://avatars.mdst.yandex.net/get-lpc/12345/abc-123/orig'
            ),
            'editPath': '/edit/123/Test1/another_main',
            'finderPath': '/finder/123/Test1/another_main',
            'siteUrl': 'https://project-test1-url',
        },
        {
            'name': 'Test2',
            'mainPageScreenshot': None,
            'editPath': '/edit/123/Test2/another_main',
            'finderPath': '/finder/123/Test2/another_main',
            'siteUrl': 'https://project-test2-url',
        },
    ],
}

LPC_POST_SITES_200_REQUEST = {'templateNodeId': TEST_TEMPLATE_NODE_ID}
LPC_POST_SITES_200_RESPONSE = {
    'status': '200',
    'text': f'/edit/12345678/lpc/frmd/Мой%20Турбо-сайт%20-%209/Страница',
}

LPC_GET_TEMPLATES_200_RESPONSE = {
    'status': '200',
    'json': [
        {
            'id': TEST_TEMPLATE_NODE_ID,
            'name': 'Test template 1',
            'description': 'Template description',
            'screenshot': 'https:://template-test-url',
            'templateId': 'some-code',
        },
        {
            'id': TEST_TEMPLATE_NODE_ID2,
            'name': 'Test template 2',
            'description': '',
            'screenshot': None,
            'templateId': 'some-code',
        },
    ],
}

LPC_400_RESPONSE = {'status': '400'}
LPC_500_RESPONSE = {'status': '500'}


@pytest.mark.parametrize(
    'method, url, lpc_url, data, '
    'lpc_response, expected_status, expected_response',
    [
        [
            'get',
            '/4.0/restapp-front/marketing/v1/lpc/sites',
            '/landing-page-constructor/api/v1/sites',
            None,
            LPC_GET_SITES_200_RESPONSE,
            200,
            LPC_GET_SITES_200_RESPONSE['json'],
        ],
        [
            'get',
            '/4.0/restapp-front/marketing/v1/lpc/sites',
            '/landing-page-constructor/api/v1/sites',
            None,
            LPC_400_RESPONSE,
            400,
            None,
        ],
        [
            'get',
            '/4.0/restapp-front/marketing/v1/lpc/sites',
            '/landing-page-constructor/api/v1/sites',
            None,
            LPC_500_RESPONSE,
            500,
            None,
        ],
        [
            'post',
            '/4.0/restapp-front/marketing/v1/lpc/sites',
            '/landing-page-constructor/api/v1/sites',
            LPC_POST_SITES_200_REQUEST,
            LPC_POST_SITES_200_RESPONSE,
            200,
            LPC_POST_SITES_200_RESPONSE['text'],
        ],
        [
            'post',
            '/4.0/restapp-front/marketing/v1/lpc/sites',
            '/landing-page-constructor/api/v1/sites',
            LPC_POST_SITES_200_REQUEST,
            LPC_400_RESPONSE,
            400,
            None,
        ],
        [
            'post',
            '/4.0/restapp-front/marketing/v1/lpc/sites',
            '/landing-page-constructor/api/v1/sites',
            LPC_POST_SITES_200_REQUEST,
            LPC_500_RESPONSE,
            500,
            None,
        ],
        [
            'get',
            '/4.0/restapp-front/marketing/v1/lpc/templates',
            '/landing-page-constructor/api/v1/templates',
            None,
            LPC_GET_TEMPLATES_200_RESPONSE,
            200,
            LPC_GET_TEMPLATES_200_RESPONSE['json'],
        ],
        [
            'get',
            '/4.0/restapp-front/marketing/v1/lpc/templates',
            '/landing-page-constructor/api/v1/templates',
            None,
            LPC_500_RESPONSE,
            500,
            None,
        ],
    ],
    ids=[
        'get sites 200',
        'get sites 400',
        'get sites 500',
        'post sites 200',
        'post sites 400',
        'post sites 500',
        'get templates 200',
        'get templates 500',
    ],
)
async def test_lpc(
        taxi_eats_restapp_marketing,
        mockserver,
        method,
        url,
        lpc_url,
        data,
        lpc_response,
        expected_status,
        expected_response,
):
    @mockserver.json_handler(lpc_url)
    def _lpc_handler(request):
        if 'text' in lpc_response:
            return mockserver.make_response(
                lpc_response['text'], lpc_response['status'],
            )

        return mockserver.make_response(**lpc_response)

    if method == 'get':
        response = await taxi_eats_restapp_marketing.get(
            url, headers={'X-YaEda-PartnerId': TEST_PARTNER_ID},
        )
    else:
        response = await taxi_eats_restapp_marketing.post(
            url, json=data, headers={'X-YaEda-PartnerId': TEST_PARTNER_ID},
        )

    assert response.status_code == expected_status
    if expected_response is not None:
        if isinstance(expected_response, str):
            assert response.text == expected_response
        else:
            assert response.json() == expected_response
