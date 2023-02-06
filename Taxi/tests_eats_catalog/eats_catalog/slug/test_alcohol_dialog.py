from dateutil import parser
import pytest

from eats_catalog import storage

TITLE = 'Категория 18+'
TITLE_KEY = 'slug.alcohol_dialog.title.default'
TEXT = 'Подтвердите, что Вы старше 18 лет'
TEXT_KEY = 'slug.alcohol_dialog.text.default'
DESCRIPTION = (
    '<p>Обращаем внимание, что в данном разделе Вы не '
    'сможете купить или заказать доставку алкоголя. Мы '
    'предоставляем возможность забронировать интересующую '
    'Вас продукцию в магазинах партнеров. Подробные условия '
    'можно посмотреть <a href="https://ya.ru">здесь</a>.</p>'
)
DESCRIPTION_KEY = 'slug.alcohol_dialog.description.1'

TRANSLATIONS = {
    'eats-catalog': {
        TITLE_KEY: {'ru': TITLE},
        TEXT_KEY: {'ru': TEXT},
        DESCRIPTION_KEY: {'ru': DESCRIPTION},
    },
}

ALCOHOL_CONFIG = {
    '1': {
        'dialog_title': TITLE_KEY,
        'dialog_text': TEXT_KEY,
        'rules': DESCRIPTION_KEY,
        'licenses': '',
        'rules_with_storage_info': {'full': {}},
        'storage_time': 1,
    },
}


@pytest.mark.parametrize(
    ('brand_id', 'expected'),
    [
        pytest.param(
            1, {'title': TITLE, 'text': TEXT, 'description': DESCRIPTION},
        ),
        pytest.param(100, None),
    ],
)
@pytest.mark.parametrize(
    'query',
    [
        pytest.param(None, id='without_position'),
        pytest.param(
            {'latitude': 55.802998, 'longitude': 37.591503},
            id='with_position',
        ),
    ],
)
@pytest.mark.now('2022-02-02T02:02:02+03:00')
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.config(EATS_RETAIL_ALCOHOL_SHOPS=ALCOHOL_CONFIG)
async def test_alcohol_dialog(
        taxi_eats_catalog, eats_catalog_storage, brand_id, expected, query,
):
    """
     Тест проверяет что объект alcoholDialog будет возвращен в ответе только
     когда в конфиге есть соответствующий этому месту бренд и что формат
     объекта alcoholDialog соответствует ожидаемому
    """

    brand = storage.Brand(brand_id=brand_id)
    place_slug = 'place_slug'
    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug=place_slug, brand=brand),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-02-02T01:02:02+03:00'),
                    end=parser.parse('2023-02-02T03:02:02+03:00'),
                ),
            ],
        ),
    )

    response = await taxi_eats_catalog.get(
        f'/eats-catalog/v1/slug/{place_slug}',
        params=query,
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.7.0',
        },
    )

    assert response.status_code == 200

    found_place = response.json()['payload']['foundPlace']

    if expected:
        assert 'alcoholDialog' in found_place
        assert expected == found_place['alcoholDialog']
    else:
        assert 'alcoholDialog' not in found_place
