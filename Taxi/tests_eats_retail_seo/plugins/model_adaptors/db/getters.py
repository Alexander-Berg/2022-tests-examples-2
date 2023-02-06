from typing import List

import pytest

from .... import models


@pytest.fixture(name='get_places_from_db')
def _get_places_from_db(pg_realdict_cursor):
    def do_get_places_from_db(
            ids: List[str] = None, brand_id: str = None,
    ) -> List[models.Place]:
        conditions = []
        if ids is not None and not ids:
            return []
        if ids:
            conditions.append(f"""id in ('{"','".join(ids)}')""")
        if brand_id:
            conditions.append(f"""brand_id = '{brand_id}'""")
        where = ''
        if conditions:
            where = f"""where {' and '.join(conditions)}"""
        pg_realdict_cursor.execute(
            f"""
            select id, slug, brand_id
            from eats_retail_seo.places
            {where}
            """,
        )

        return sorted(
            [
                models.Place(
                    place_id=row['id'],
                    slug=row['slug'],
                    brand_id=row['brand_id'],
                )
                for row in pg_realdict_cursor
            ],
        )

    return do_get_places_from_db


@pytest.fixture(name='get_brands_from_db')
def _get_brands_from_db(pg_realdict_cursor, get_places_from_db):
    def do_get_brands_from_db(ids: List[str] = None) -> List[models.Brand]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""where id in ('{"','".join(ids)}')"""
        pg_realdict_cursor.execute(
            f"""
            select id, slug, name
            from eats_retail_seo.brands
            {where}
            """,
        )

        rows = pg_realdict_cursor.fetchall()
        return sorted(
            [
                models.Brand(
                    brand_id=row['id'],
                    slug=row['slug'],
                    name=row['name'],
                    places={
                        place.place_id: place
                        for place in get_places_from_db(brand_id=row['id'])
                    },
                )
                for row in rows
            ],
        )

    return do_get_brands_from_db


@pytest.fixture(name='get_brands_market_feeds_from_db')
def _get_brands_market_feeds_from_db(
        pg_realdict_cursor,
        get_places_from_db,
        get_brands_from_db,
        to_utc_datetime,
):
    def do_get_brands_market_feeds_from_db(  # pylint: disable=C0103
            brand_ids: List[str] = None,
    ) -> List[models.BrandMarketFeed]:
        where = ''
        if brand_ids:
            where = f"""where id in ('{"','".join(brand_ids)}')"""
        pg_realdict_cursor.execute(
            f"""
            select brand_id, s3_path, last_generated_at
            from eats_retail_seo.brands_market_feeds
            {where}
            """,
        )

        brands_feeds = []
        rows = pg_realdict_cursor.fetchall()
        for row in rows:
            brand = get_brands_from_db(ids=[row['brand_id']])[0]
            brands_feeds.append(
                models.BrandMarketFeed(
                    brand=brand,
                    s3_path=row['s3_path'],
                    last_generated_at=to_utc_datetime(
                        row['last_generated_at'],
                    ),
                ),
            )
        return sorted(brands_feeds)

    return do_get_brands_market_feeds_from_db


@pytest.fixture(name='get_brands_google_feeds_from_db')
def _get_brands_google_feeds_from_db(
        pg_realdict_cursor,
        get_places_from_db,
        get_brands_from_db,
        to_utc_datetime,
):
    def do_get_brands_google_feeds_from_db(  # pylint: disable=C0103
            brand_ids: List[str] = None,
    ) -> List[models.BrandGoogleFeed]:
        where = ''
        if brand_ids:
            where = f"""where id in ('{"','".join(brand_ids)}')"""
        pg_realdict_cursor.execute(
            f"""
            select brand_id, s3_path, last_generated_at
            from eats_retail_seo.brands_google_feeds
            {where}
            """,
        )

        brands_feeds = []
        rows = pg_realdict_cursor.fetchall()
        for row in rows:
            brand = get_brands_from_db(ids=[row['brand_id']])[0]
            brands_feeds.append(
                models.BrandGoogleFeed(
                    brand=brand,
                    s3_path=row['s3_path'],
                    last_generated_at=to_utc_datetime(
                        row['last_generated_at'],
                    ),
                ),
            )
        return sorted(brands_feeds)

    return do_get_brands_google_feeds_from_db


@pytest.fixture(name='get_product_brands_from_db')
def _get_product_brands_from_db(pg_realdict_cursor, to_utc_datetime):
    def do_get_product_brands_from_db(
            ids: List[int] = None,
    ) -> List[models.ProductBrand]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""where id in ({",".join([str(i) for i in ids])})"""
        pg_realdict_cursor.execute(
            f"""
            select name, last_referenced_at
            from eats_retail_seo.product_brands
            {where}
            """,
        )

        return sorted(
            [
                models.ProductBrand(
                    row['name'], to_utc_datetime(row['last_referenced_at']),
                )
                for row in pg_realdict_cursor
            ],
        )

    return do_get_product_brands_from_db


