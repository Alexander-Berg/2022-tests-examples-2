from typing import Dict
from typing import List
from typing import Union

import pytest

from .... import models


@pytest.fixture(name='save_places_to_db')
def _save_places_to_db(pg_cursor):
    def do_save_places_to_db(places: List[models.Place]):
        for place in places:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.places(
                    id,
                    slug,
                    brand_id
                )
                values (
                    '{place.place_id}',
                    '{place.slug}',
                    '{place.brand_id}'
                )
                on conflict (id) do update
                set
                    slug = excluded.slug,
                    brand_id = excluded.brand_id
                """,
            )

    return do_save_places_to_db


@pytest.fixture(name='save_brands_to_db')
def _save_brands_to_db(pg_cursor, save_places_to_db, sql_escape):
    def do_save_brands_to_db(brands: List[models.Brand]):
        for brand in brands:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.brands(
                    id,
                    slug,
                    name
                )
                values (
                    '{brand.brand_id}',
                    '{brand.slug}',
                    '{sql_escape(brand.name)}'
                )
                on conflict (id) do update
                set
                    slug = excluded.slug,
                    name = excluded.name
                """,
            )

            save_places_to_db(list(brand.places.values()))

    return do_save_brands_to_db


@pytest.fixture(name='save_snapshot_tables_to_db')
def _save_snapshot_tables_to_db(pg_cursor):
    def do_save_snapshot_tables_to_db(
            snapshot_tables: List[models.SnapshotTable],
    ):
        for snapshot_table in snapshot_tables:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.yt_snapshot_tables
                (table_id, table_path)
                values
                ('{snapshot_table.table_id}', '{snapshot_table.table_path}')
                on conflict (table_id) do update
                set
                    table_path = excluded.table_path
                """,
            )

    return do_save_snapshot_tables_to_db


@pytest.fixture(name='save_brands_feeds_to_db')
def _save_brands_feeds_to_db(pg_cursor, save_brands_to_db):
    def do_save_brands_feeds_to_db(
            brands_feeds: Union[
                List[models.BrandMarketFeed], List[models.BrandGoogleFeed],
            ],
    ):
        if not brands_feeds:
            return

        if isinstance(brands_feeds[0], models.BrandMarketFeed):
            table_name = 'brands_market_feeds'
        else:
            table_name = 'brands_google_feeds'

        for brand_feed in brands_feeds:
            save_brands_to_db([brand_feed.brand])
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.{table_name}(
                    brand_id,
                    s3_path,
                    last_generated_at
                )
                values (
                    '{brand_feed.brand.brand_id}',
                    '{brand_feed.s3_path}',
                    '{str(brand_feed.last_generated_at)}'
                )
                on conflict (brand_id) do update
                set
                    s3_path = excluded.s3_path,
                    last_generated_at = excluded.last_generated_at
                """,
            )

    return do_save_brands_feeds_to_db


@pytest.fixture(name='save_product_brands_to_db')
def _save_product_brands_to_db(pg_cursor, sql_escape):
    def do_save_product_brands_to_db(
            product_brands: List[models.ProductBrand],
    ) -> Dict[str, int]:
        product_brands_name_to_id = {}
        for product_brand in product_brands:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.product_brands(
                    name,
                    last_referenced_at
                ) values (
                    '{sql_escape(product_brand.name)}',
                    '{str(product_brand.last_referenced_at)}'
                )
                on conflict (name) do update
                set
                    -- костыль, чтобы возвращался id
                    name = excluded.name
                returning id
                """,
            )
            product_brand_id = pg_cursor.fetchone()[0]
            product_brands_name_to_id[product_brand.name] = product_brand_id

        return product_brands_name_to_id

    return do_save_product_brands_to_db


@pytest.fixture(name='save_product_types_to_db')
def _save_product_types_to_db(
        pg_cursor, save_product_brands_to_db, sql_escape,
):
    def do_save_product_types_to_db(
            product_types: List[models.ProductType],
    ) -> Dict[str, int]:
        product_types_name_to_id = {}
        for product_type in product_types:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.product_types(
                    name,
                    last_referenced_at
                ) values (
                    '{sql_escape(product_type.name)}',
                    '{str(product_type.last_referenced_at)}'
                )
                on conflict (name) do update
                set
                    -- костыль, чтобы возвращался id
                    name = excluded.name
                returning id
                """,
            )
            product_type_id = pg_cursor.fetchone()[0]
            product_types_name_to_id[product_type.name] = product_type_id

            product_brands_name_to_id = save_product_brands_to_db(
                product_type.get_product_brands(),
            )
            for type_brand in product_type.get_type_brands():
                product_brand_id = product_brands_name_to_id[
                    type_brand.product_brand.name
                ]
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.product_types_product_brands(
                        product_type_id,
                        product_brand_id,
                        last_referenced_at
                    )
                    values(
                        {product_type_id},
                        {product_brand_id},
                        '{str(type_brand.last_referenced_at)}'
                    )
                    on conflict (product_type_id, product_brand_id)
                    do update
                    set
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

        return product_types_name_to_id

    return do_save_product_types_to_db


