from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations

TRANSLATION_KEY = 'catalog_for_full_text_search.pickup_tag'
TRANSLATIONS = {TRANSLATION_KEY: 'С собой', 'c4l.place_category.1': 'Завтраки'}


@pytest.mark.parametrize(
    ['place', 'expected_tags'],
    [
        # Тест проверяет что в случае когда игнорирование shipping_type
        # не включено, ресторан на самовывоз в выдаче отсутствует,
        # соответственно, и тегов у него не будет никаких.
        pytest.param(
            {
                'business': storage.Business.Restaurant,
                'shipping': storage.ShippingType.Pickup,
            },
            [],
        ),
        # Тест проверяет что в случае когда ресторан работает на доставку
        # то в выдаче у него будут стандартные теги.
        pytest.param(
            {
                'business': storage.Business.Restaurant,
                'shipping': storage.ShippingType.Delivery,
            },
            ['Завтраки'],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # не включено, магазин на самовывоз в выдаче отсутствует,
        # соответственно, и тегов у него не будет никаких.
        pytest.param(
            {
                'business': storage.Business.Shop,
                'shipping': storage.ShippingType.Pickup,
            },
            [],
        ),
        # Тест проверяет что в случае когда магазин работает на доставку
        # то в выдаче у него будут стандартные теги.
        pytest.param(
            {
                'business': storage.Business.Shop,
                'shipping': storage.ShippingType.Delivery,
            },
            ['Завтраки'],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, но конфиг по добавлению специального тега выключен,
        # ресторан на самовывоз имеет стандартные теги.
        pytest.param(
            {
                'business': storage.Business.Restaurant,
                'shipping': storage.ShippingType.Pickup,
            },
            ['Завтраки'],
            marks=[experiments.ignore_shipping_type_in_search(['restaurant'])],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, но конфиг по добавлению специального тега выключен,
        # магазин на самовывоз имеет стандартные теги.
        pytest.param(
            {
                'business': storage.Business.Shop,
                'shipping': storage.ShippingType.Pickup,
            },
            ['Завтраки'],
            marks=[experiments.ignore_shipping_type_in_search(['shop'])],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, конфиг по добавлению специального тега включен,
        # но ключ для специального тега не пришел (например, пришел ответ
        # из дефолтной клозы), тогда ресторан на самовывоз имеет стандартные
        # теги.
        pytest.param(
            {
                'business': storage.Business.Restaurant,
                'shipping': storage.ShippingType.Pickup,
            },
            ['Завтраки'],
            marks=[
                experiments.ignore_shipping_type_in_search(['restaurant']),
                experiments.tag_for_pickup_in_search(None),
            ],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, конфиг по добавлению специального тега включен,
        # ключ для специального тега пришел, но его нет в переводах,
        # тогда ресторан на самовывоз имеет стандартные теги.
        pytest.param(
            {
                'business': storage.Business.Restaurant,
                'shipping': storage.ShippingType.Pickup,
            },
            ['Завтраки'],
            marks=[
                experiments.ignore_shipping_type_in_search(['restaurant']),
                experiments.tag_for_pickup_in_search('none'),
            ],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, конфиг по добавлению специального тега включен,
        # но ресторан работает на доставку, то специальный тег не добавляется,
        # возвращаются стандартные теги.
        pytest.param(
            {
                'business': storage.Business.Restaurant,
                'shipping': storage.ShippingType.Delivery,
            },
            ['Завтраки'],
            marks=[
                experiments.ignore_shipping_type_in_search(['restaurant']),
                experiments.tag_for_pickup_in_search('TRANSLATION_KEY'),
            ],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, конфиг по добавлению специального тега включен,
        # но магазин работает на доставку, то специальный тег не добавляется,
        # возвращаются стандартные теги.
        pytest.param(
            {
                'business': storage.Business.Shop,
                'shipping': storage.ShippingType.Delivery,
            },
            ['Завтраки'],
            marks=[
                experiments.ignore_shipping_type_in_search(['shop']),
                experiments.tag_for_pickup_in_search(TRANSLATION_KEY),
            ],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, конфиг по добавлению специального тега включен, в
        # танкере есть соответствующий перевод, то ресторан на самовывоз
        # получает дополнительно специальный тег в первом элементе массива.
        pytest.param(
            {
                'business': storage.Business.Restaurant,
                'shipping': storage.ShippingType.Pickup,
            },
            ['С собой', 'Завтраки'],
            marks=[
                experiments.ignore_shipping_type_in_search(['restaurant']),
                experiments.tag_for_pickup_in_search(TRANSLATION_KEY),
            ],
        ),
        # Тест проверяет что в случае когда игнорирование shipping_type
        # включено, конфиг по добавлению специального тега включен, в
        # танкере есть соответствующий перевод магазин на самовывоз получает
        # дополнительно специальный тег в первом элементе массива.
        pytest.param(
            {
                'business': storage.Business.Shop,
                'shipping': storage.ShippingType.Pickup,
            },
            ['С собой', 'Завтраки'],
            marks=[
                experiments.ignore_shipping_type_in_search(['shop']),
                experiments.tag_for_pickup_in_search(TRANSLATION_KEY),
            ],
        ),
    ],
)
@pytest.mark.now('2021-07-05T14:14:00+03:00')
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_pickup_tag(
        catalog_for_full_text_search,
        eats_catalog_storage,
        place,
        expected_tags,
):
    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            slug='slug',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            business=place['business'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=place['shipping'],
            working_intervals=open_schedule,
        ),
    )

    response = await catalog_for_full_text_search(
        shipping_type=storage.ShippingType.Delivery,
        blocks=[{'id': 'any', 'type': 'any'}],
    )

    assert response.status == 200
    blocks = response.json()['blocks']

    if not expected_tags:
        assert not blocks
        return

    assert len(blocks) == 1
    assert len(blocks[0]['list']) == 1

    tags = blocks[0]['list'][0]['tags']

    assert expected_tags == [tag['name'] for tag in tags]