@pytest.fixture(name='get_product_types_from_db')
def _get_product_types_from_db(
        get_product_brands_from_db,
        pg_realdict_cursor,
        sql_escape,
        to_utc_datetime,
):
    def do_get_product_types_from_db(
            ids: List[int] = None,
    ) -> List[models.ProductType]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""where id in ({",".join([str(i) for i in ids])})"""
        pg_realdict_cursor.execute(
            f"""
            select name, last_referenced_at
            from eats_retail_seo.product_types
            {where}
            """,
        )
        product_types = [
            models.ProductType(
                row['name'], to_utc_datetime(row['last_referenced_at']),
            )
            for row in pg_realdict_cursor
        ]
        for product_type in product_types:
            pg_realdict_cursor.execute(
                f"""
                select pb.id, pb.name, ptpb.last_referenced_at
                from eats_retail_seo.product_types_product_brands ptpb
                join eats_retail_seo.product_types pt
                    on ptpb.product_type_id = pt.id
                join eats_retail_seo.product_brands pb
                    on ptpb.product_brand_id = pb.id
                where pt.name = '{sql_escape(product_type.name)}'
                """,
            )
            pb_rows = pg_realdict_cursor.fetchall()
            product_brands_ids = [row['id'] for row in pb_rows]
            product_brand_to_last_referenced_at = {  # pylint: disable=C0103
                row['name']: to_utc_datetime(row['last_referenced_at'])
                for row in pb_rows
            }
            product_brands = get_product_brands_from_db(ids=product_brands_ids)
            for product_brand in product_brands:
                last_referenced_at = product_brand_to_last_referenced_at[
                    product_brand.name
                ]
                product_type.add_product_brand(
                    product_brand, last_referenced_at,
                )

        return sorted(product_types)

    return do_get_product_types_from_db


@pytest.fixture(name='get_tags_from_db')
def _get_tags_from_db(pg_realdict_cursor, sql_escape, to_utc_datetime):
    def do_get_tags_from_db(ids: List[int] = None) -> List[models.Tag]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""where id in ({",".join([str(i) for i in ids])})"""
        pg_realdict_cursor.execute(
            f"""
            select name, last_referenced_at
            from eats_retail_seo.tags
            {where}
            """,
        )
        tags = [
            models.Tag(row['name'], to_utc_datetime(row['last_referenced_at']))
            for row in pg_realdict_cursor
        ]

        return sorted(tags)

    return do_get_tags_from_db


@pytest.fixture(name='get_barcodes_from_db')
def _get_barcodes_from_db(pg_realdict_cursor, to_utc_datetime):
    def do_get_barcodes_from_db(ids: List[int] = None) -> List[models.Barcode]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""where id in ({",".join([str(i) for i in ids])})"""
        pg_realdict_cursor.execute(
            f"""
            select value, last_referenced_at
            from eats_retail_seo.barcodes
            {where}
            """,
        )

        return sorted(
            [
                models.Barcode(
                    row['value'], to_utc_datetime(row['last_referenced_at']),
                )
                for row in pg_realdict_cursor
            ],
        )

    return do_get_barcodes_from_db


@pytest.fixture(name='get_pictures_from_db')
def _get_pictures_from_db(pg_realdict_cursor, to_utc_datetime):
    def do_get_pictures_from_db(ids: List[int] = None) -> List[models.Picture]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""where id in ({",".join([str(i) for i in ids])})"""
        pg_realdict_cursor.execute(
            f"""
            select url, last_referenced_at
            from eats_retail_seo.pictures
            {where}
            """,
        )

        return sorted(
            [
                models.Picture(
                    row['url'], to_utc_datetime(row['last_referenced_at']),
                )
                for row in pg_realdict_cursor
            ],
        )

    return do_get_pictures_from_db