@pytest.fixture(name='save_tags_to_db')
def _save_tags_to_db(pg_cursor, sql_escape):
    def do_save_tags_to_db(tags: List[models.Tag]) -> Dict[str, int]:
        tag_names_to_id = {}
        for tag in tags:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.tags(
                    name,
                    last_referenced_at
                ) values (
                    '{sql_escape(tag.name)}',
                    '{str(tag.last_referenced_at)}'
                )
                on conflict (name) do update
                set
                    -- костыль, чтобы возвращался id
                    name = excluded.name
                returning id
                """,
            )
            product_type_id = pg_cursor.fetchone()[0]
            tag_names_to_id[tag.name] = product_type_id

        return tag_names_to_id

    return do_save_tags_to_db


@pytest.fixture(name='save_barcodes_to_db')
def _save_barcodes_to_db(pg_cursor):
    def do_save_barcodes_to_db(
            barcodes: List[models.Barcode],
    ) -> Dict[str, int]:
        barcodes_value_to_id = {}
        for barcode in barcodes:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.barcodes(
                    value,
                    last_referenced_at
                ) values (
                    '{barcode.value}',
                    '{str(barcode.last_referenced_at)}'
                )
                on conflict (value) do update
                set
                    -- костыль, чтобы возвращался id
                    value = excluded.value
                returning id
                """,
            )
            barcode_id = pg_cursor.fetchone()[0]
            barcodes_value_to_id[barcode.value] = barcode_id

        return barcodes_value_to_id

    return do_save_barcodes_to_db


