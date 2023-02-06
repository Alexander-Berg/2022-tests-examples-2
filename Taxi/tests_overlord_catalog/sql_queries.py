import json


NULL = 'NULL'


def add_company(company_id, external_id, title, tin):
    return f"""
INSERT INTO catalog_wms.companies
(company_id, external_id, title, tin) VALUES
('{company_id}', '{external_id}', '{title}', '{tin}');
    """


def quoted_or_null(value):
    if value is None:
        return NULL
    return f'\'{value}\''  # No quote escaping


def quoted_array(value, datatype='TEXT', serialize=quoted_or_null):
    if value is None:
        return NULL
    if isinstance(value, dict):
        raise ValueError('Cannot format dict as postgres array')
    else:
        return (
            'ARRAY['
            + ','.join(serialize(x) for x in value)
            + f']::{datatype}[]'
        )


def dict_as_array_of_kvp(value, datatype='catalog_wms.key_value_pair'):
    if value is None:
        return NULL
    if not isinstance(value, dict):
        raise ValueError('Can format only dict as postgres array of KVP')
    return (
        'ARRAY['
        + ','.join(f'\'({k},{v})\'' for k, v in value.items())
        + f']::{datatype}[]'
    )


def dict_as_composite_type_or_null(value):
    if value is None:
        return NULL
    if not isinstance(value, dict):
        raise ValueError('Can format only dict as postgres composite type')
    return 'ROW(' + ','.join(f'{v}' for v in value.values()) + ')'


def list_as_quoted_object(value):
    if value is None:
        return NULL
    if not isinstance(value, list):
        raise ValueError('Can format only list')
    return (
        '('
        + ','.join(
            ('NULL' if not v else f'\'{v}\'')
            if not isinstance(v, list)
            else quoted_array(v)
            for v in value
        )
        + ')'
    )


def transaction(sql_query):
    return f"""
BEGIN TRANSACTION;
{sql_query}
COMMIT TRANSACTION;
    """


def refresh_wms_views():
    return f"""
REFRESH MATERIALIZED VIEW catalog_wms.active_assortment_items_view;
REFRESH MATERIALIZED VIEW catalog_wms.categories_by_root_view_v3;
REFRESH MATERIALIZED VIEW catalog_wms.goods_with_categories_view_v21;
    """


def add_depot(
        depot_id,
        external_id,
        location,
        zone,
        root_category_id,
        assortment_id,
        price_list_id,
        allow_parcels,
        region_id,
        currency,
        time_range,
        company_id,
        open_ts,
        timezone,
):
    add_assortment_query = _add_assortment_query(assortment_id)

    add_price_list_query = _add_price_list_query(price_list_id)

    add_depot_query = _add_depot_query(
        depot_id,
        external_id,
        location,
        zone,
        root_category_id,
        assortment_id,
        price_list_id,
        allow_parcels,
        region_id,
        currency,
        time_range,
        company_id,
        'NULL' if open_ts is None else f'\'{open_ts}\'',
        timezone,
    )

    return f"""
{add_assortment_query}
{add_price_list_query}
{add_depot_query}
    """


def add_category(
        category_id,
        external_id,
        rank,
        timetable,
        external_depot_id,
        eats_id,
        parent_id=None,
        status=None,
):
    add_wms_category_query = _add_wms_category(
        category_id, external_id, rank, timetable, parent_id, status,
    )

    add_eats_category_query = ''
    return f"""
{add_wms_category_query}
{add_eats_category_query}
    """


def _add_wms_category(
        category_id, external_id, rank, timetable, parent_id=None, status=None,
):
    parent_id = quoted_or_null(parent_id)
    if status is None:
        status = 'active'

    timetable = ','.join(f'\'{item}\'' for item in timetable)

    return f"""
INSERT INTO catalog_wms.categories (
    category_id, external_id, status, name, description, rank, parent_id,
    images, legal_restrictions, timetable
)
VALUES
(
    '{category_id}',
    '{external_id}',
    '{status}',
    'test_category_{category_id}',
    'Test Category With ID {category_id}',
    {rank},
    {parent_id},
    array[]::text[], array[]::text[],
    ARRAY[
        ('everyday', ({timetable})::catalog_wms.timerange_v1)
    ]::catalog_wms.timetable_item_v2[]
);
    """


