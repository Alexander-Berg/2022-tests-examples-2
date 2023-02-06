import datetime
import json
import typing

from testsuite.utils import matching

from tests_eats_rest_menu_storage import models

# маппинг table_tame и поля представляющего собой uuid
# в таблице brand_table_tame
BRAND_ID_NAMES = {
    'place_menu_items': 'brand_menu_item_id',
    'place_menu_item_inner_options': 'brand_menu_item_inner_option',
    'place_menu_item_option_groups': 'brand_menu_item_option_group',
    'place_menu_item_options': 'brand_menu_item_option',
    'place_menu_categories': 'brand_menu_category_id',
}


def get_deleted_at(deleted: bool) -> typing.Optional[str]:
    if not deleted:
        return None

    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def insert_brand(database, brand_id: int):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.brands (id)
        VALUES (%s);
        """,
        (brand_id,),
    )


def insert_place(database, place: models.Place):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.places (
            id,
            brand_id,
            slug
        ) VALUES (
            %s,
            %s,
            %s
        );
        """,
        (place.place_id, place.brand_id, place.slug),
    )


def insert_place_category_relation(
        database, relation: models.CategoryRelation,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.category_relations (
            place_id,
            category_id,
            parent_id,
            deleted_at
        ) VALUES (
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            relation.place_id,
            relation.category_id,
            relation.parent_id,
            get_deleted_at(relation.deleted),
        ),
    )


def get_brand_menu_categories(
        database, brand_id: int,
) -> typing.List[models.BrandMenuCategory]:
    cursor = database.cursor()
    cursor.execute(
        """
        SELECT
            id,
            brand_id,
            origin_id,
            name
        FROM eats_rest_menu_storage.brand_menu_categories
        WHERE brand_id = %s;
        """,
        (brand_id,),
    )

    result = []
    for row in list(cursor):
        result.append(
            models.BrandMenuCategory(
                brand_id=row[1], origin_id=row[2], name=row[3],
            ),
        )

    return result


def insert_brand_menu_item(
        database, brand_menu_item: models.BrandMenuItem,
) -> str:
    cursor = database.cursor()

    nutrients = None
    if brand_menu_item.nutrients is not None:
        nutrients = json.dumps(brand_menu_item.nutrients.as_dict())

    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.brand_menu_items (
            brand_id,
            origin_id,
            name,
            adult,
            description,
            weight_value,
            weight_unit,
            short_name,
            nutrients
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::TEXT;
        """,
        (
            brand_menu_item.brand_id,
            brand_menu_item.origin_id,
            brand_menu_item.name,
            brand_menu_item.adult,
            brand_menu_item.description,
            brand_menu_item.weight_value,
            brand_menu_item.weight_unit,
            brand_menu_item.short_name,
            nutrients,
        ),
    )
    return cursor.fetchone()[0]


def insert_place_menu_item(
        database, place_menu_item: models.PlaceMenuItem,
) -> int:
    cursor = database.cursor()

    nutrients = None
    if place_menu_item.nutrients is not None:
        nutrients = json.dumps(place_menu_item.nutrients.as_dict())

    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_items(
            brand_menu_item_id,
            place_id,
            origin_id,
            name,
            adult,
            description,
            weight_value,
            weight_unit,
            sort,
            shipping_types,
            legacy_id,
            ordinary,
            choosable,
            deleted_at,
            short_name,
            nutrients,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            cast(%s AS eats_rest_menu_storage.shipping_types_v1[]),
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::BIGINT
        """,
        (
            place_menu_item.brand_menu_item_id,
            place_menu_item.place_id,
            place_menu_item.origin_id,
            place_menu_item.name,
            place_menu_item.adult,
            place_menu_item.description,
            place_menu_item.weight_value,
            place_menu_item.weight_unit,
            place_menu_item.sort,
            place_menu_item.shipping_types,
            place_menu_item.legacy_id,
            place_menu_item.ordinary,
            place_menu_item.choosable,
            place_menu_item.deleted_at,
            place_menu_item.short_name,
            nutrients,
            place_menu_item.updated_at,
        ),
    )
    return cursor.fetchone()[0]


def insert_place_menu_item_price(
        database, place_menu_item_price: models.PlaceMenuItemPrice,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_prices(
            place_menu_item_id,
            price,
            promo_price,
            vat,
            deleted_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            place_menu_item_price.place_menu_item_id,
            place_menu_item_price.price,
            place_menu_item_price.promo_price,
            place_menu_item_price.vat,
            get_deleted_at(place_menu_item_price.deleted),
        ),
    )


def insert_picture(database, picture: models.Picture) -> int:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.pictures(
            url,
            ratio
        )
        VALUES (
            %s,
            %s
        )
        RETURNING id::BIGINT;
        """,
        (picture.url, picture.ratio),
    )
    return cursor.fetchone()[0]


def insert_item_picture(database, item_picture: models.ItemPicture):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.item_pictures(
            place_menu_item_id,
            picture_id,
            deleted_at
        )
        VALUES (
            %s,
            %s,
            %s
        );
        """,
        (
            item_picture.place_menu_item_id,
            item_picture.picture_id,
            get_deleted_at(item_picture.deleted),
        ),
    )