@pytest.fixture(name='save_pictures_to_db')
def _save_pictures_to_db(pg_cursor):
    def do_save_pictures_to_db(
            pictures: List[models.Picture],
    ) -> Dict[str, int]:
        pictures_url_to_id = {}
        for picture in pictures:
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.pictures(
                    url,
                    last_referenced_at
                ) values (
                    '{picture.url}',
                    '{str(picture.last_referenced_at)}'
                )
                on conflict (url) do update
                set
                    -- костыль, чтобы возвращался id
                    url = excluded.url
                returning id
                """,
            )
            picture_id = pg_cursor.fetchone()[0]
            pictures_url_to_id[picture.url] = picture_id

        return pictures_url_to_id

    return do_save_pictures_to_db


@pytest.fixture(name='save_products_to_db')
def _save_products_to_db(
        pg_cursor,
        bool_to_sql,
        opt_to_sql,
        save_product_types_to_db,
        save_product_brands_to_db,
        save_barcodes_to_db,
        save_pictures_to_db,
        sql_escape,
):
    def do_save_products_to_db(
            products: List[models.Product],
    ) -> Dict[str, int]:
        nomenclature_id_to_product_id = {}
        for product in products:
            product_type_id = None
            if product.product_type:
                product_type_id = save_product_types_to_db(
                    [product.product_type],
                )[product.product_type.name]
            product_brand_id = None
            if product.product_brand:
                product_brand_id = save_product_brands_to_db(
                    [product.product_brand],
                )[product.product_brand.name]
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.products(
                    nomenclature_id,
                    name,
                    brand_id,
                    origin_id,
                    sku_id,
                    is_choosable,
                    is_catch_weight,
                    is_adult,
                    description,
                    composition,
                    carbohydrates_in_grams,
                    proteins_in_grams,
                    fats_in_grams,
                    calories,
                    storage_requirements,
                    expiration_info,
                    package_info,
                    product_type_id,
                    product_brand_id,
                    vendor_name,
                    vendor_country,
                    measure_in_grams,
                    measure_in_milliliters,
                    volume,
                    delivery_flag,
                    pick_flag,
                    marking_type,
                    is_alcohol,
                    is_fresh,
                    last_referenced_at
                )
                values(
                    '{product.nomenclature_id}',
                    '{sql_escape(product.name)}',
                    '{product.brand.brand_id}',
                    '{product.origin_id}',
                    {opt_to_sql(product.sku_id)},
                    {bool_to_sql(product.is_choosable)},
                    {bool_to_sql(product.is_catch_weight)},
                    {bool_to_sql(product.is_adult)},
                    {opt_to_sql(product.description)},
                    {opt_to_sql(product.composition)},
                    {opt_to_sql(product.carbohydrates_in_grams)},
                    {opt_to_sql(product.proteins_in_grams)},
                    {opt_to_sql(product.fats_in_grams)},
                    {opt_to_sql(product.calories)},
                    {opt_to_sql(product.storage_requirements)},
                    {opt_to_sql(product.expiration_info)},
                    {opt_to_sql(product.package_info)},
                    {opt_to_sql(product_type_id)},
                    {opt_to_sql(product_brand_id)},
                    {opt_to_sql(product.vendor_name)},
                    {opt_to_sql(product.vendor_country)},
                    {opt_to_sql(product.measure_in_grams)},
                    {opt_to_sql(product.measure_in_milliliters)},
                    {opt_to_sql(product.volume)},
                    {opt_to_sql(product.delivery_flag)},
                    {opt_to_sql(product.pick_flag)},
                    {opt_to_sql(product.marking_type)},
                    {opt_to_sql(product.is_alcohol)},
                    {opt_to_sql(product.is_fresh)},
                    '{str(product.last_referenced_at)}'
                )
                on conflict (nomenclature_id) do update
                set
                    name = excluded.name,
                    brand_id = excluded.brand_id,
                    origin_id = excluded.origin_id,
                    sku_id = excluded.sku_id,
                    is_choosable = excluded.is_choosable,
                    is_catch_weight = excluded.is_catch_weight,
                    is_adult = excluded.is_adult,
                    description = excluded.description,
                    composition = excluded.composition,
                    carbohydrates_in_grams = excluded.carbohydrates_in_grams,
                    proteins_in_grams = excluded.proteins_in_grams,
                    fats_in_grams = excluded.fats_in_grams,
                    calories = excluded.calories,
                    storage_requirements = excluded.storage_requirements,
                    expiration_info = excluded.expiration_info,
                    package_info = excluded.package_info,
                    product_type_id = excluded.product_type_id,
                    product_brand_id = excluded.product_brand_id,
                    vendor_name = excluded.vendor_name,
                    vendor_country = excluded.vendor_country,
                    measure_in_grams = excluded.measure_in_grams,
                    measure_in_milliliters = excluded.measure_in_milliliters,
                    volume = excluded.volume,
                    delivery_flag = excluded.delivery_flag,
                    pick_flag = excluded.pick_flag,
                    marking_type = excluded.marking_type,
                    is_alcohol = excluded.is_alcohol,
                    is_fresh = excluded.is_fresh,
                    last_referenced_at = excluded.last_referenced_at
                returning id
                """,
            )
            product_id = pg_cursor.fetchone()[0]
            nomenclature_id_to_product_id[product.nomenclature_id] = product_id

            barcodes_value_to_id = save_barcodes_to_db(product.get_barcodes())
            for product_barcode in product.get_product_barcodes():
                barcode_id = barcodes_value_to_id[
                    product_barcode.barcode.value
                ]
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.products_barcodes(
                        product_id,
                        barcode_id,
                        last_referenced_at
                    )
                    values(
                        {product_id},
                        {barcode_id},
                        '{str(product_barcode.last_referenced_at)}'
                    )
                    on conflict (product_id, barcode_id)
                    do update
                    set
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

            pictures_url_to_id = save_pictures_to_db(product.get_pictures())
            for product_picture in product.get_product_pictures():
                picture_id = pictures_url_to_id[product_picture.picture.url]
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.products_pictures(
                        product_id,
                        picture_id,
                        last_referenced_at
                    )
                    values(
                        {product_id},
                        {picture_id},
                        '{str(product_picture.last_referenced_at)}'
                    )
                    on conflict (product_id, picture_id)
                    do update
                    set
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

            for place_product in product.get_product_in_places():
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.places_products(
                        place_id,
                        product_id,
                        is_available,
                        price,
                        old_price,
                        stocks,
                        vat,
                        last_referenced_at
                    )
                    values (
                        '{place_product.place.place_id}',
                        '{product_id}',
                        {place_product.is_available},
                        {place_product.price},
                        {opt_to_sql(place_product.old_price)},
                        {opt_to_sql(place_product.stocks)},
                        {opt_to_sql(place_product.vat)},
                        '{str(place_product.last_referenced_at)}'
                    )
                    on conflict (place_id, product_id) do update
                    set
                        is_available = excluded.is_available,
                        price = excluded.price,
                        old_price = excluded.old_price,
                        stocks = excluded.stocks,
                        vat = excluded.vat,
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

        return nomenclature_id_to_product_id

    return do_save_products_to_db