def add_product(
        product_id,
        external_id,
        rank,
        ranks,
        in_stock,
        depleted,
        restored,
        price,
        depot_id,
        external_depot_id,
        category_id,
        assortment_id,
        assortment_item_id,
        price_list_id,
        price_list_item_id,
        add_to_products,
        add_to_depot,
        add_to_category,
        eats_id,
        vat,
        updated,
        checkout_limit=None,
        country=None,
        country_of_origin=None,
        amount_unit=None,
        amount_unit_alias=None,
        manufacturer=None,
        amount=None,
        storage_traits=None,
        ingredients=None,
        shelf_type='store',
        measurements=None,
        grades=None,
        parent_id=None,
        barcodes=None,
        important_ingredients=None,
        main_allergens=None,
        photo_stickers=None,
        custom_tags=None,
        logistic_tags=None,
        status='active',
        supplier_tin=None,
):
    add_to_goods_query = ''
    add_to_assortment_items_query = ''
    add_to_price_list_items_query = ''
    add_to_stocks_query = ''
    add_to_goods_categories_query = ''
    add_eats_product_query = ''

    if add_to_products:
        add_to_goods_query = _add_to_goods_query(
            product_id,
            external_id,
            status,
            rank,
            vat,
            checkout_limit,
            country,
            country_of_origin,
            amount_unit,
            amount_unit_alias,
            manufacturer,
            amount,
            storage_traits,
            ingredients,
            measurements,
            grades,
            parent_id,
            barcodes,
            important_ingredients,
            main_allergens,
            photo_stickers,
            custom_tags,
            logistic_tags,
            ranks,
            supplier_tin,
        )

    if add_to_depot:
        add_to_assortment_items_query = _add_to_assortment_items_query(
            product_id, assortment_id, assortment_item_id,
        )
        add_to_price_list_items_query = _add_to_price_list_items_query(
            product_id,
            price_list_id,
            price,
            price_list_item_id,
            shelf_type,
            updated,
        )

        if in_stock is not None:
            add_to_stocks_query = _add_to_stocks_query(
                product_id,
                depot_id,
                in_stock,
                depleted,
                updated,
                restored,
                shelf_type,
            )

    add_eats_product_query = ''
    if add_to_category:
        add_to_goods_categories_query = _add_to_goods_categories_query(
            product_id, category_id,
        )

    return f"""
{add_to_goods_query}
{add_to_assortment_items_query}
{add_to_price_list_items_query}
{add_to_stocks_query}
{add_to_goods_categories_query}
{add_eats_product_query}
    """


def count_products(pgsql):
    db = pgsql['overlord_catalog']
    cursor = db.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM catalog_wms.goods;""")
    return cursor.fetchall()[0][0]


def _add_depot_query(
        depot_id,
        external_id,
        location,
        zone,
        root_category_id,
        assortment_id,
        price_list_id,
        allow_parcels,
        region_id,
        currency,
        time_range,
        company_id,
        open_ts,
        timezone,
):
    location = ', '.join(str(lonlat) for lonlat in location)
    zone = json.dumps(zone)

    return f"""
INSERT INTO catalog_wms.depots (
    depot_id, external_id, updated, name, location, extended_zones, title,
    timezone, region_id, currency, status, source, root_category_id,
    assortment_id, price_list_id, allow_parcels, company_id, open_ts
)
VALUES
(
    '{depot_id}',
    '{external_id}',
    CURRENT_TIMESTAMP,
    'test_depot_{depot_id}',
    ({location})::catalog_wms.depot_location,
    ARRAY[
        (
            'foot',
            '{zone}'::JSONB,
            ARRAY[
                ('everyday', ({time_range})::catalog_wms.timerange_v1)
            ]::catalog_wms.timetable_item_v2[],
            'active'
        )
    ]::catalog_wms.extended_zone_v1[],
    'Test Depot With ID {depot_id}',
    '{timezone}',
    {region_id},
    '{currency}',
    'active',
    'WMS',
    '{root_category_id}',
    '{assortment_id}',
    '{price_list_id}',
    '{allow_parcels}',
    '{company_id}',
    {open_ts}
);
    """


def _add_assortment_query(assortment_id, parent_id=None):
    if parent_id is None:
        parent_id = NULL
    else:
        parent_id = f'\'{parent_id}\''

    return f"""
INSERT INTO catalog_wms.assortments (
    assortment_id, status, title, parent_id
)
VALUES
(
    '{assortment_id}',
    'active',
    'Test Assortment With ID {assortment_id}',
    {parent_id}
);
    """


def _add_price_list_query(price_list_id):
    return f"""
