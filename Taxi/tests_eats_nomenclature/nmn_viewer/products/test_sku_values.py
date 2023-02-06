import pytest

from . import constants
from .. import models
from ... import utils

ASSORTMENT_ID = constants.ASSORTMENT_ID
BRAND_ID = constants.BRAND_ID
DEFAULT_CATEGORY_ID = constants.CATEGORY_ID


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
        'minimal_schema_data.sql',
    ],
)
async def test_minimal_schema(
        stq_runner, load_json, nmn_vwr_utils, exp_set_sku_data,
):
    await exp_set_sku_data(True)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3file = nmn_vwr_utils.s3_get_single_file()
    assert (
        nmn_vwr_utils.sorted_json_data(s3file)
        == nmn_vwr_utils.sorted_json_data(
            load_json('minimal_schema_result.json'),
        )
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
        'full_schema_data.sql',
    ],
)
async def test_full_schema(
        stq_runner, load_json, nmn_vwr_utils, exp_set_sku_data,
):
    await exp_set_sku_data(True)

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3file = nmn_vwr_utils.s3_get_single_file()
    assert nmn_vwr_utils.sorted_json_data(
        s3file,
    ) == nmn_vwr_utils.sorted_json_data(load_json('full_schema_result.json'))


@pytest.mark.parametrize(
    'product_params,sku_params,expected_fields',
    [
        pytest.param(
            {'measure_value': 1000, 'measure_unit': 'GRM'},
            {'weight': '2 кг'},
            {'measure/value': '2', 'measure/unit': 'KGRM'},
            id='measure override (weight)',
        ),
        pytest.param(
            {'measure_value': 1000, 'measure_unit': 'GRM'},
            {'volume': '2 л'},
            {'measure/value': '2', 'measure/unit': 'LT'},
            id='measure override (volume)',
        ),
        pytest.param(
            {'measure_value': 1000, 'measure_unit': 'GRM'},
            {'weight': '2 кг', 'volume': '2 л'},
            {'measure/value': '2', 'measure/unit': 'LT'},
            id='measure override priority',
        ),
        pytest.param(
            {
                'measure_value': 1000,
                'measure_unit': 'GRM',
                'is_catch_weight': True,
            },
            {'weight': '2 кг'},
            {'measure/value': '1000', 'measure/unit': 'GRM'},
            id='measure override disabled on catch weight',
        ),
        pytest.param(
            {'name': 'original'},
            {'name': 'overriden'},
            {'name': 'overriden'},
            id='name override',
        ),
        pytest.param(
            {
                'images': [
                    models.Image(raw_url='original', processed_url='original'),
                ],
            },
            {
                'images': [
                    models.Image(
                        raw_url='overriden', processed_url='overriden',
                    ),
                ],
            },
            {'images': [{'url': 'overriden', 'sort_order': 0}]},
            id='images override',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_fields(
        stq_runner,
        nmn_vwr_utils,
        exp_set_sku_data,
        # parametrize
        product_params,
        sku_params,
        expected_fields,
):
    await exp_set_sku_data(True)

    sku = models.Sku(**sku_params)
    product = models.Product(sku=sku, brand_id=BRAND_ID, **product_params)
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    nmn_vwr_utils.verify_json_field(s3product, expected_fields)


@pytest.mark.parametrize(
    'product_params,sku_params,expected_attributes',
    [
        pytest.param(
            {'vendor': models.Vendor(country='original')},
            {'country': 'overriden'},
            {'vendor_country': {'value': 'overriden'}},
            id='vendor country override',
        ),
        pytest.param(
            {'description': 'original'},
            {'package_type': 'overriden'},
            {'description': {'value': 'Упаковка: overriden'}},
            id='description override',
        ),
        pytest.param(
            {'is_adult': False},
            {'is_adult': True},
            {'is_adult': {'value': True}},
            id='adult override',
        ),
        pytest.param(
            {'package_info': 'original'},
            {'package_type': 'overriden'},
            {'package_info': {'value': 'overriden'}},
            id='package info override',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_attributes(
        stq_runner,
        nmn_vwr_utils,
        exp_set_sku_data,
        # parametrize
        product_params,
        sku_params,
        expected_attributes,
):
    await exp_set_sku_data(True)

    sku = models.Sku(**sku_params)
    product = models.Product(sku=sku, brand_id=BRAND_ID, **product_params)
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    nmn_vwr_utils.verify_json_attribute(s3product, expected_attributes)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_image_url_filtering(
        stq_runner, nmn_vwr_utils, exp_set_sku_data,
):
    """
    Verifies that images without processed url are ignored
    """

    await exp_set_sku_data(True)

    image_to_display = models.Image(
        raw_url='raw_1', processed_url='processed_1',
    )
    image_to_ignore = models.Image(raw_url='raw_2', processed_url=None)

    sku = models.Sku(images=[image_to_display, image_to_ignore])
    product = models.Product(sku=sku, brand_id=BRAND_ID)
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    images = s3product['images']
    assert images == [{'url': image_to_display.processed_url, 'sort_order': 0}]


@pytest.mark.parametrize(**utils.gen_bool_params('use_override'))
@pytest.mark.parametrize(**utils.gen_bool_params('is_empty_override'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'brand_place.sql',
        'assortment_with_category.sql',
    ],
)
async def test_sku_override(
        stq_runner,
        nmn_vwr_utils,
        exp_set_sku_data,
        # parametrize
        use_override,
        is_empty_override,
):
    await exp_set_sku_data(True)

    sku = models.Sku(name='overriden')
    sku_override = models.Sku(name='overriden more')
    product = models.Product(
        name='original',
        sku=sku,
        use_sku_override=use_override,
        sku_override=None if is_empty_override else sku_override,
        brand_id=BRAND_ID,
    )
    nmn_vwr_utils.sql.save_category_product(
        models.CategoryProduct(product=product, assortment_id=ASSORTMENT_ID),
        category_id=DEFAULT_CATEGORY_ID,
    )

    await stq_runner.eats_nomenclature_add_custom_assortment.call(
        task_id='1', kwargs={'assortment_id': ASSORTMENT_ID},
    )

    s3product = nmn_vwr_utils.s3_get_single_product()
    name = s3product['name']
    if not use_override:
        assert name == sku.name
    elif is_empty_override:
        assert name == product.name
    else:
        assert name == sku_override.name