@pytest.fixture(name='save_categories_to_db')
def _save_categories_to_db(
        pg_cursor,
        opt_to_sql,
        save_product_types_to_db,
        save_tags_to_db,
        save_products_to_db,
        sql_escape,
):
    def do_save_categories_to_db(categories: List[models.Category]):
        for category in categories:
            do_save_categories_to_db(category.get_child_categories())

            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.categories(
                    id,
                    name,
                    image_url,
                    last_referenced_at
                )
                values(
                    '{category.category_id}',
                    '{sql_escape(category.name)}',
                    {opt_to_sql(category.image_url)},
                    '{str(category.last_referenced_at)}'
                )
                on conflict (id) do update
                set
                    name = excluded.name,
                    image_url = excluded.image_url,
                    last_referenced_at = excluded.last_referenced_at
                """,
            )

            for ccr in category.get_child_categories_relations():
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.categories_relations(
                        category_id,
                        parent_category_id,
                        last_referenced_at
                    )
                    values(
                        '{ccr.category.category_id}',
                        '{category.category_id}',
                        '{str(ccr.last_referenced_at)}'
                    )
                    on conflict
                    (category_id, coalesce(parent_category_id, '-1'))
                    do update
                    set
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

            nomenclature_id_to_product_id = save_products_to_db(
                category.get_products(),
            )
            for category_product in category.get_category_products():
                product_id = nomenclature_id_to_product_id[
                    category_product.product.nomenclature_id
                ]
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.categories_products(
                        brand_id,
                        category_id,
                        product_id,
                        last_referenced_at
                    )
                    values(
                        '{category_product.product.brand.brand_id}',
                        '{category.category_id}',
                        {product_id},
                        '{str(category_product.last_referenced_at)}'
                    )
                    on conflict
                    (brand_id, category_id, product_id)
                    do update
                    set
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

            product_types_name_to_id = save_product_types_to_db(
                category.get_product_types(),
            )
            for cpt in category.get_category_product_types():
                product_type_id = product_types_name_to_id[
                    cpt.product_type.name
                ]
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.categories_product_types(
                        category_id,
                        product_type_id,
                        last_referenced_at
                    )
                    values(
                        '{category.category_id}',
                        {product_type_id},
                        '{str(cpt.last_referenced_at)}'
                    )
                    on conflict (category_id, product_type_id)
                    do update
                    set
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

            tags_name_to_id = save_tags_to_db(category.get_tags())
            for cat_tag in category.get_category_tags():
                tag_id = tags_name_to_id[cat_tag.tag.name]
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.categories_tags(
                        category_id,
                        tag_id,
                        last_referenced_at
                    )
                    values(
                        '{category.category_id}',
                        {tag_id},
                        '{str(cat_tag.last_referenced_at)}'
                    )
                    on conflict (category_id, tag_id)
                    do update
                    set
                        last_referenced_at = excluded.last_referenced_at
                    """,
                )

    return do_save_categories_to_db


