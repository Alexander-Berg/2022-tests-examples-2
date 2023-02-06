import pytest

# Checks /admin/products/v1/localization GET
# Получить все ключи с переводами из танкера
@pytest.mark.translations(
    virtual_catalog={
        'tanker_key_title_1': {'en': 'First key', 'ru': 'Первый ключ'},
        'tanker_key_title_2': {'en': 'Second key', 'ru': 'Второй ключ'},
    },
)
@pytest.mark.parametrize(
    'locale,expected_response',
    [
        pytest.param(None, 'ru_response.json', id='no locale'),
        pytest.param('en', 'en_response.json', id='en'),
        pytest.param('ru', 'ru_response.json', id='ru'),
    ],
)
async def test_localization(
        taxi_grocery_products, load_json, locale, expected_response,
):
    await taxi_grocery_products.invalidate_caches()
    headers = {'Accept-Language': locale}
    response = await taxi_grocery_products.get(
        '/admin/products/v1/localization', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


# Checks /admin/products/v1/localization GET
# ошибка 400 при отсутсвии перевода на ru
@pytest.mark.translations(
    virtual_catalog={
        'title_key_1': {'en': 'title_key_translation_en_1'},
        'title_key_2': {'en': 'title_key_translation_en_2'},
    },
)
async def test_localization_400(taxi_grocery_products):
    await taxi_grocery_products.invalidate_caches()
    headers = {'Accept-Language': 'ru'}
    response = await taxi_grocery_products.get(
        '/admin/products/v1/localization', headers=headers,
    )
    assert response.status_code == 400
