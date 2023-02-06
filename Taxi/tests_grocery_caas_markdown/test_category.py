import decimal

import pytest

from testsuite.utils import ordered_object

from tests_grocery_caas_markdown.common import constants
from tests_grocery_caas_markdown.common import experiments
from tests_grocery_caas_markdown.plugins import (
    caas_markdown_db as caas_markdown_db_plugin,
)


@pytest.fixture(name='test_grocery_caas_markdown')
def _test_grocery_caas_markdown(taxi_grocery_caas_markdown):
    class TestGroceryCaasMarkdown:
        def __init__(self):
            pass

        @staticmethod
        async def category(
                depot_id,
                country_iso3,
                handler,
                extra_headers=None,
                need_v2=None,
        ):
            headers = constants.DEFAULT_HEADERS.copy()

            if extra_headers is not None:
                for key, val in extra_headers.items():
                    if val is not None:
                        headers[key] = val
                    else:
                        headers.pop(key, None)

            return await taxi_grocery_caas_markdown.post(
                handler,
                headers=headers,
                json={
                    'depot_id': depot_id,
                    'country_iso3': country_iso3,
                    'need_v2': need_v2,
                },
            )

        @staticmethod
        async def invalidate_caches():
            await taxi_grocery_caas_markdown.invalidate_caches()

    return TestGroceryCaasMarkdown()


@experiments.LAVKA_SELLONCOGS_EXPERIMENT
async def test_basic(test_grocery_caas_markdown, caas_markdown_db):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    country_iso3 = constants.COUNTRY_ISO3_WITH_MARKDOWNS
    product_id = constants.DEFAULT_PRODUCT_ID

    caas_markdown_db.add_markdown_products(depot_id, product_id)

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['products'] == [
        {
            'product_id': product_id,
            'quantity': str(constants.DEFAULT_PRODUCT_QUANTITY),
            'tags': constants.DEFAULT_PRODUCT_TAGS,
        },
    ]
    assert response_json['items'] == [
        {'id': product_id, 'item_type': 'product'},
    ]


async def test_no_experiment(test_grocery_caas_markdown, caas_markdown_db):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    country_iso3 = constants.COUNTRY_ISO3_WITH_MARKDOWNS

    caas_markdown_db.add_markdown_products(
        depot_id, constants.DEFAULT_PRODUCT_ID,
    )

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['products'] == []
    assert response_json['items'] == []


@experiments.LAVKA_SELLONCOGS_EXPERIMENT_WITH_NO_ENABLED
async def test_experiment_with_no_enabled(
        test_grocery_caas_markdown, caas_markdown_db,
):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    country_iso3 = constants.COUNTRY_ISO3_WITH_MARKDOWNS

    caas_markdown_db.add_markdown_products(
        depot_id, constants.DEFAULT_PRODUCT_ID,
    )

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['products'] == []
    assert response_json['items'] == []


@pytest.mark.parametrize(
    'depot_id',
    [constants.DEPOT_ID_WITH_MARKDOWNS, constants.DEPOT_ID_WITHOUT_MARKDOWNS],
)
@pytest.mark.parametrize(
    'country_iso3',
    [
        constants.COUNTRY_ISO3_WITH_MARKDOWNS,
        constants.COUNTRY_ISO3_WITHOUT_MARKDOWNS,
    ],
)
@pytest.mark.parametrize(
    'yandex_uid',
    [
        constants.YANDEX_UID_WITH_MARKDOWNS,
        constants.YANDEX_UID_WITHOUT_MARKDOWNS,
    ],
)
@experiments.LAVKA_SELLONCOGS_EXPERIMENT
async def test_markdown_enable(
        test_grocery_caas_markdown,
        caas_markdown_db,
        depot_id,
        country_iso3,
        yandex_uid,
):
    markdowns_enabled = (
        depot_id == constants.DEPOT_ID_WITH_MARKDOWNS
        or yandex_uid == constants.YANDEX_UID_WITH_MARKDOWNS
        or country_iso3 == constants.COUNTRY_ISO3_WITH_MARKDOWNS
    )

    caas_markdown_db.add_markdown_products(
        depot_id, constants.DEFAULT_PRODUCT_ID,
    )

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
        extra_headers={constants.X_YANDEX_UID: yandex_uid},
    )
    assert response.status_code == 200
    response_json = response.json()
    if markdowns_enabled:
        assert response_json['products']
        assert response_json['items']
    else:
        assert not response_json['products']
        assert not response_json['items']


