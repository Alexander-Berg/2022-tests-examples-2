import aiohttp.test_utils
import pytest

HEADERS = {
    'X-YaTaxi-Api-Key': 'a8f5513cc4c84d18b56acd86bdd691ed',
    'Content-Type': 'application/json',
}

FLOWS_RESPONSE_EN = {
    'countries': [
        {
            'code': 'rus',
            'flows': [
                {
                    'code': 'close_contract_refresh_oferta_corporate',
                    'name': 'Replace corporate contract with offer contract',
                },
            ],
            'name': 'Russia',
        },
        {
            'code': 'kaz',
            'flows': [
                {
                    'code': 'close_contract_refresh_oferta_corporate',
                    'name': 'Replace corporate contract with offer contract',
                },
            ],
            'name': 'Kazakhstan',
        },
    ],
}
FLOWS_RESPONSE_RU = {
    'countries': [
        {
            'code': 'rus',
            'flows': [
                {
                    'code': 'close_contract_refresh_oferta_corporate',
                    'name': 'Изменение корп.договора на оферту',
                },
            ],
            'name': 'Россия',
        },
        {
            'code': 'kaz',
            'flows': [
                {
                    'code': 'close_contract_refresh_oferta_corporate',
                    'name': 'Изменение корп.договора на оферту',
                },
            ],
            'name': 'Казахстан',
        },
    ],
}


@pytest.mark.translations(
    geoareas={
        'flows.kaz': {'ru': 'Казахстан', 'en': 'Kazakhstan'},
        'flows.rus': {'ru': 'Россия', 'en': 'Russia'},
    },
    forms={
        'flows.close_contract_refresh_oferta_corporate': {
            'ru': 'Изменение корп.договора на оферту',
            'en': 'Replace corporate contract with offer contract',
        },
    },
)
@pytest.mark.parametrize(
    'expected_status,expected_content,locale',
    [
        (200, FLOWS_RESPONSE_EN, None),
        (200, FLOWS_RESPONSE_EN, 'en'),
        (200, FLOWS_RESPONSE_RU, 'ru'),
    ],
)
@pytest.mark.usefixtures('db')
async def test_get_all_flows(
        web_app_client: aiohttp.test_utils.TestClient,
        expected_status: int,
        expected_content: dict,
        locale: str,
):
    if locale is None:
        headers = HEADERS
    else:
        headers = {'Accept-Language': locale, **HEADERS}

    response = await web_app_client.get('/admin/v1/flows/', headers=headers)
    content = await response.json()

    assert (response.status, content) == (expected_status, expected_content), (
        'response status {}, expected {}, '
        'response content {!r}, expected {!r}'.format(
            response.status, expected_status, content, expected_content,
        )
    )