def insert_category_picture(
        database, category_picture: models.CategoryPicture,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.category_pictures(
            place_menu_category_id,
            picture_id,
            deleted_at
        )
        VALUES (
            %s,
            %s,
            %s
        );
        """,
        (
            category_picture.place_menu_category_id,
            category_picture.picture_id,
            get_deleted_at(category_picture.deleted),
        ),
    )


def insert_brand_inner_option(
        database,
        brand_menu_item_inner_option: models.BrandMenuItemInnerOption,
) -> str:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.brand_menu_item_inner_options(
            brand_id,
            origin_id,
            name,
            group_name,
            group_origin_id,
            min_amount,
            max_amount
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::TEXT;
        """,
        (
            brand_menu_item_inner_option.brand_id,
            brand_menu_item_inner_option.origin_id,
            brand_menu_item_inner_option.name,
            brand_menu_item_inner_option.group_name,
            brand_menu_item_inner_option.group_origin_id,
            brand_menu_item_inner_option.min_amount,
            brand_menu_item_inner_option.max_amount,
        ),
    )
    return cursor.fetchone()[0]


def insert_place_inner_option(
        database,
        place_menu_item_inner_option: models.PlaceMenuItemInnerOption,
) -> int:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_inner_options(
            brand_menu_item_inner_option,
            place_menu_item_id,
            origin_id,
            legacy_id,
            name,
            group_name,
            group_origin_id,
            min_amount,
            max_amount,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::BIGINT;
        """,
        (
            place_menu_item_inner_option.brand_menu_item_inner_option,
            place_menu_item_inner_option.place_menu_item_id,
            place_menu_item_inner_option.origin_id,
            place_menu_item_inner_option.legacy_id,
            place_menu_item_inner_option.name,
            place_menu_item_inner_option.group_name,
            place_menu_item_inner_option.group_origin_id,
            place_menu_item_inner_option.min_amount,
            place_menu_item_inner_option.max_amount,
            get_deleted_at(place_menu_item_inner_option.deleted),
            place_menu_item_inner_option.updated_at,
        ),
    )
    return cursor.fetchone()[0]


def insert_brand_option_group(
        database,
        brand_menu_item_option_group: models.BrandMenuItemOptionGroup,
) -> str:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.brand_menu_item_option_groups(
            brand_id,
            origin_id,
            name,
            min_selected_options,
            max_selected_options
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::TEXT;
        """,
        (
            brand_menu_item_option_group.brand_id,
            brand_menu_item_option_group.origin_id,
            brand_menu_item_option_group.name,
            brand_menu_item_option_group.min_selected_options,
            brand_menu_item_option_group.max_selected_options,
        ),
    )
    return cursor.fetchone()[0]


def insert_place_option_group(
        database,
        place_menu_item_option_group: models.PlaceMenuItemOptionGroup,
) -> int:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_option_groups(
            brand_menu_item_option_group,
            place_menu_item_id,
            origin_id,
            legacy_id,
            name,
            sort,
            min_selected_options,
            max_selected_options,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::BIGINT;
        """,
        (
            place_menu_item_option_group.brand_menu_item_option_group,
            place_menu_item_option_group.place_menu_item_id,
            place_menu_item_option_group.origin_id,
            place_menu_item_option_group.legacy_id,
            place_menu_item_option_group.name,
            place_menu_item_option_group.sort,
            place_menu_item_option_group.min_selected_options,
            place_menu_item_option_group.max_selected_options,
            get_deleted_at(place_menu_item_option_group.deleted),
            place_menu_item_option_group.updated_at,
        ),
    )
    return cursor.fetchone()[0]


def insert_brand_menu_item_option(
        database, brand_menu_item_option: models.BrandMenuItemOption,
) -> str:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.brand_menu_item_options(
            brand_id,
            origin_id,
            name,
            multiplier,
            min_amount,
            max_amount,
            sort
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::TEXT;
        """,
        (
            brand_menu_item_option.brand_id,
            brand_menu_item_option.origin_id,
            brand_menu_item_option.name,
            brand_menu_item_option.multiplier,
            brand_menu_item_option.min_amount,
            brand_menu_item_option.max_amount,
            brand_menu_item_option.sort,
        ),
    )
    return cursor.fetchone()[0]


