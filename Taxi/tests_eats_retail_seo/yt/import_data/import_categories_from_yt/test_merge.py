import datetime as dt

import pytest
import pytz

from . import constants
from .... import models


OLD_LAST_REFERENCED_AT = dt.datetime(2021, 2, 18, 1, 0, 0, tzinfo=pytz.UTC)
MOCK_NOW = dt.datetime(2022, 4, 10, 2, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.yt(
    schemas=[
        'yt_categories_schema.yaml',
        'yt_categories_relations_schema.yaml',
    ],
    static_table_data=[
        'yt_categories_data_for_merge.yaml',
        'yt_categories_relations_data_for_merge.yaml',
    ],
)
@pytest.mark.config(
    EATS_NOMENCLATURE_MASTER_TREE=constants.DEFAULT_MASTER_TREE_CONFIG,
)
async def test_merge(
        add_common_data,
        assert_objects_lists,
        enable_periodic_in_config,
        get_categories_from_db,
        get_product_types_from_db,
        get_tags_from_db,
        save_categories_to_db,
        taxi_eats_retail_seo,
        testpoint,
        yt_apply,
):
    @testpoint('categories-importer-finished')
    def categories_import_finished(param):
        pass

    @testpoint('categories-relations-importer-finished')
    def categories_relations_import_finished(param):  # pylint: disable=C0103
        pass

    @testpoint(constants.PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    enable_periodic_in_config(constants.PERIODIC_NAME)
    add_common_data()

    [product_types, categories, tags] = _generate_data()
    [product_type_1, product_type_2] = product_types
    [tag_1, tag_2] = tags
    [
        category_1_will_be_changed,
        category_2_will_be_changed,
        category_3_will_not_change,
        category_4_will_be_reset,
    ] = categories

    save_categories_to_db(categories)

    await taxi_eats_retail_seo.run_distlock_task(constants.PERIODIC_NAME)

    product_type_1.last_referenced_at = MOCK_NOW
    tag_1.last_referenced_at = MOCK_NOW
    new_product_type_3 = models.ProductType(
        name='яйца', last_referenced_at=MOCK_NOW,
    )
    new_product_type_4 = models.ProductType(
        name='Ультрапастеризованное молоко', last_referenced_at=MOCK_NOW,
    )
    new_tag_3 = models.Tag(name='тег яйца', last_referenced_at=MOCK_NOW)
    new_tag_4 = models.Tag(
        name='тег Ультрапастеризованное молоко', last_referenced_at=MOCK_NOW,
    )

    category_5_new = models.Category(
        category_id='8041',
        name='Ультрапастеризованное',
        image_url='new_cat_url4',
        last_referenced_at=MOCK_NOW,
    )
    category_5_new.set_category_product_types(
        [
            models.CategoryProductType(
                new_product_type_4, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    category_5_new.set_category_tags(
        [models.CategoryTag(new_tag_4, last_referenced_at=MOCK_NOW)],
    )

    category_1_will_be_changed.name = 'Молоко и яйца'
    category_1_will_be_changed.image_url = 'new_cat_url1'
    # устаревшие связки удаляются отдельным периодиком
    category_1_will_be_changed.set_category_product_types(
        [
            models.CategoryProductType(
                product_type_1, last_referenced_at=MOCK_NOW,
            ),
            models.CategoryProductType(
                product_type_2, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.CategoryProductType(
                new_product_type_3, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    category_1_will_be_changed.set_category_tags(
        [
            models.CategoryTag(tag_1, last_referenced_at=MOCK_NOW),
            models.CategoryTag(
                tag_2, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.CategoryTag(new_tag_3, last_referenced_at=MOCK_NOW),
        ],
    )
    category_1_will_be_changed.set_child_categories_relations(
        [
            models.CategoryRelation(
                category_2_will_be_changed, last_referenced_at=MOCK_NOW,
            ),
            models.CategoryRelation(
                category_4_will_be_reset,
                last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
            models.CategoryRelation(
                category_5_new, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    category_1_will_be_changed.last_referenced_at = MOCK_NOW

    category_2_will_be_changed.image_url = 'new_cat_url2'
    category_2_will_be_changed.set_category_product_types(
        [
            models.CategoryProductType(
                product_type_1, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    category_2_will_be_changed.set_category_tags(
        [models.CategoryTag(tag_1, last_referenced_at=MOCK_NOW)],
    )
    category_2_will_be_changed.set_child_categories_relations(
        [
            models.CategoryRelation(
                category_4_will_be_reset, last_referenced_at=MOCK_NOW,
            ),
        ],
    )
    category_2_will_be_changed.last_referenced_at = MOCK_NOW

    category_3_will_not_change.last_referenced_at = MOCK_NOW

    category_4_will_be_reset.image_url = None
    # устаревшие связки удаляются отдельным периодиком
    category_4_will_be_reset.set_category_product_types(
        [
            models.CategoryProductType(
                product_type_1, last_referenced_at=OLD_LAST_REFERENCED_AT,
            ),
        ],
    )
    category_4_will_be_reset.set_category_tags(
        [models.CategoryTag(tag_1, last_referenced_at=OLD_LAST_REFERENCED_AT)],
    )
    category_4_will_be_reset.last_referenced_at = MOCK_NOW

    assert_objects_lists(
        get_product_types_from_db(),
        [
            product_type_1,
            product_type_2,
            new_product_type_3,
            new_product_type_4,
        ],
    )
    assert_objects_lists(
        get_tags_from_db(), [tag_1, tag_2, new_tag_3, new_tag_4],
    )
    assert_objects_lists(
        get_categories_from_db(),
        [
            category_1_will_be_changed,
            category_2_will_be_changed,
            category_3_will_not_change,
            category_4_will_be_reset,
            category_5_new,
        ],
    )

    assert categories_import_finished.times_called == 1
    assert categories_relations_import_finished.times_called == 1
    assert periodic_finished.times_called == 1


def _generate_data():
    product_type_1 = models.ProductType(
        name='молоко', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_type_2 = models.ProductType(
        name='сыр', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    product_types = [product_type_1, product_type_2]

    tag_1 = models.Tag(
        name='тег молоко', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    tag_2 = models.Tag(
        name='тег сыр', last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    tags = [tag_1, tag_2]

    category_1_will_be_changed = models.Category(
        category_id='801',
        name='Молочные продукты',
        image_url='cat_url1',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_1_will_be_changed.set_product_types(
        [product_type_1, product_type_2],
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_1_will_be_changed.set_tags(
        [tag_1, tag_2], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_2_will_be_changed = models.Category(
        category_id='802',
        name='Молоко',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_3_will_not_change = models.Category(
        category_id='803',
        name='Сметана',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_4_will_be_reset = models.Category(
        category_id='804',
        name='Пастеризованное',
        image_url='cat_url3',
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_4_will_be_reset.set_product_types(
        [product_type_1], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_4_will_be_reset.set_tags(
        [tag_1], last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    category_1_will_be_changed.set_child_categories(
        [category_2_will_be_changed, category_4_will_be_reset],
        last_referenced_at=OLD_LAST_REFERENCED_AT,
    )
    categories = [
        category_1_will_be_changed,
        category_2_will_be_changed,
        category_3_will_not_change,
        category_4_will_be_reset,
    ]

    return [product_types, categories, tags]
