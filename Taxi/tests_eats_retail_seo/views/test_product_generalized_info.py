import decimal
from typing import Any
from typing import Dict

import pytest

from .. import models

HANDLER = '/v1/product/generalized-info'
BRAND_1_ID = '771'
PLACE_1_ID = '1001'
PLACE_2_ID = '1002'
PRODUCT_NOMENCLATURE_ID_1 = '12331b95-1ff2-4bc4-b78d-dcaa1f69b006'
PRODUCT_NOMENCLATURE_ID_2 = '45631b95-1ff2-4bc4-b78d-dcaa1f69b006'
PRODUCT_NOMENCLATURE_ID_3 = '78931b95-1ff2-4bc4-b78d-dcaa1f69b006'
PRODUCT_NOMENCLATURE_ID_4 = '89131b95-1ff2-4bc4-b78d-dcaa1f69b006'
PRODUCT_NOMENCLATURE_ID_5_NOT_IN_MENU = 'ghi31b95-1ff2-4bc4-b78d-dcaa1f69b006'


@pytest.mark.parametrize(
    'product_nomenclature_id',
    [
        pytest.param(PRODUCT_NOMENCLATURE_ID_1, id='1'),
        pytest.param(PRODUCT_NOMENCLATURE_ID_2, id='2'),
        pytest.param(PRODUCT_NOMENCLATURE_ID_3, id='3'),
        pytest.param(PRODUCT_NOMENCLATURE_ID_4, id='4'),
    ],
)
async def test_product_generalized_info(
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        # parametrize params
        product_nomenclature_id,
):
    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [products, categories, generalized_places_products] = _generate_data(
        brands,
    )
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(
        list(generalized_places_products.values()),
    )

    response = await taxi_eats_retail_seo.get(
        f'{HANDLER}?product_id={product_nomenclature_id}',
    )
    assert response.status_code == 200
    expected_response = _generate_expected_response(
        generalized_places_products[product_nomenclature_id],
    )
    assert _sort_response(response.json()) == expected_response


@pytest.mark.parametrize(
    'product_nomenclature_id',
    [
        pytest.param(PRODUCT_NOMENCLATURE_ID_5_NOT_IN_MENU, id='not_in_menu'),
        pytest.param(
            '99999999-9999-9999-9999-999999999999', id='not_in_brand',
        ),
    ],
)
async def test_404(
        save_brands_to_db,
        save_categories_to_db,
        save_generalized_places_products_to_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        # parametrize params
        product_nomenclature_id,
):
    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    [products, categories, generalized_places_products] = _generate_data(
        brands,
    )
    save_products_to_db(products)
    save_categories_to_db(categories)
    save_generalized_places_products_to_db(
        list(generalized_places_products.values()),
    )

    response = await taxi_eats_retail_seo.get(
        f'{HANDLER}?product_id={product_nomenclature_id}',
    )
    assert response.status_code == 404


def _generate_brands():
    brand_1 = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand_1.places = {
        PLACE_1_ID: models.Place(
            place_id=PLACE_1_ID, slug='place1001', brand_id=brand_1.brand_id,
        ),
        PLACE_2_ID: models.Place(
            place_id=PLACE_2_ID, slug='place1002', brand_id=brand_1.brand_id,
        ),
    }

    return {brand.brand_id: brand for brand in [brand_1]}