@pytest.fixture(name='get_products_from_db')
def _get_products_from_db(
        pg_realdict_cursor,
        get_barcodes_from_db,
        get_brands_from_db,
        get_pictures_from_db,
        get_places_from_db,
        get_product_types_from_db,
        get_product_brands_from_db,
        to_utc_datetime,
):
    def do_get_products_from_db(
            nomenclature_ids: List[str] = None,
    ) -> List[models.Product]:
        where = ''
        if nomenclature_ids is not None and not nomenclature_ids:
            return []
        if nomenclature_ids is not None:
            where = f"""
                where nomenclature_id in ('{"','".join(nomenclature_ids)}')
            """
        pg_realdict_cursor.execute(
            f"""
            select
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
            from eats_retail_seo.products
            {where}
            """,
        )

        products = []
        product_rows = pg_realdict_cursor.fetchall()
        for product_row in product_rows:
            brand = get_brands_from_db(ids=[product_row['brand_id']])[0]
            product_type = None
            if product_row['product_type_id']:
                product_type = get_product_types_from_db(
                    ids=[product_row['product_type_id']],
                )[0]
            product_brand = None
            if product_row['product_brand_id']:
                product_brand = get_product_brands_from_db(
                    ids=[product_row['product_brand_id']],
                )[0]
            product = models.Product(
                nomenclature_id=product_row['nomenclature_id'],
                name=product_row['name'],
                brand=brand,
                origin_id=product_row['origin_id'],
                sku_id=product_row['sku_id'],
                is_choosable=product_row['is_choosable'],
                is_catch_weight=product_row['is_catch_weight'],
                is_adult=product_row['is_adult'],
                description=product_row['description'],
                composition=product_row['composition'],
                carbohydrates_in_grams=product_row['carbohydrates_in_grams'],
                proteins_in_grams=product_row['proteins_in_grams'],
                fats_in_grams=product_row['fats_in_grams'],
                calories=product_row['calories'],
                storage_requirements=product_row['storage_requirements'],
                expiration_info=product_row['expiration_info'],
                package_info=product_row['package_info'],
                product_type=product_type,
                product_brand=product_brand,
                vendor_name=product_row['vendor_name'],
                vendor_country=product_row['vendor_country'],
                measure_in_grams=product_row['measure_in_grams'],
                measure_in_milliliters=product_row['measure_in_milliliters'],
                volume=product_row['volume'],
                delivery_flag=product_row['delivery_flag'],
                pick_flag=product_row['pick_flag'],
                marking_type=product_row['marking_type'],
                is_alcohol=product_row['is_alcohol'],
                is_fresh=product_row['is_fresh'],
                last_referenced_at=to_utc_datetime(
                    product_row['last_referenced_at'],
                ),
            )

            pg_realdict_cursor.execute(
                f"""
                select barcode_id, value, pbar.last_referenced_at
                from eats_retail_seo.products_barcodes pbar
                join eats_retail_seo.products pr on pbar.product_id = pr.id
                join eats_retail_seo.barcodes bar on pbar.barcode_id = bar.id
                where pr.nomenclature_id = '{product.nomenclature_id}'
                """,
            )
            barcodes_rows = pg_realdict_cursor.fetchall()
            barcodes_ids = [row['barcode_id'] for row in barcodes_rows]
            barcode_to_last_referenced_at = {
                row['value']: to_utc_datetime(row['last_referenced_at'])
                for row in barcodes_rows
            }
            barcodes = get_barcodes_from_db(ids=barcodes_ids)
            for barcode in barcodes:
                last_referenced_at = barcode_to_last_referenced_at[
                    barcode.value
                ]
                product.add_barcode(barcode, last_referenced_at)

            pg_realdict_cursor.execute(
                f"""
                select picture_id, url, ppic.last_referenced_at
                from eats_retail_seo.products_pictures ppic
                join eats_retail_seo.products pr on ppic.product_id = pr.id
                join eats_retail_seo.pictures pic on ppic.picture_id = pic.id
                where pr.nomenclature_id = '{product.nomenclature_id}'
                """,
            )
            pictures_rows = pg_realdict_cursor.fetchall()
            pictures_ids = [row['picture_id'] for row in pictures_rows]
            picture_to_last_referenced_at = {
                row['url']: to_utc_datetime(row['last_referenced_at'])
                for row in pictures_rows
            }
            pictures = get_pictures_from_db(ids=pictures_ids)
            for picture in pictures:
                last_referenced_at = picture_to_last_referenced_at[picture.url]
                product.add_picture(picture, last_referenced_at)

            pg_realdict_cursor.execute(
                f"""
                select
                    place_id,
                    is_available,
                    price,
                    old_price,
                    stocks,
                    vat,
                    pp.last_referenced_at
                from eats_retail_seo.places_products pp
                join eats_retail_seo.products p on p.id = pp.product_id
                where p.nomenclature_id = '{product.nomenclature_id}'
                """,
            )
            places_products_rows = pg_realdict_cursor.fetchall()
            places_products = []
            for places_products_row in places_products_rows:
                place = get_places_from_db(
                    ids=[places_products_row['place_id']],
                    brand_id=brand.brand_id,
                )[0]
                places_products.append(
                    models.ProductInPlace(
                        place=place,
                        is_available=places_products_row['is_available'],
                        price=places_products_row['price'],
                        old_price=places_products_row['old_price'],
                        stocks=places_products_row['stocks'],
                        vat=places_products_row['vat'],
                        last_referenced_at=places_products_row[
                            'last_referenced_at'
                        ],
                    ),
                )
            product.set_product_in_places(sorted(places_products))

            products.append(product)

        return sorted(products)

    return do_get_products_from_db