@experiments.LAVKA_SELLONCOGS_EXPERIMENT
async def test_empty_markdowns(test_grocery_caas_markdown):
    response = await test_grocery_caas_markdown.category(
        depot_id=constants.DEPOT_ID_WITH_MARKDOWNS,
        country_iso3=None,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['products'] == []
    assert response_json['items'] == []


@experiments.LAVKA_SELLONCOGS_EXPERIMENT
async def test_zero_stocks(test_grocery_caas_markdown, caas_markdown_db):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    country_iso3 = constants.COUNTRY_ISO3_WITH_MARKDOWNS

    caas_markdown_db.add_markdown_products(
        depot_id,
        caas_markdown_db_plugin.MarkdownProduct(
            product_id=constants.DEFAULT_PRODUCT_ID, quantity=0,
        ),
    )

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['products'] == []
    assert response_json['items'] == []


@experiments.LAVKA_SELLONCOGS_EXPERIMENT
async def test_markdowns_update(test_grocery_caas_markdown, caas_markdown_db):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    country_iso3 = constants.COUNTRY_ISO3_WITH_MARKDOWNS

    product_id_1 = constants.DEFAULT_PRODUCT_ID
    product_quantity_1 = decimal.Decimal(111)

    product_id_2 = '123456789abcdef0002222000123456789abcdef0002'
    product_quantity_2 = decimal.Decimal(222)

    caas_markdown_db.add_markdown_products(depot_id, product_id_1)

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['products'] == [
        {
            'product_id': product_id_1,
            'quantity': str(constants.DEFAULT_PRODUCT_QUANTITY),
            'tags': constants.DEFAULT_PRODUCT_TAGS,
        },
    ]
    assert response_json['items'] == [
        {'id': product_id_1, 'item_type': 'product'},
    ]

    caas_markdown_db.add_markdown_products(
        depot_id,
        products=[
            caas_markdown_db_plugin.MarkdownProduct(
                product_id=product_id_1, quantity=product_quantity_1,
            ),
            caas_markdown_db_plugin.MarkdownProduct(
                product_id=product_id_2, quantity=product_quantity_2,
            ),
        ],
    )

    await test_grocery_caas_markdown.invalidate_caches()

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()

    expected_products = [
        {
            'product_id': product_id_1,
            'quantity': str(product_quantity_1),
            'tags': constants.DEFAULT_PRODUCT_TAGS,
        },
        {
            'product_id': product_id_2,
            'quantity': str(product_quantity_2),
            'tags': constants.DEFAULT_PRODUCT_TAGS,
        },
    ]
    expected_items = [
        {'id': product_id_1, 'item_type': 'product'},
        {'id': product_id_2, 'item_type': 'product'},
    ]

    ordered_object.assert_eq(
        response_json['products'], expected_products, [''],
    )
    ordered_object.assert_eq(response_json['items'], expected_items, [''])


@pytest.mark.config(GROCERY_CAAS_MARKDOWN_GENERIC_TAG='test_generic_tag')
@experiments.LAVKA_SELLONCOGS_EXPERIMENT
async def test_generic_tag(test_grocery_caas_markdown, caas_markdown_db):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    country_iso3 = constants.COUNTRY_ISO3_WITH_MARKDOWNS

    caas_markdown_db.add_markdown_products(
        depot_id, constants.DEFAULT_PRODUCT_ID,
    )

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    assert response.json()['products'][0]['tags'] == ['test_generic_tag']


# Проверяем что в markdown_v2 подают только продукты из конфига,
# а в markdown только то чего нет в конфиге
@experiments.LAVKA_SELLONCOGS_EXPERIMENT
@pytest.mark.config(GROCERY_CAAS_MARKDOWN_V2_PRODUCTS=['product_1'])
@pytest.mark.parametrize(
    'need_v2,result_product',
    [
        pytest.param(True, 'product_1', id='markdown_v2'),
        pytest.param(False, 'product_2', id='markdown_v1'),
    ],
)
async def test_markdown_v2(
        test_grocery_caas_markdown, caas_markdown_db, need_v2, result_product,
):
    depot_id = constants.DEPOT_ID_WITH_MARKDOWNS
    country_iso3 = constants.COUNTRY_ISO3_WITH_MARKDOWNS
    product_1 = 'product_1'
    product_2 = 'product_2'

    caas_markdown_db.add_markdown_products(depot_id, product_1)
    caas_markdown_db.add_markdown_products(depot_id, product_2)

    response = await test_grocery_caas_markdown.category(
        depot_id=depot_id,
        country_iso3=country_iso3,
        need_v2=need_v2,
        handler='/internal/v1/caas-markdown/v2/category',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['items'] == [
        {'id': result_product, 'item_type': 'product'},
    ]
