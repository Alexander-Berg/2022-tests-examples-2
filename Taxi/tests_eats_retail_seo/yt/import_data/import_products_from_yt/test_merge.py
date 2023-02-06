import datetime as dt
import decimal

import pytest
import pytz

from . import constants
from .... import models


OLD_LAST_REFERENCED_AT = dt.datetime(2021, 2, 18, 1, 0, 0, tzinfo=pytz.UTC)
MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=['yt_products_schema.yaml'],
    static_table_data=['yt_products_data_for_merge.yaml'],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_merge(
        add_common_data,
        assert_objects_lists,
        enable_periodic_in_config,
        get_barcodes_from_db,
        get_pictures_from_db,
        get_product_types_from_db,
        get_product_brands_from_db,
        get_products_from_db,
        save_products_to_db,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
):
    @testpoint('products-importer-finished')
    def products_import_finished(param):
        pass

    @testpoint(constants.PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(constants.PERIODIC_NAME)
    brand = add_common_data()

    [
        product_brands,
        product_types,
        barcodes,
        pictures,
        products,
    ] = _generate_data(brand)
    [product_brand_1, product_brand_2] = product_brands
    [product_type_1, product_type_2] = product_types
    [barcode_1, barcode_2, barcode_3, barcode_4] = barcodes
    [picture_1, picture_2, picture_3] = pictures
    [
        product_1_will_be_changed,
        product_2_will_be_reset,
        product_4_will_not_change,
    ] = products

    save_products_to_db(products)

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    product_brand_2.last_referenced_at = MOCK_NOW
    new_product_brand_1 = models.ProductBrand(
        'Простоквашино new', last_referenced_at=MOCK_NOW,
    )
    new_product_brand_2 = models.ProductBrand(
        'Мираторг', last_referenced_at=MOCK_NOW,
    )

    # устаревшие связки удаляются отдельным периодиком
    product_type_2.set_type_brands(
        [
            models.ProductTypeProductBrand(
                product_brand_1, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.ProductTypeProductBrand(
                product_brand_2, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    product_type_2.last_referenced_at = MOCK_NOW

    new_product_type_1 = models.ProductType(
        'Молоко new', last_referenced_at=MOCK_NOW,
    )
    new_product_type_1.set_type_brands(
        [
            models.ProductTypeProductBrand(
                new_product_brand_1, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    new_product_type_2 = models.ProductType(
        'Колбаса', last_referenced_at=MOCK_NOW,
    )
    new_product_type_2.set_type_brands(
        [
            models.ProductTypeProductBrand(
                new_product_brand_2, last_referenced_at=MOCK_NOW,
            ),
        ],
    )

    barcode_1.last_referenced_at = MOCK_NOW
    barcode_2.last_referenced_at = MOCK_NOW
    new_barcode_1 = models.Barcode(
        '3911220000009', last_referenced_at=MOCK_NOW,
    )
    new_barcode_2 = models.Barcode(
        '4620001311514', last_referenced_at=MOCK_NOW,
    )

    picture_1.last_referenced_at = MOCK_NOW
    picture_2.last_referenced_at = MOCK_NOW
    new_picture_1 = models.Picture('new_url_1', last_referenced_at=MOCK_NOW)
    new_picture_2 = models.Picture('new_url_2', last_referenced_at=MOCK_NOW)
    new_picture_3 = models.Picture('new_url_3', last_referenced_at=MOCK_NOW)

    product_1_will_be_changed.origin_id = '350462'
    product_1_will_be_changed.name = 'Молоко Простоквашино Новое'
    product_1_will_be_changed.is_choosable = False
    product_1_will_be_changed.is_catch_weight = True
    product_1_will_be_changed.is_adult = True
    product_1_will_be_changed.sku_id = '1408d309-f63a-4b95-8843-87fece3d6ae36'
    product_1_will_be_changed.description = (
        'Товар 1<p>Новое описание</p> <b>Молоко</b>1'
    )
    product_1_will_be_changed.composition = 'Состав молока new'
    product_1_will_be_changed.carbohydrates_in_grams = decimal.Decimal('21.1')
    product_1_will_be_changed.proteins_in_grams = decimal.Decimal('22.2')
    product_1_will_be_changed.fats_in_grams = decimal.Decimal('23.3')
    product_1_will_be_changed.calories = decimal.Decimal('24.4')
    product_1_will_be_changed.storage_requirements = 'при температуре от +15С'
    product_1_will_be_changed.expiration_info = '280 д'
    product_1_will_be_changed.package_info = 'без упаковки'
    product_1_will_be_changed.product_type = new_product_type_1
    product_1_will_be_changed.product_brand = new_product_brand_1
    product_1_will_be_changed.vendor_name = 'ООО "Простоквашино" new'
    product_1_will_be_changed.vendor_country = 'Россия new'
    product_1_will_be_changed.measure_in_grams = 1500
    product_1_will_be_changed.measure_in_milliliters = None
    product_1_will_be_changed.volume = 200
    product_1_will_be_changed.delivery_flag = False
    product_1_will_be_changed.pick_flag = True
    product_1_will_be_changed.marking_type = 'energy_drink'
    product_1_will_be_changed.is_alcohol = False
    product_1_will_be_changed.is_fresh = True
    product_1_will_be_changed.last_referenced_at = MOCK_NOW
    # устаревшие связки удаляются отдельным периодиком
    product_1_will_be_changed.set_product_barcodes(
        [
            models.ProductBarcode(barcode_1, last_referenced_at=MOCK_NOW),
            models.ProductBarcode(
                barcode_2, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.ProductBarcode(new_barcode_1, last_referenced_at=MOCK_NOW),
        ],
    )
    product_1_will_be_changed.set_product_pictures(
        [
            models.ProductPicture(
                picture_1, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.ProductPicture(picture_2, last_referenced_at=MOCK_NOW),
            models.ProductPicture(new_picture_1, last_referenced_at=MOCK_NOW),
            models.ProductPicture(new_picture_2, last_referenced_at=MOCK_NOW),
        ],
    )

    product_2_will_be_reset.is_choosable = True
    product_2_will_be_reset.is_catch_weight = False
    product_2_will_be_reset.is_adult = False
    product_2_will_be_reset.sku_id = None
    product_2_will_be_reset.description = None
    product_2_will_be_reset.composition = None
    product_2_will_be_reset.carbohydrates_in_grams = None
    product_2_will_be_reset.proteins_in_grams = None
    product_2_will_be_reset.fats_in_grams = None
    product_2_will_be_reset.calories = None
    product_2_will_be_reset.storage_requirements = None
    product_2_will_be_reset.expiration_info = None
    product_2_will_be_reset.package_info = None
    product_2_will_be_reset.product_type = None
    product_2_will_be_reset.product_brand = None
    product_2_will_be_reset.vendor_name = None
    product_2_will_be_reset.vendor_country = None
    product_2_will_be_reset.measure_in_grams = None
    product_2_will_be_reset.measure_in_milliliters = None
    product_2_will_be_reset.volume = None
    product_2_will_be_reset.delivery_flag = None
    product_2_will_be_reset.pick_flag = None
    product_2_will_be_reset.marking_type = None
    product_2_will_be_reset.is_alcohol = False
    product_2_will_be_reset.is_fresh = False
    product_2_will_be_reset.last_referenced_at = MOCK_NOW
    # устаревшие связки удаляются отдельным периодиком
    product_2_will_be_reset.set_product_barcodes(
        [
            models.ProductBarcode(
                barcode_2, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.ProductBarcode(
                barcode_3, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.ProductBarcode(
                barcode_4, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    product_2_will_be_reset.set_product_pictures(
        [
            models.ProductPicture(
                picture_2, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.ProductPicture(
                picture_3, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )

    product_3_new = models.Product(
        nomenclature_id='559cffb0-9723-4377-b354-25419eef427b',
        name='Сервелат Российский',
        brand=brand,
        origin_id='488759',
        sku_id='b81d3603-0879-45d0-83c0-880fcec7a3cc',
        is_choosable=True,
        is_catch_weight=False,
        is_adult=False,
        description='<p>Описание Сервелат Российский</p>',
        composition='Состав сервелата',
        carbohydrates_in_grams=decimal.Decimal('121.1'),
        proteins_in_grams=decimal.Decimal('122.2'),
        fats_in_grams=decimal.Decimal('123.3'),
        calories=decimal.Decimal('124.4'),
        storage_requirements='при температуре от +125С',
        expiration_info='380 д',
        package_info='упаковка',
        product_type=new_product_type_2,
        product_brand=new_product_brand_2,
        vendor_name='ООО Мираторг',
        vendor_country='РОССИЯ',
        measure_in_grams=None,
        measure_in_milliliters=250,
        volume=None,
        delivery_flag=True,
        pick_flag=True,
        marking_type='tobacco',
        is_alcohol=True,
        is_fresh=False,
        last_referenced_at=MOCK_NOW,
    )
    product_3_new.set_product_barcodes(
        [models.ProductBarcode(new_barcode_2, last_referenced_at=MOCK_NOW)],
    )
    product_3_new.set_product_pictures(
        [models.ProductPicture(new_picture_3, last_referenced_at=MOCK_NOW)],
    )

    product_4_will_not_change.set_product_barcodes(
        [
            models.ProductBarcode(barcode_1, last_referenced_at=MOCK_NOW),
            models.ProductBarcode(barcode_2, last_referenced_at=MOCK_NOW),
        ],
    )
    product_4_will_not_change.set_product_pictures(
        [
            models.ProductPicture(picture_1, last_referenced_at=MOCK_NOW),
            models.ProductPicture(picture_2, last_referenced_at=MOCK_NOW),
        ],
    )
    product_4_will_not_change.last_referenced_at = MOCK_NOW

    assert_objects_lists(
        get_barcodes_from_db(),
        [
            barcode_1,
            barcode_2,
            barcode_3,
            barcode_4,
            new_barcode_1,
            new_barcode_2,
        ],
    )
    assert_objects_lists(
        get_pictures_from_db(),
        [
            picture_1,
            picture_2,
            picture_3,
            new_picture_1,
            new_picture_2,
            new_picture_3,
        ],
    )
    assert_objects_lists(
        get_product_types_from_db(),
        [
            product_type_1,
            product_type_2,
            new_product_type_1,
            new_product_type_2,
        ],
    )
    assert_objects_lists(
        get_product_brands_from_db(),
        [
            product_brand_1,
            product_brand_2,
            new_product_brand_1,
            new_product_brand_2,
        ],
    )
    assert_objects_lists(
        get_products_from_db(),
        [
            product_1_will_be_changed,
            product_2_will_be_reset,
            product_3_new,
            product_4_will_not_change,
        ],
    )

    assert products_import_finished.times_called == 1
    assert periodic_finished.times_called == 1


def _generate_data(brand):
    product_brand_1 = models.ProductBrand(
        'Простоквашино', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_brand_2 = models.ProductBrand(
        'Домик в деревне', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_brands = [product_brand_1, product_brand_2]

    product_type_1 = models.ProductType(
        name='Молоко', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_type_1.set_product_brands(
        [product_brand_1, product_brand_2],
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_type_2 = models.ProductType(
        'Сыр', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_type_2.set_product_brands(
        [product_brand_1, product_brand_2],
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_types = [product_type_1, product_type_2]

    barcode_1 = models.Barcode(
        '2911220000009', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    barcode_2 = models.Barcode(
        '4607084351377', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    barcode_3 = models.Barcode(
        '4607084351378', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    barcode_4 = models.Barcode(
        '4607084351379', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    barcodes = [barcode_1, barcode_2, barcode_3, barcode_4]

    picture_1 = models.Picture(
        'url_1', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    picture_2 = models.Picture(
        'url_2', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    picture_3 = models.Picture(
        'url_3', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    pictures = [picture_1, picture_2, picture_3]

    product_1_will_be_changed = models.Product(
        nomenclature_id='12331b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Молоко Простоквашино',
        brand=brand,
        origin_id='350461',
        sku_id='93144054-e2f1-49bb-b711-3d27c04fa3b5',
        is_choosable=True,
        is_catch_weight=False,
        is_adult=False,
        description='Товар 1<p>Описание</p> <b>Молоко</b>',
        composition='Состав молока',
        carbohydrates_in_grams=decimal.Decimal('11.1'),
        proteins_in_grams=decimal.Decimal('12.2'),
        fats_in_grams=decimal.Decimal('13.3'),
        calories=decimal.Decimal('14.4'),
        storage_requirements='при температуре от +13С до +23С',
        expiration_info='180 д',
        package_info='Вакуумная упаковка',
        product_type=product_type_1,
        product_brand=product_brand_1,
        vendor_name='ООО "Простоквашино"',
        vendor_country='Россия',
        measure_in_grams=None,
        measure_in_milliliters=500,
        volume=None,
        delivery_flag=True,
        pick_flag=False,
        marking_type='default',
        is_alcohol=True,
        is_fresh=True,
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_1_will_be_changed.set_barcodes(
        [barcode_1, barcode_2], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_1_will_be_changed.set_pictures(
        [picture_1, picture_2], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_2_will_be_reset = models.Product(
        nomenclature_id='89131b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Сыр Ламбер',
        brand=brand,
        origin_id='548215',
        sku_id=None,
        is_choosable=True,
        is_catch_weight=True,
        is_adult=False,
        description='<p>Описание сыра Ламбер</p>',
        composition=None,
        carbohydrates_in_grams=decimal.Decimal('100'),
        proteins_in_grams=decimal.Decimal('100'),
        fats_in_grams=decimal.Decimal('100'),
        calories=decimal.Decimal('100'),
        storage_requirements='при температуре от +23С',
        expiration_info='100 д',
        package_info='упаковка',
        product_type=product_type_2,
        product_brand=product_brand_2,
        vendor_name=None,
        vendor_country='Австралия',
        measure_in_grams=250,
        measure_in_milliliters=None,
        volume=250,
        delivery_flag=False,
        pick_flag=True,
        marking_type='default',
        is_alcohol=True,
        is_fresh=True,
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_2_will_be_reset.set_barcodes(
        [barcode_2, barcode_3, barcode_4],
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_2_will_be_reset.set_pictures(
        [picture_2, picture_3], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_4_will_not_change = models.Product(
        nomenclature_id='91231b95-1ff2-4bc4-b78d-dcaa1f69b006',
        name='Сыр Российский',
        brand=brand,
        origin_id='548216',
        sku_id='31244054-e2f1-49bb-b711-3d27c04fa3b5',
        is_choosable=True,
        is_catch_weight=False,
        is_adult=False,
        description='Описание сыра',
        composition='Состав сыра',
        carbohydrates_in_grams=decimal.Decimal('11.1'),
        proteins_in_grams=decimal.Decimal('12.2'),
        fats_in_grams=decimal.Decimal('13.3'),
        calories=decimal.Decimal('14.4'),
        storage_requirements='при температуре от +13С до +23С',
        expiration_info='180 д',
        package_info='Вакуумная упаковка',
        product_type=product_type_2,
        product_brand=product_brand_2,
        vendor_name='ООО "Домик в деревне"',
        vendor_country='Россия',
        measure_in_grams=300,
        delivery_flag=True,
        pick_flag=True,
        marking_type='default',
        is_alcohol=False,
        is_fresh=True,
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_4_will_not_change.set_barcodes(
        [barcode_1, barcode_2], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_4_will_not_change.set_pictures(
        [picture_1, picture_2], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    products = [
        product_1_will_be_changed,
        product_2_will_be_reset,
        product_4_will_not_change,
    ]

    return [product_brands, product_types, barcodes, pictures, products]