def _generate_data(brands):
    product_type_1 = models.ProductType(name='Молоко')

    product_brand_1 = models.ProductBrand('Мираторг')
    product_brand_2 = models.ProductBrand('Агуша')

    barcode_1 = models.Barcode('10205800000')
    barcode_2 = models.Barcode('10205800001')
    barcode_3 = models.Barcode('10205800002')
    barcode_4 = models.Barcode('78905800000')

    picture_1 = models.Picture('product_url_1')
    picture_2 = models.Picture('product_url_2')
    picture_3 = models.Picture('product_url_3')

    product_1 = models.Product(
        nomenclature_id=PRODUCT_NOMENCLATURE_ID_1,
        name='Молоко',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-1',
        sku_id='some_sku_id',
        is_choosable=False,
        is_catch_weight=True,
        description='Товар 1<p>Описание</p> <b>Молоко</b>',
        composition='Состав товара',
        carbohydrates_in_grams=decimal.Decimal('7.1'),
        proteins_in_grams=decimal.Decimal('7.5'),
        fats_in_grams=decimal.Decimal('14.8'),
        calories=decimal.Decimal('120.2'),
        storage_requirements='при температуре от +13С до +23С',
        expiration_info='180 д',
        package_info='Вакуумная упаковка',
        product_type=product_type_1,
        product_brand=product_brand_2,
        vendor_name='Поставщик&nbsp;1',
        vendor_country='Австралия',
        measure_in_milliliters=2000,
        volume=2000,
        delivery_flag=False,
        pick_flag=True,
        marking_type='default',
        is_fresh=True,
    )
    product_1.set_pictures([picture_1])
    product_2 = models.Product(
        nomenclature_id=PRODUCT_NOMENCLATURE_ID_2,
        name='Конфеты&nbsp;M&m\'s',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-2',
        description='Конфеты&npsp;M&M\'s;<p>шоколадные конфеты</p>',
        expiration_info=' 10  дней  ',
        vendor_name='Поставщик&nbsp;2',
        vendor_country='Невалидная страна',
        measure_in_grams=100,
        volume=200,
        delivery_flag=True,
        pick_flag=False,
    )
    product_2.set_barcodes([barcode_1, barcode_2, barcode_3])
    product_2.set_pictures([picture_2])
    product_3 = models.Product(
        nomenclature_id=PRODUCT_NOMENCLATURE_ID_3,
        name='Колбаса',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-3',
        is_adult=True,
        description='Товар&nbsp;3<BR/>Описание 1<p><B>Описание 2</B>test</p>',
        expiration_info='некорректный срок хранения',
        product_brand=product_brand_1,
        delivery_flag=True,
        pick_flag=True,
        is_alcohol=True,
    )
    product_3.set_barcodes([barcode_4])
    product_4 = models.Product(
        nomenclature_id=PRODUCT_NOMENCLATURE_ID_4,
        name='Сервелат',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-4',
        is_adult=True,
        description='Товар 4',
        vendor_country='РОССИЯ',
        measure_in_grams=1600,
        delivery_flag=False,
        pick_flag=False,
    )
    product_4.set_pictures([picture_3])
    product_5_not_in_categories = models.Product(
        nomenclature_id=PRODUCT_NOMENCLATURE_ID_5_NOT_IN_MENU,
        name='Товар вне категорий',
        brand=brands[BRAND_1_ID],
        origin_id='item-origin-id-7',
    )
    products = [
        product_1,
        product_2,
        product_3,
        product_4,
        product_5_not_in_categories,
    ]

    category_1 = models.Category(
        category_id='1234', name='Молоко', image_url='cat_url_1234',
    )
    category_1.set_products([product_1])
    category_2 = models.Category(category_id='123', name='Молоко & сыр')
    category_2.set_child_categories([category_1])
    category_3 = models.Category(
        category_id='789', name='Колбасные&nbsp;изделия',
    )
    category_3.set_products([product_3, product_4])
    category_4 = models.Category(category_id='12', name='Молочные продукты')
    category_4.set_child_categories([category_2, category_3])

    category_5 = models.Category(
        category_id='456', name='Конфеты&nbsp;<b>шоколадные</b>',
    )
    category_5.set_products([product_2])
    category_6 = models.Category(category_id='45', name='Конфеты')
    category_6.set_child_categories([category_5])

    categories = [category_4, category_6]

    generalized_places_product_1 = models.GeneralizedPlacesProduct(
        product=product_1,
        category=category_1,
        price=decimal.Decimal('8'),
        vat=10,
    )
    generalized_places_product_2 = models.GeneralizedPlacesProduct(
        product=product_2,
        category=category_5,
        price=decimal.Decimal('99'),
        old_price=decimal.Decimal('95.3'),
        vat=20,
    )
    generalized_places_product_3 = models.GeneralizedPlacesProduct(
        product=product_3, category=category_3, price=decimal.Decimal('50.97'),
    )
    generalized_places_product_4 = models.GeneralizedPlacesProduct(
        product=product_4,
        category=category_4,
        price=decimal.Decimal('20'),
        vat=0,
    )
    generalized_places_products = {
        item.product.nomenclature_id: item
        for item in [
            generalized_places_product_1,
            generalized_places_product_2,
            generalized_places_product_3,
            generalized_places_product_4,
        ]
    }

    return [products, categories, generalized_places_products]


def _sort_response(response):
    response['product']['static_data']['barcodes'] = sorted(
        response['product']['static_data']['barcodes'],
        key=lambda x: x['value'],
    )
    return response