@pytest.fixture(name='get_categories_from_db')
def _get_categories_from_db(
        pg_realdict_cursor,
        get_products_from_db,
        get_product_types_from_db,
        get_tags_from_db,
        to_utc_datetime,
):
    def do_get_categories_from_db(
            ids: List[str] = None,
    ) -> List[models.Category]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""
                where id in ('{"','".join(ids)}')
            """
        pg_realdict_cursor.execute(
            f"""
            select id, name, image_url, last_referenced_at
            from eats_retail_seo.categories
            {where}
            """,
        )

        categories = []
        categories_rows = pg_realdict_cursor.fetchall()
        for category_row in categories_rows:
            category = models.Category(
                category_id=category_row['id'],
                name=category_row['name'],
                image_url=category_row['image_url'],
                last_referenced_at=to_utc_datetime(
                    category_row['last_referenced_at'],
                ),
            )

            pg_realdict_cursor.execute(
                f"""
                select category_id, last_referenced_at
                from eats_retail_seo.categories_relations
                where parent_category_id = '{category.category_id}'
                """,
            )
            child_cat_id_to_last_referenced_at = {  # pylint: disable=C0103
                row['category_id']: to_utc_datetime(row['last_referenced_at'])
                for row in pg_realdict_cursor
            }
            child_categories = do_get_categories_from_db(
                ids=list(child_cat_id_to_last_referenced_at.keys()),
            )
            for child_category in child_categories:
                last_referenced_at = child_cat_id_to_last_referenced_at[
                    child_category.category_id
                ]
                category.add_child_category(child_category, last_referenced_at)

            pg_realdict_cursor.execute(
                f"""
                select pr.nomenclature_id, cp.last_referenced_at
                from eats_retail_seo.categories_products cp
                join eats_retail_seo.products pr on cp.product_id = pr.id
                where cp.category_id = '{category.category_id}'
                """,
            )
            nomenclature_id_to_last_referenced_at = {  # pylint: disable=C0103
                row['nomenclature_id']: to_utc_datetime(
                    row['last_referenced_at'],
                )
                for row in pg_realdict_cursor
            }
            products = get_products_from_db(
                nomenclature_ids=list(
                    nomenclature_id_to_last_referenced_at.keys(),
                ),
            )
            for product in products:
                last_referenced_at = nomenclature_id_to_last_referenced_at[
                    product.nomenclature_id
                ]
                category.add_product(product, last_referenced_at)

            pg_realdict_cursor.execute(
                f"""
                select pt.id, pt.name, cpt.last_referenced_at
                from eats_retail_seo.categories_product_types cpt
                join eats_retail_seo.product_types pt
                    on cpt.product_type_id = pt.id
                where cpt.category_id = '{category.category_id}'
                """,
            )
            pt_rows = pg_realdict_cursor.fetchall()
            product_types_ids = [row['id'] for row in pt_rows]
            pt_name_to_last_referenced_at = {
                row['name']: to_utc_datetime(row['last_referenced_at'])
                for row in pt_rows
            }
            product_types = get_product_types_from_db(ids=product_types_ids)
            for product_type in product_types:
                last_referenced_at = pt_name_to_last_referenced_at[
                    product_type.name
                ]
                category.add_product_type(product_type, last_referenced_at)

            pg_realdict_cursor.execute(
                f"""
                select t.id, t.name, ct.last_referenced_at
                from eats_retail_seo.categories_tags ct
                join eats_retail_seo.tags t
                    on ct.tag_id = t.id
                where ct.category_id = '{category.category_id}'
                """,
            )
            tags_rows = pg_realdict_cursor.fetchall()
            tags_ids = [row['id'] for row in tags_rows]
            tag_name_to_last_referenced_at = {
                row['name']: to_utc_datetime(row['last_referenced_at'])
                for row in tags_rows
            }
            tags = get_tags_from_db(ids=tags_ids)
            for tag in tags:
                last_referenced_at = tag_name_to_last_referenced_at[tag.name]
                category.add_tag(tag, last_referenced_at)

            categories.append(category)

        return sorted(categories)

    return do_get_categories_from_db


@pytest.fixture(name='get_generalized_places_products_from_db')
def _get_generalized_places_products_from_db(
        pg_realdict_cursor, get_products_from_db, get_categories_from_db,
):
    def do_get(ids: List[str] = None) -> List[models.GeneralizedPlacesProduct]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""
                where id in ('{"','".join(ids)}')
            """
        pg_realdict_cursor.execute(
            f"""
            select
                pr.nomenclature_id,
                gpp.category_id,
                gpp.price,
                gpp.old_price,
                gpp.vat
            from eats_retail_seo.generalized_places_products gpp
            join eats_retail_seo.products pr on gpp.product_id = pr.id
            {where}
            """,
        )

        generalized_places_products = []
        gpp_rows = pg_realdict_cursor.fetchall()
        for gpp_row in gpp_rows:
            product = get_products_from_db(
                nomenclature_ids=[gpp_row['nomenclature_id']],
            )[0]

            category = get_categories_from_db(ids=[gpp_row['category_id']])[0]

            generalized_places_product = models.GeneralizedPlacesProduct(
                product=product,
                category=category,
                price=gpp_row['price'],
                old_price=gpp_row['old_price'],
                vat=gpp_row['vat'],
            )
            generalized_places_products.append(generalized_places_product)

        return sorted(generalized_places_products)

    return do_get