def insert_place_menu_item_option(
        database, place_menu_item_option: models.PlaceMenuItemOption,
) -> int:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_options(
            brand_menu_item_option,
            place_menu_item_option_group_id,
            origin_id,
            legacy_id,
            name,
            multiplier,
            min_amount,
            max_amount,
            sort,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::BIGINT;
        """,
        (
            place_menu_item_option.brand_menu_item_option,
            place_menu_item_option.place_menu_item_option_group_id,
            place_menu_item_option.origin_id,
            place_menu_item_option.legacy_id,
            place_menu_item_option.name,
            place_menu_item_option.multiplier,
            place_menu_item_option.min_amount,
            place_menu_item_option.max_amount,
            place_menu_item_option.sort,
            get_deleted_at(place_menu_item_option.deleted),
            place_menu_item_option.updated_at,
        ),
    )
    return cursor.fetchone()[0]


def insert_option_price(
        database,
        place_menu_item_option_price: models.PlaceMenuItemOptionPrice,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_option_prices(
            place_menu_item_option_id,
            price,
            promo_price,
            vat,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            place_menu_item_option_price.place_menu_item_option_id,
            place_menu_item_option_price.price,
            place_menu_item_option_price.promo_price,
            place_menu_item_option_price.vat,
            get_deleted_at(place_menu_item_option_price.deleted),
            place_menu_item_option_price.updated_at,
        ),
    )


def insert_brand_menu_category(
        database, brand_menu_category: models.BrandMenuCategory,
) -> str:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.brand_menu_categories(
            brand_id,
            origin_id,
            name
        )
        VALUES (
            %s,
            %s,
            %s
        )
        RETURNING id::TEXT;
        """,
        (
            brand_menu_category.brand_id,
            brand_menu_category.origin_id,
            brand_menu_category.name,
        ),
    )
    return cursor.fetchone()[0]


def insert_place_menu_category(
        database, place_menu_category: models.PlaceMenuCategory,
) -> int:
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_categories(
            brand_menu_category_id,
            place_id,
            origin_id,
            sort,
            legacy_id,
            name,
            schedule,
            deleted_at,
            updated_at,
            is_synced_schedule
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id::BIGINT;
        """,
        (
            place_menu_category.brand_menu_category_id,
            place_menu_category.place_id,
            place_menu_category.origin_id,
            place_menu_category.sort,
            place_menu_category.legacy_id,
            place_menu_category.name,
            json.dumps(place_menu_category.schedule)
            if place_menu_category.schedule
            else None,
            place_menu_category.deleted_at,
            place_menu_category.updated_at,
            place_menu_category.synced_schedule,
        ),
    )
    return cursor.fetchone()[0]


def get_place_menu_categories(
        database, place_id: int,
) -> typing.List[models.PlaceMenuCategory]:
    cursor = database.cursor()
    cursor.execute(
        """
            SELECT
                id,
                place_id,
                origin_id,
                sort,
                legacy_id,
                name,
                schedule,
                deleted_at,
                updated_at
            FROM eats_rest_menu_storage.place_menu_categories
            WHERE place_id = %s;
            """,
        (place_id,),
    )

    result = []
    for row in list(cursor):
        deleted_at = None
        if row[7]:
            deleted_at = row[7].strftime('%Y-%m-%dT%H:%M:%S%z')
        result.append(
            models.PlaceMenuCategory(
                brand_menu_category_id=matching.any_string,
                category_id=str(row[0]),
                place_id=row[1],
                origin_id=row[2],
                sort=row[3],
                legacy_id=row[4],
                name=row[5],
                schedule=row[6],
                deleted_at=deleted_at,
                updated_at=row[8].strftime('%Y-%m-%dT%H:%M:%S%z'),
            ),
        )

    return result


def insert_place_menu_item_stock(
        database, place_menu_item_stock: models.PlaceMenuItemStock,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_stocks(
            place_menu_item_id,
            stock,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            place_menu_item_stock.place_menu_item_id,
            place_menu_item_stock.stock,
            get_deleted_at(place_menu_item_stock.deleted),
            place_menu_item_stock.updated_at,
        ),
    )


def insert_option_status(
        database,
        place_menu_item_option_status: models.PlaceMenuItemOptionStatus,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_option_statuses(
            place_menu_item_option_id,
            active,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            place_menu_item_option_status.place_menu_item_option_id,
            place_menu_item_option_status.active,
            get_deleted_at(place_menu_item_option_status.deleted),
            place_menu_item_option_status.updated_at,
        ),
    )


def insert_place_menu_item_status(
        database, place_menu_item_status: models.PlaceMenuItemStatus,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_statuses(
            place_menu_item_id,
            active,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            place_menu_item_status.place_menu_item_id,
            place_menu_item_status.active,
            get_deleted_at(place_menu_item_status.deleted),
            place_menu_item_status.updated_at,
        ),
    )


def insert_category_status(
        database, place_menu_category_status: models.PlaceMenuCategoryStatus,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_category_statuses(
            place_menu_category_id,
            active,
            deleted_at,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            place_menu_category_status.place_menu_category_id,
            place_menu_category_status.active,
            get_deleted_at(place_menu_category_status.deleted),
            place_menu_category_status.updated_at,
        ),
    )


def insert_item_category(
        database, place_menu_item_category: models.PlaceMenuItemCategory,
):
    cursor = database.cursor()
    cursor.execute(
        """
        INSERT INTO eats_rest_menu_storage.place_menu_item_categories (
            place_id,
            place_menu_category_id,
            place_menu_item_id,
            deleted_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        );
        """,
        (
            place_menu_item_category.place_id,
            place_menu_item_category.place_menu_category_id,
            place_menu_item_category.place_menu_item_id,
            get_deleted_at(place_menu_item_category.deleted),
        ),
    )