def _generate_expected_response(item: models.GeneralizedPlacesProduct):
    return {
        'product': {
            'id': item.product.nomenclature_id,
            'static_data': _generate_expected_static_data(item.product),
            'dynamic_data': _generate_expected_dynamic_data(item),
        },
    }


def _generate_expected_static_data(product: models.Product):
    static_data = {
        'origin_id': product.origin_id,
        'place_brand_id': product.brand.brand_id,
        'name': product.name,
        'description': product.description,
        'barcodes': _generate_item_barcodes(product),
        'is_choosable': product.is_choosable,
        'is_catch_weight': product.is_catch_weight,
        'is_adult': product.is_adult,
        'shipping_type': _generate_item_shipping_type(product),
        'images': _generate_item_images(product),
        'is_alcohol': product.is_alcohol,
        'is_fresh': product.is_fresh,
    }  # type: Dict[str, Any]
    measure = _generate_item_measure(product)
    if measure is not None:
        static_data['measure'] = measure
    volume = _generate_item_volume(product)
    if volume is not None:
        static_data['volume'] = volume
    if product.vendor_name is not None:
        static_data['vendor_name'] = product.vendor_name
    if product.vendor_country is not None:
        static_data['vendor_country'] = product.vendor_country
    if product.product_brand is not None:
        static_data['brand'] = product.product_brand.name
    if product.carbohydrates_in_grams is not None:
        static_data['carbohydrates'] = str(product.carbohydrates_in_grams)
    if product.proteins_in_grams is not None:
        static_data['proteins'] = str(product.proteins_in_grams)
    if product.fats_in_grams is not None:
        static_data['fats'] = str(product.fats_in_grams)
    if product.calories is not None:
        static_data['calories'] = str(product.calories)
    if product.storage_requirements is not None:
        static_data['storage_requirements'] = product.storage_requirements
    expiration_info = _generate_item_expiration_info(product)
    if expiration_info is not None:
        static_data['expiration_info'] = expiration_info
    if product.sku_id is not None:
        static_data['sku_id'] = product.sku_id
    if product.product_type is not None:
        static_data['product_type'] = product.product_type.name
    if product.package_info is not None:
        static_data['package_info'] = product.package_info
    if product.marking_type is not None:
        static_data['marking_type'] = product.marking_type
    return static_data


def _generate_expected_dynamic_data(item: models.GeneralizedPlacesProduct):
    dynamic_data = {
        'parent_category_ids': [item.category.category_id],
        'price': str(item.price),
    }  # type: Dict[str, Any]
    if item.old_price is not None:
        dynamic_data['old_price'] = str(item.old_price)
    if item.vat is not None:
        dynamic_data['vat_percentage'] = item.vat
    return dynamic_data


def _generate_item_measure(product: models.Product):
    if product.measure_in_grams:
        value = product.measure_in_grams
        if value >= 1000 and value % 1000 == 0:
            return {'value': value / 1000, 'unit': 'KGRM'}
        return {'value': value, 'unit': 'GRM'}
    if product.measure_in_milliliters:
        value = product.measure_in_milliliters
        if value >= 1000 and value % 1000 == 0:
            return {'value': value / 1000, 'unit': 'LT'}
        return {'value': value, 'unit': 'MLT'}
    return None


def _generate_item_volume(product: models.Product):
    value = product.volume
    if not value:
        return None
    if value >= 1000 and value % 1000 == 0:
        return {'value': value / 1000, 'unit': 'DMQ'}
    return {'value': value, 'unit': 'CMQ'}


def _generate_item_shipping_type(product: models.Product):
    if product.delivery_flag and not product.pick_flag:
        return 'delivery'
    if not product.delivery_flag and product.pick_flag:
        return 'pickup'
    # default value in nomenclature
    return 'all'


def _generate_item_barcodes(product: models.Product):
    return [{'value': barcode.value} for barcode in product.get_barcodes()]


def _generate_item_images(product: models.Product):
    if not product.get_pictures():
        return []
    images = []
    sort_order = len(product.get_pictures()) - 1
    for picture in product.get_pictures():
        images.append({'url': picture.url, 'sort_order': sort_order})
        sort_order -= 1
    return sorted(images, key=lambda x: x['sort_order'], reverse=True)


def _generate_item_expiration_info(product: models.Product):
    if product.expiration_info is None:
        return None
    parts = product.expiration_info.split(' ')
    result_parts = []
    for part in parts:
        part = part.strip(' ')
        if not part:
            continue
        result_parts.append(part)
    if len(result_parts) != 2:
        return None
    return {'value': int(result_parts[0]), 'unit': result_parts[1]}
