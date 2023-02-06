from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage


def create_place_with_schedule(eats_catalog_storage, index, place, schedule):
    eats_catalog_storage.add_place(
        storage.Place(
            slug=place['slug'],
            place_id=index,
            brand=storage.Brand(brand_id=index),
            business=place['business'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=index,
            place_id=index,
            shipping_type=place['shipping'],
            working_intervals=schedule,
        ),
    )


# Во всех тестах дополнительно проверяется, что заведения с самовывозом
# следуют за заведениями с доставкой.
@pytest.mark.parametrize(
    ['requested_block', 'expected'],
    [
        # Тест проверяет что в случае когда запрошен блок
        # open_delivery_or_pickup и игнорирование типа получения включено и
        # для ресторанов и для магазинов, то возвращаются рестораны и
        # магазины и с доставкой и с самовывозом.
        pytest.param(
            'open_delivery_or_pickup',
            {
                'delivery_restaurant': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
                'pickup_restaurant': {
                    'delivery': '1.1 км',
                    'is_available': True,
                },
                'delivery_shop': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
                'pickup_shop': {'delivery': '1.1 км', 'is_available': True},
            },
            marks=[
                experiments.ignore_shipping_type_in_search(
                    ['restaurant', 'shop'],
                ),
            ],
        ),
        # Тест проверяет что в случае когда запрошен блок
        # open_delivery_or_pickup и игнорирование типа получения выключено и
        # для ресторанов и для магазинов, то возвращаются рестораны и магазины
        #  только с доставкой.
        pytest.param(
            'open_delivery_or_pickup',
            {
                'delivery_restaurant': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
                'delivery_shop': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
            },
            marks=[experiments.ignore_shipping_type_in_search([])],
        ),
        # Тест проверяет что в случае когда запрошен блок
        # open_delivery_or_pickup и игнорирование типа получения включено
        # только для ресторанов, то рестораны возвращаются и с доставкой и с
        # самовывозом, а магазины только с доставкой.
        pytest.param(
            'open_delivery_or_pickup',
            {
                'delivery_restaurant': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
                'pickup_restaurant': {
                    'delivery': '1.1 км',
                    'is_available': True,
                },
                'delivery_shop': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
            },
            marks=[experiments.ignore_shipping_type_in_search(['restaurant'])],
        ),
        # Тест проверяет что в случае когда запрошен блок
        # open_delivery_or_pickup и игнорирование типа получения включено
        # только для магазинов, то магазины возвращаются и с доставкой и с
        # самовывозом, а рестораны только с доставкой.
        pytest.param(
            'open_delivery_or_pickup',
            {
                'delivery_restaurant': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
                'delivery_shop': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
                'pickup_shop': {'delivery': '1.1 км', 'is_available': True},
            },
            marks=[experiments.ignore_shipping_type_in_search(['shop'])],
        ),
        # Тест проверяет что в случае когда запрошен блок open, то
        # игнорирование типа получения для ресторанов и для магазинов не
        # влияет на результат, т.е. будут возвращены только заведения с
        # доставкой.
        pytest.param(
            'open',
            {
                'delivery_restaurant': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
                'delivery_shop': {
                    'delivery': '25 – 35 мин',
                    'is_available': True,
                },
            },
            marks=[
                experiments.ignore_shipping_type_in_search(
                    ['restaurant', 'shop'],
                ),
            ],
        ),
        # Тест проверяет что в случае когда запрошен блок closed, то
        # игнорирование типа получения для ресторанов и для магазинов не
        # влияет на результат, т.е. открытые заведения не будут возвращены.
        # А будут возвращены только закрытые заведения на доставку, т.к.
        # фильтр closed пропускает только заведения с доставкой (как и
        # фильтр open для открытых заведений).
        pytest.param(
            'closed',
            {
                'delivery_restaurant_closed': {
                    'delivery': 'Сегодня 23:00',
                    'is_available': False,
                },
                'delivery_shop_closed': {
                    'delivery': 'Сегодня 23:00',
                    'is_available': False,
                },
            },
            marks=[
                experiments.ignore_shipping_type_in_search(
                    ['restaurant', 'shop'],
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2021-07-05T14:14:00+03:00')
@pytest.mark.config(
    EATS_RETAIL_ALCOHOL_SHOPS={
        '6': {
            'rules': 'text.alcohol_shops.rules',
            'licenses': 'text.alcohol_shops.licenses',
            'rules_with_storage_info': {'full': {}},
            'storage_time': 48,
        },
        '7': {
            'rules': 'text.alcohol_shops.rules',
            'licenses': 'text.alcohol_shops.licenses',
            'rules_with_storage_info': {'full': {}},
            'storage_time': 48,
        },
    },
)
async def test_ignore_shipping_types(
        catalog_for_full_text_search,
        eats_catalog_storage,
        requested_block,
        expected,
):
    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    closed_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T22:00:00+03:00'),
            end=parser.parse('2021-07-05T23:00:00+03:00'),
        ),
    ]

    places = [
        {
            'slug': 'delivery_restaurant',
            'business': storage.Business.Restaurant,
            'shipping': storage.ShippingType.Delivery,
        },
        {
            'slug': 'pickup_restaurant',
            'business': storage.Business.Restaurant,
            'shipping': storage.ShippingType.Pickup,
        },
        {
            'slug': 'delivery_shop',
            'business': storage.Business.Shop,
            'shipping': storage.ShippingType.Delivery,
        },
        {
            'slug': 'pickup_shop',
            'business': storage.Business.Shop,
            'shipping': storage.ShippingType.Pickup,
        },
    ]

    counter = 1
    # Для каждого элемента places создаем открытый магазин и закрытый
    # для того чтобы проверить разные значения поля availability.
    for place in places:
        create_place_with_schedule(
            eats_catalog_storage, counter, place, open_schedule,
        )
        counter += 1
        place['slug'] += '_closed'
        create_place_with_schedule(
            eats_catalog_storage, counter, place, closed_schedule,
        )
        counter += 1

    response = await catalog_for_full_text_search(
        shipping_type=storage.ShippingType.Delivery,
        blocks=[{'id': requested_block, 'type': requested_block}],
    )

    assert response.status == 200
    blocks = response.json()['blocks']

    if not expected:
        assert not blocks
        return

    assert len(blocks) == 1

    result_places = blocks[0]['list']

    slugs_expected = [slug for slug, _ in expected.items()]
    slugs_result = [place['slug'] for place in result_places]
    assert sorted(slugs_expected) == sorted(slugs_result)

    pickup_found = False
    for place in result_places:
        slug = place['slug']
        assert expected[slug]['delivery'] == place['delivery']['text']
        assert (
            expected[slug]['is_available']
            == place['availability']['is_available']
        )

        # Проверяем дополнительно что все заведения с самовывозом
        # следуют после заведений с доставкой.
        if slug.find('pickup') != -1:
            pickup_found = True
        elif slug.find('delivery') != -1 and pickup_found:
            assert False