@pytest.fixture(name='save_generalized_places_products_to_db')
def _save_generalized_places_products_to_db(
        pg_cursor,
        opt_to_sql,
        save_categories_to_db,
        save_products_to_db,
        sql_escape,
):
    def do_save(
            generalized_places_products: List[models.GeneralizedPlacesProduct],
    ):
        for generalized_places_product in generalized_places_products:
            nomenclature_id_to_product_id = save_products_to_db(
                [generalized_places_product.product],
            )
            product_id = nomenclature_id_to_product_id[
                generalized_places_product.product.nomenclature_id
            ]

            save_categories_to_db([generalized_places_product.category])

            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.generalized_places_products(
                    product_id,
                    category_id,
                    price,
                    old_price,
                    vat
                )
                values(
                    {product_id},
                    '{generalized_places_product.category.category_id}',
                    {generalized_places_product.price},
                    {opt_to_sql(generalized_places_product.old_price)},
                    {opt_to_sql(generalized_places_product.vat)}
                )
                on conflict (product_id) do update
                set
                    category_id = excluded.category_id,
                    price = excluded.price,
                    old_price = excluded.old_price,
                    vat = excluded.vat
                """,
            )

    return do_save


@pytest.fixture(name='save_seo_queries_to_db')
def _save_seo_queries_to_db(
        bool_to_sql,
        opt_to_sql,
        pg_cursor,
        save_product_types_to_db,
        save_product_brands_to_db,
        sql_escape,
):
    def do_save_seo_queries_to_db(
            seo_queries: List[models.SeoQuery],
    ) -> Dict[str, int]:
        seo_queries_slug_to_id = {}
        for seo_query in seo_queries:
            product_type_id = None
            if seo_query.product_type:
                product_type_id = save_product_types_to_db(
                    [seo_query.product_type],
                )[seo_query.product_type.name]
            product_brand_id = None
            if seo_query.product_brand:
                product_brand_id = save_product_brands_to_db(
                    [seo_query.product_brand],
                )[seo_query.product_brand.name]
            pg_cursor.execute(
                f"""
                insert into eats_retail_seo.seo_queries(
                    product_type_id,
                    product_brand_id,
                    is_enabled
                )
                values (
                    {opt_to_sql(product_type_id)},
                    {opt_to_sql(product_brand_id)},
                    {bool_to_sql(seo_query.is_enabled)}
                )
                on conflict (
                    coalesce(product_type_id, -1),
                    coalesce(product_brand_id, -1)
                )
                do update set
                    is_enabled = excluded.is_enabled
                returning id
                """,
            )
            seo_query_id = pg_cursor.fetchone()[0]

            generated_seo_query_type = 'generated'
            manual_seo_query_type = 'manual'

            result_slug = None
            for seo_query_type in [
                    generated_seo_query_type,
                    manual_seo_query_type,
            ]:
                if seo_query_type == generated_seo_query_type:
                    item_data = seo_query.generated_data
                    table_name = 'generated_seo_queries_data'
                else:
                    item_data = seo_query.manual_data
                    table_name = 'manual_seo_queries_data'
                if not item_data:
                    continue
                pg_cursor.execute(
                    f"""
                    insert into eats_retail_seo.{table_name}(
                        seo_query_id,
                        slug,
                        query,
                        title,
                        description,
                        priority
                    )
                    values (
                        {seo_query_id},
                        '{sql_escape(item_data.slug)}',
                        '{sql_escape(item_data.query)}',
                        '{sql_escape(item_data.title)}',
                        '{sql_escape(item_data.description)}',
                        {item_data.priority}
                    )
                    on conflict (seo_query_id) do update
                    set
                        slug = excluded.slug,
                        query = excluded.query,
                        title = excluded.title,
                        description = excluded.description,
                        priority = excluded.priority
                    """,
                )
                result_slug = item_data.slug

            if result_slug:
                seo_queries_slug_to_id[result_slug] = seo_query_id

        return seo_queries_slug_to_id

    return do_save_seo_queries_to_db
