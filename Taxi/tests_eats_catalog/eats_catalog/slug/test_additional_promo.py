from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage


NOW = parser.parse('2021-01-01T12:00:00+03:00')

PLACE_SLUG = 'coffee_boy_novodmitrovskaya_2k6'

PROMO_TYPE = {
    'id': 1,
    'name': 'Тесты в подарок',
    'pictureUri': 'http://istock/harold',
    'detailedPictureUrl': 'http://istock/pepe',
}

PROMO = {
    'id': 1,
    'name': 'Бесплатные тесты',
    'description': 'При написании фичи, тесты в подарок',
    'type': PROMO_TYPE,
}

DISCOUNT_PROMO_TYPE = {
    'detailedPictureUrl': None,
    'id': 101,
    'name': 'Бесплатная доставка',
    'pictureUri': 'picture_uri',
}

DISCOUNT_PROMO = {
    'description': 'description',
    'id': 101,
    'name': 'name',
    'type': DISCOUNT_PROMO_TYPE,
}


EXP_PROMO_TYPE = {
    'id': 2,
    'name': 'Промо тайп из эксперимента',
    'pictureUri': 'http://istock/harold',
    'detailedPictureUrl': 'http://istock/pepe',
}

EXP_PROMO = {
    'id': 2,
    'name': 'Промо из эксперимента',
    'description': 'Описание промо из эксперимента',
    'type': EXP_PROMO_TYPE,
}

TAG = 'tag1'


@experiments.always_match(
    name='eats_discounts_applicator_promocode',
    consumer='eats-discounts-applicator/promocode_discount',
    value={
        'name': 'Скидка 40%',
        'description': 'По промокоду TEMPORARY_SOLUTION',
        'picture_url': 'lala',
        'promo_type_id': 2,
        'promo_type_name': 'test',
        'places_list': {'list_type': 'exclude', 'places_list': []},
        'business_types': ['restaurant'],
    },
)
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
async def test_promocode_slug(slug, eats_catalog_storage):

    eats_catalog_storage.add_place(storage.Place(slug=PLACE_SLUG))

    response = await slug(PLACE_SLUG)

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']['place']
    assert place['promos'] == [
        {
            'id': 2,
            'name': 'Скидка 40%',
            'description': 'По промокоду TEMPORARY_SOLUTION',
            'type': {
                'id': 2,
                'name': 'test',
                'pictureUri': 'lala',
                'detailedPictureUrl': None,
            },
        },
    ]


@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.parametrize(
    'expected_promos,expected_promo_types',
    [
        pytest.param(
            [DISCOUNT_PROMO, PROMO],
            [DISCOUNT_PROMO_TYPE, PROMO_TYPE],
            id='promo enabled',
        ),
        pytest.param(
            [], [], marks=experiments.DISABLE_PROMOS, id='promo disabled',
        ),
    ],
)
async def test_free_discounts_promo(
        slug,
        mockserver,
        eats_catalog_storage,
        eats_discounts_applicator,
        expected_promos,
        expected_promo_types,
):
    """
    Проверяем, что на основе похода в eats-discounts-applicator
    матчится эксперимент, который добавлет
    дополнительную промо акции на бесплатную доставку
    """

    eats_catalog_storage.add_place(storage.Place(slug=PLACE_SLUG))
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    hierarchy = 'place_delivery_discounts'
    eats_discounts_applicator.add_discount(
        discount_id='101',
        hierarchy_name=hierarchy,
        extra={
            'money_value': {
                'menu_value': {'value_type': 'absolute', 'value': '10'},
            },
        },
    )
    eats_discounts_applicator.bind_discount('1', '101', hierarchy)

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await slug(PLACE_SLUG)

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']['place']
    assert place['promos'] == expected_promos
    assert place['promoTypes'] == expected_promo_types


@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.parametrize(
    'order_empty',
    [
        pytest.param(
            False,
            id='with_order',
            marks=experiments.sort_promo_actions(
                consumer='eats-catalog-slug',
                limit=3,
                order={'101': 2, '1': 1},
            ),
        ),
        pytest.param(
            True,
            id='no_order',
            marks=experiments.sort_promo_actions(
                consumer='eats-catalog-slug', limit=3, order={},
            ),
        ),
    ],
)
async def test_promos_sort(
        slug,
        mockserver,
        eats_catalog_storage,
        eats_discounts_applicator,
        order_empty,
):
    """
    Проверяем, что акции сортируются на слаге
    """

    eats_catalog_storage.add_place(storage.Place(slug=PLACE_SLUG))
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    hierarchy = 'place_delivery_discounts'
    eats_discounts_applicator.add_discount(
        discount_id='101',
        hierarchy_name=hierarchy,
        extra={
            'money_value': {
                'menu_value': {'value_type': 'absolute', 'value': '10'},
            },
        },
    )
    eats_discounts_applicator.bind_discount('1', '101', hierarchy)

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await slug(PLACE_SLUG)

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']['place']
    if order_empty:
        assert place['promos'] == [DISCOUNT_PROMO, PROMO]
        assert place['promoTypes'] == [DISCOUNT_PROMO_TYPE, PROMO_TYPE]
    else:
        assert place['promos'] == [PROMO, DISCOUNT_PROMO]
        assert place['promoTypes'] == [PROMO_TYPE, DISCOUNT_PROMO_TYPE]


@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@experiments.hide_promos_slug(enabled=True, promo_type_ids=[1])
async def test_promos_hide(
        slug, mockserver, eats_catalog_storage, eats_discounts_applicator,
):
    """
    Проверяем, что акции не показываются на слаге
    """

    eats_catalog_storage.add_place(storage.Place(slug=PLACE_SLUG))
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    hierarchy = 'place_delivery_discounts'
    eats_discounts_applicator.add_discount(
        discount_id='101',
        hierarchy_name=hierarchy,
        extra={
            'money_value': {
                'menu_value': {'value_type': 'absolute', 'value': '10'},
            },
        },
    )
    eats_discounts_applicator.bind_discount('1', '101', hierarchy)

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await slug(PLACE_SLUG)

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']['place']
    assert PROMO not in place['promos']
    assert PROMO_TYPE not in place['promoTypes']
