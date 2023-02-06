import pytest


@pytest.mark.parametrize(
    'url, expected_status, expected_response',
    [
        pytest.param(
            '/v1/categories',
            200,
            {
                'items': [
                    {'name': 'econom', 'translation': 'Эконом'},
                    {'name': 'business', 'translation': 'Комфорт'},
                    {'name': 'comfortplus', 'translation': 'Комфорт+'},
                    {'name': 'cargocorp', 'translation': 'Грузовой (корп.)'},
                ],
            },
            id='rus',
        ),
        pytest.param(
            '/v1/categories?services=taxi',
            200,
            {
                'items': [
                    {'name': 'econom', 'translation': 'Эконом'},
                    {'name': 'business', 'translation': 'Комфорт'},
                    {'name': 'comfortplus', 'translation': 'Комфорт+'},
                ],
            },
            id='without cargo',
        ),
        pytest.param(
            '/v1/categories?country=isr',
            200,
            {
                'items': [
                    {'name': 'econom', 'translation': 'Эконом'},
                    {'name': 'business', 'translation': 'Комфорт'},
                    {'name': 'comfortplus', 'translation': 'Израиль Фикс'},
                    {'name': 'cargocorp', 'translation': 'Грузовой (корп.)'},
                ],
            },
            id='isr',
        ),
        pytest.param(
            '/v1/categories?services=cargo',
            200,
            {
                'items': [
                    {'name': 'cargocorp', 'translation': 'Грузовой (корп.)'},
                ],
            },
            id='without taxi',
        ),
    ],
)
@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом'},
        'name.business': {'ru': 'Комфорт'},
        'name.comfortplus': {'ru': 'Комфорт+'},
        'name.telaviv_fix': {'ru': 'Израиль Фикс'},
        'name.cargocorp': {'ru': 'Грузовой (корп.)'},
    },
)
@pytest.mark.config(
    CORP_CATEGORIES={
        '__default__': {
            'econom': 'name.econom',
            'business': 'name.business',
            'comfortplus': 'name.comfortplus',
        },
        'isr': {'comfortplus': 'name.telaviv_fix'},
    },
    CORP_CARGO_CATEGORIES={'__default__': {'cargocorp': 'name.cargocorp'}},
)
async def test_get_view(
        taxi_corp_admin_client, url, expected_status, expected_response,
):
    response = await taxi_corp_admin_client.get(url)
    response_json = await response.json()
    assert response.status == expected_status, response_json
    if 'items' in response_json:
        response_items = sorted(
            response_json['items'], key=lambda x: x['name'],
        )
        expected_items = sorted(
            expected_response['items'], key=lambda x: x['name'],
        )
        assert response_items == expected_items
    else:
        assert response_json == expected_response, response_json
