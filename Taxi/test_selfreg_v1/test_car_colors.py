import pytest

LOCALE_RU = 'ru'
LOCALE_EN = 'en'
LOCALE_KZ = 'kz'

TRANSLATIONS = {
    'CarHelper_Color_Красный': {'ru': 'красный', 'en': ''},
    'CarHelper_Color_Желтый': {'ru': 'желтый', 'en': ''},
    'CarHelper_Color_Синий': {'ru': 'синий', 'en': ''},
}


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.parametrize('locale', [LOCALE_RU, LOCALE_EN, LOCALE_KZ])
async def test_car_colors(taxi_selfreg, locale):
    print('wololo', locale)

    response = await taxi_selfreg.get(
        '/selfreg/v1/car/colors',
        params={'token': 'token1'},
        headers={'Accept-Language': locale},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'colors': [
            {'color_id': 'Красный', 'localized_name': 'красный'},
            {'color_id': 'Синий', 'localized_name': 'синий'},
            {'color_id': 'Желтый', 'localized_name': 'желтый'},
        ],
    }