@pytest.fixture(name='get_seo_queries_from_db')
def _get_seo_queries_from_db(
        pg_realdict_cursor,
        get_product_types_from_db,
        get_product_brands_from_db,
):
    def do_get_seo_queries_from_db(
            ids: List[int] = None,
    ) -> List[models.SeoQuery]:
        where = ''
        if ids is not None and not ids:
            return []
        if ids:
            where = f"""where id in ({",".join([str(i) for i in ids])})"""
        pg_realdict_cursor.execute(
            f"""
            select id, product_type_id, product_brand_id, is_enabled
            from eats_retail_seo.seo_queries
            {where}
            """,
        )

        seo_queries = []
        seo_queries_rows = pg_realdict_cursor.fetchall()
        for seo_query_row in seo_queries_rows:
            product_type = None
            if seo_query_row['product_type_id']:
                product_type = get_product_types_from_db(
                    ids=[seo_query_row['product_type_id']],
                )[0]
            product_brand = None
            if seo_query_row['product_brand_id']:
                product_brand = get_product_brands_from_db(
                    ids=[seo_query_row['product_brand_id']],
                )[0]
            seo_query = models.SeoQuery(
                product_type=product_type,
                product_brand=product_brand,
                is_enabled=seo_query_row['is_enabled'],
            )

            generated_seo_query_type = 'generated'
            manual_seo_query_type = 'manual'

            for seo_query_type in [
                    generated_seo_query_type,
                    manual_seo_query_type,
            ]:
                if seo_query_type == generated_seo_query_type:
                    table_name = 'generated_seo_queries_data'
                else:
                    table_name = 'manual_seo_queries_data'
                pg_realdict_cursor.execute(
                    f"""
                    select slug, query, title, description, priority
                    from eats_retail_seo.{table_name}
                    where seo_query_id = {seo_query_row['id']}
                    """,
                )
                row = pg_realdict_cursor.fetchone()
                if row:
                    item_data = models.SeoQueryData(
                        slug=row['slug'],
                        query=row['query'],
                        title=row['title'],
                        description=row['description'],
                        priority=row['priority'],
                    )
                    if seo_query_type == generated_seo_query_type:
                        seo_query.generated_data = item_data
                    else:
                        seo_query.manual_data = item_data

            seo_queries.append(seo_query)

        return sorted(seo_queries)

    return do_get_seo_queries_from_db