INSERT INTO catalog_wms.price_lists (
    price_list_id, status, title
)
VALUES
(
    '{price_list_id}',
    'active',
    'Test Price List With ID {price_list_id}'
);
    """


def _add_to_goods_query(
        product_id,
        external_id,
        status,
        rank,
        vat,
        checkout_limit,
        country,
        country_of_origin,
        amount_unit,
        amount_unit_alias,
        manufacturer,
        amount,
        storage_traits,
        ingredients,
        measurements,
        grades,
        parent_id,
        barcodes,
        important_ingredients,
        main_allergens,
        photo_stickers,
        custom_tags,
        logistic_tags,
        ranks,
        supplier_tin,
):
    vat = quoted_or_null(vat)
    checkout_limit = quoted_or_null(checkout_limit)
    country = quoted_or_null(country)
    manufacturer = quoted_or_null(manufacturer)
    country_of_origin = quoted_array(country_of_origin or [])
    amount_unit = quoted_or_null(amount_unit)
    amount_unit_alias = quoted_or_null(amount_unit_alias)
    if amount is None:
        amount = NULL
    storage_traits = dict_as_array_of_kvp(storage_traits)
    ingredients = (
        '\'{}\'' if ingredients is None else dict_as_array_of_kvp(ingredients)
    )
    measurements = dict_as_composite_type_or_null(measurements)
    grades = list_as_quoted_object(grades)
    parent_id = quoted_or_null(parent_id)
    barcodes = quoted_array(barcodes or [])
    important_ingredients = quoted_array(important_ingredients or [])
    main_allergens = quoted_array(main_allergens or [])
    photo_stickers = quoted_array(photo_stickers or [])
    custom_tags = quoted_array(custom_tags or [])
    logistic_tags = quoted_array(logistic_tags or [])
    ranks = '{' + ', '.join(str(e) for e in ranks) + '}'
    supplier_tin = quoted_or_null(supplier_tin)
    return f"""
INSERT INTO catalog_wms.goods (
    product_id, status, external_id, title, long_title, description, rank,
    ranks, amount_unit, amount_unit_alias, manufacturer, amount, images,
    legal_restrictions, pfc, ingredients, checkout_limit, vat, country,
    country_of_origin, shelf_conditions, measurements, grades, parent_id,
    barcodes, important_ingredients, main_allergens, photo_stickers,
    custom_tags, logistic_tags, supplier_tin
)
VALUES
(
    '{product_id}',
    '{status}',
    {external_id},
    'Test Product With ID {product_id}',
    'Long Test Product With ID {product_id}',
    'Description Of Test Product With ID {product_id}',
    {rank},
    '{ranks}',
    {amount_unit},
    {amount_unit_alias},
    {manufacturer},
    {amount},
    '{{image of {product_id}}}', '{{}}', '{{}}',
    {ingredients},
    {checkout_limit},
    {vat},
    {country},
    {country_of_origin},
    {storage_traits},
    {measurements},
    {grades},
    {parent_id},
    {barcodes},
    {important_ingredients},
    {main_allergens},
    {photo_stickers},
    {custom_tags},
    {logistic_tags},
    {supplier_tin}
);
    """


def _add_to_assortment_items_query(product_id, assortment_id, item_id):
    return f"""
INSERT INTO catalog_wms.assortment_items(
    item_id, status, assortment_id, product_id
)
VALUES
(
    '{item_id}',
    'active',
    '{assortment_id}',
    '{product_id}'
);
    """


def _add_to_price_list_items_query(
        product_id, price_list_id, price, item_id, shelf_type, updated,
):
    return f"""
INSERT INTO catalog_wms.price_list_items (
    item_id, status, price_list_id, product_id, price, shelf_type, updated
)
VALUES
(
    '{item_id}',
    'active',
    '{price_list_id}',
    '{product_id}',
    {price},
    '{shelf_type}'::catalog_wms.shelf_type_t,
    '{updated}'
);
    """


def _add_to_stocks_query(
        product_id,
        depot_id,
        in_stock,
        depleted,
        updated,
        restored,
        shelf_type,
):
    return f"""
INSERT INTO catalog_wms.stocks (
    depot_id, product_id, in_stock, depleted, updated, restored, shelf_type
)
VALUES
(
    '{depot_id}',
    '{product_id}',
    {in_stock},
    '{depleted}',
    '{updated}',
    '{restored}',
    '{shelf_type}'::catalog_wms.shelf_type_t
);
    """


def _fetch_stocks_query(product_id, depot_id, shelf_type):
    return f"""
SELECT * FROM catalog_wms.stocks WHERE
    product_id='{product_id}' and
    depot_id='{depot_id}' and
    shelf_type='{shelf_type}'::catalog_wms.shelf_type_t;
    """


def _update_stocks_query(product_id, depot_id, shelf_type, in_stock):
    return f"""
UPDATE catalog_wms.stocks SET in_stock={in_stock}
WHERE
    product_id='{product_id}' and
    depot_id='{depot_id}' and
    shelf_type='{shelf_type}'::catalog_wms.shelf_type_t;
    """


def _add_to_goods_categories_query(product_id, category_id):
    return f"""
INSERT INTO catalog_wms.goods_categories (
    product_id, category_id
)
VALUES
(
    '{product_id}',
    '{category_id}'
);
    """
