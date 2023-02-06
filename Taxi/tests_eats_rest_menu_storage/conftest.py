import decimal
import typing

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_rest_menu_storage_plugins import *  # noqa: F403 F401

from tests_eats_rest_menu_storage import models
from tests_eats_rest_menu_storage import sql
from tests_eats_rest_menu_storage.menu_update import handler


@pytest.fixture(name='update_menu_handler')
def _update_menu_handler(taxi_eats_rest_menu_storage):
    async def do_request(
            place_id: int,
            categories: typing.Optional[
                typing.List[handler.UpdateCategory]
            ] = None,
            items: typing.Optional[typing.List[handler.UpdateItem]] = None,
    ):
        raw_categories = []
        for category in categories or []:
            raw_categories.append(category.as_dict())

        raw_items = []
        for item in items or []:
            raw_items.append(item.as_dict())

        response = await taxi_eats_rest_menu_storage.post(
            '/internal/v1/update/menu',
            json={
                'place_id': place_id,
                'categories': raw_categories,
                'items': raw_items,
            },
        )
        return response

    return do_request


@pytest.fixture(name='database')
def _db(pgsql):
    return pgsql['eats_rest_menu_storage']


@pytest.fixture(name='sql_get_brand_menu_items')
def _sql_get_brand_menu_items(database):
    def do_sql_get_brand_menu_items(brand_id: int):
        cursor = database.cursor()
        cursor.execute(
            """
            SELECT
                origin_id,
                name,
                adult,
                description,
                weight_value,
                weight_unit
            FROM eats_rest_menu_storage.brand_menu_items
            WHERE brand_id = %s;
            """,
            (brand_id,),
        )
        return set(cursor)

    return do_sql_get_brand_menu_items


@pytest.fixture(name='sql_get_place_menu_items')
def _sql_get_place_menu_items(pgsql):
    def do_sql_get_place_menu_items(place_id: int):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            """
            SELECT
                bmi.origin_id,
                bmi.brand_id,
                pmi.origin_id,
                pmi.name,
                pmi.adult,
                pmi.description,
                pmi.weight_value,
                pmi.weight_unit,
                pmi.sort,
                pmi.shipping_types,
                pmi.legacy_id,
                pmi.ordinary,
                pmi.choosable,
                pmi.deleted_at is not null,
                pmi.short_name,
                pmi.updated_at
            FROM eats_rest_menu_storage.place_menu_items AS pmi
            INNER JOIN eats_rest_menu_storage.brand_menu_items AS bmi
                ON pmi.brand_menu_item_id = bmi.id
            WHERE place_id = %s;
            """,
            (place_id,),
        )
        return set(cursor)

    return do_sql_get_place_menu_items


@pytest.fixture(name='sql_get_place_menu_item_prices')
def _sql_get_place_menu_item_prices(pgsql):
    def do_sql_get_item_prices(place_id):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select origin_id, price, promo_price, vat,
                   pmip.deleted_at is not null
            from eats_rest_menu_storage.place_menu_items pmi
            join eats_rest_menu_storage.place_menu_item_prices pmip
            on pmi.id = pmip.place_menu_item_id
            where place_id = {place_id}
            """,
        )
        return set(cursor)

    return do_sql_get_item_prices


@pytest.fixture(name='sql_get_place_menu_item_pictures')
def _sql_get_place_menu_item_pictures(pgsql):
    def do_sql_get_item_pictures(place_id):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select origin_id, url, ratio, ip.deleted_at is not null
            from eats_rest_menu_storage.place_menu_items pmi
              join eats_rest_menu_storage.item_pictures ip
                on pmi.id = ip.place_menu_item_id
              join eats_rest_menu_storage.pictures p
                on p.id = ip.picture_id
            where place_id = {place_id}
            """,
        )
        return set(cursor)

    return do_sql_get_item_pictures


@pytest.fixture(name='sql_get_brand_item_inner_options')
def _sql_get_brand_item_inner_options(pgsql):
    def do_sql_get_brand_inner_options(brand_id: int):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            """
            SELECT
                origin_id,
                name,
                group_name,
                group_origin_id,
                min_amount,
                max_amount
            FROM eats_rest_menu_storage.brand_menu_item_inner_options
            WHERE brand_id = %s;
            """,
            (brand_id,),
        )
        return set(cursor)

    return do_sql_get_brand_inner_options


@pytest.fixture(name='sql_get_place_item_inner_options')
def _sql_get_place_item_inner_options(pgsql):
    def do_sql_get_place_inner_options(place_id: int):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            """
            SELECT
                bmiio.origin_id,
                pmiio.place_menu_item_id,
                pmi.origin_id,
                pmiio.origin_id,
                pmiio.legacy_id,
                pmiio.name,
                pmiio.group_name,
                pmiio.group_origin_id,
                pmiio.min_amount,
                pmiio.max_amount,
                pmiio.deleted_at is not null,
                pmiio.updated_at
            FROM eats_rest_menu_storage.place_menu_item_inner_options AS pmiio
            INNER JOIN eats_rest_menu_storage.brand_menu_item_inner_options AS
                bmiio ON pmiio.brand_menu_item_inner_option = bmiio.id
            INNER JOIN eats_rest_menu_storage.place_menu_items AS pmi
                ON pmi.id = pmiio.place_menu_item_id
            WHERE place_id = %s;
            """,
            (place_id,),
        )
        return set(cursor)

    return do_sql_get_place_inner_options


@pytest.fixture(name='sql_get_brand_item_option_groups')
def _sql_get_brand_item_option_groups(database):
    def do_get_brand_option_groups(brand_id: int):
        cursor = database.cursor()
        cursor.execute(
            """
            SELECT
                origin_id,
                name,
                min_selected_options,
                max_selected_options
            FROM eats_rest_menu_storage.brand_menu_item_option_groups
            WHERE brand_id = %s
            """,
            (brand_id,),
        )
        return set(cursor)

    return do_get_brand_option_groups


@pytest.fixture(name='sql_get_place_item_option_groups')
def _sql_get_place_item_option_groups(database):
    def do_get_place_option_groups(place_id: int):
        cursor = database.cursor()
        cursor.execute(
            """
            SELECT
                bmiog.origin_id,
                pmi.origin_id,
                pmiog.origin_id,
                pmiog.is_required,
                pmiog.legacy_id,
                pmiog.name,
                pmiog.sort,
                pmiog.min_selected_options,
                pmiog.max_selected_options,
                pmiog.deleted_at is not null,
                pmiog.updated_at
            FROM eats_rest_menu_storage.place_menu_item_option_groups AS pmiog
            INNER JOIN eats_rest_menu_storage.brand_menu_item_option_groups AS
                bmiog ON pmiog.brand_menu_item_option_group = bmiog.id
            INNER JOIN eats_rest_menu_storage.place_menu_items AS pmi
                ON pmi.id = pmiog.place_menu_item_id
            WHERE pmi.place_id = %s
            """,
            (place_id,),
        )
        return set(cursor)

    return do_get_place_option_groups


@pytest.fixture(name='sql_get_brand_item_options')
def _sql_get_brand_item_options(pgsql):
    def do_get_brand_options(brand_id):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select origin_id, name, multiplier, min_amount, max_amount, sort
            from eats_rest_menu_storage.brand_menu_item_options
            where brand_id = {brand_id}
            """,
        )
        return set(cursor)

    return do_get_brand_options


@pytest.fixture(name='sql_get_place_item_options')
def _sql_get_place_item_options(pgsql):
    def do_get_place_options(place_id):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select pmio.id,bmio.origin_id, pmiog.origin_id, pmi.origin_id,
                   pmio.origin_id, pmio.legacy_id, pmio.name, pmio.multiplier,
                   pmio.min_amount, pmio.max_amount, pmio.sort,
                   pmio.deleted_at is not null,
                   pmio.updated_at
            from eats_rest_menu_storage.place_menu_item_options pmio
            join eats_rest_menu_storage.brand_menu_item_options bmio
            on pmio.brand_menu_item_option = bmio.id
            join eats_rest_menu_storage.place_menu_item_option_groups pmiog
            on pmio.place_menu_item_option_group_id = pmiog.id
            join eats_rest_menu_storage.place_menu_items pmi
            on pmi.id = pmiog.place_menu_item_id
            where place_id = {place_id}
            """,
        )
        return set(cursor)

    return do_get_place_options


@pytest.fixture(name='sql_get_brand_menu_categories')
def _sql_get_brand_menu_categories(pgsql):
    def do_get_brand_categories(brand_id):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select origin_id, name
            from eats_rest_menu_storage.brand_menu_categories
            where brand_id = {brand_id}
            """,
        )
        return set(cursor)

    return do_get_brand_categories


@pytest.fixture(name='sql_get_item_option_prices')
def _sql_get_item_option_prices(pgsql):
    def do_get_item_option_prices(place_id):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select pmi.origin_id, pmiog.origin_id, pmio.origin_id,
                   price, promo_price, vat, pmiop.deleted_at is not null
            from eats_rest_menu_storage.place_menu_item_options pmio
            join eats_rest_menu_storage.place_menu_item_option_groups pmiog
            on pmio.place_menu_item_option_group_id = pmiog.id
            join eats_rest_menu_storage.place_menu_items pmi
            on pmi.id = pmiog.place_menu_item_id
            join eats_rest_menu_storage.place_menu_item_option_prices pmiop
            on pmiop.place_menu_item_option_id = pmio.id
            where place_id = {place_id}
            """,
        )
        return set(cursor)

    return do_get_item_option_prices


@pytest.fixture(name='sql_get_origin_id_uuid_mapping')
def _sql_get_origin_id_uuid_mapping(pgsql):
    def do_sql_get_id_mapping(table_name: str):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select origin_id, {sql.BRAND_ID_NAMES[table_name]}
            from eats_rest_menu_storage.{table_name}
            """,
        )
        return {str(row[0]): row[1] for row in cursor}

    return do_sql_get_id_mapping


@pytest.fixture(name='sql_get_item_categories')
def _sql_get_item_categories(pgsql):
    def do_sql_get_item_categories(place_id):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select c.origin_id, i.origin_id, ic.deleted_at is not null
            from eats_rest_menu_storage.place_menu_item_categories ic
            join eats_rest_menu_storage.place_menu_items i
            on ic.place_menu_item_id = i.id
            join eats_rest_menu_storage.place_menu_categories c
            on ic.place_menu_category_id = c.id
            where ic.place_id = {place_id}
            """,
        )
        return set(cursor)

    return do_sql_get_item_categories


@pytest.fixture(name='sql_get_item_stocks')
def _sql_get_item_stocks(pgsql):
    def do_sql_get_item_stocks(place_id: int):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            """
            SELECT
                pmi.origin_id,
                pmis.stock,
                pmis.deleted_at is not null
            FROM eats_rest_menu_storage.place_menu_item_stocks AS pmis
            INNER JOIN eats_rest_menu_storage.place_menu_items AS pmi
                ON pmis.place_menu_item_id = pmi.id
            WHERE pmi.place_id = %s;
            """,
            (place_id,),
        )
        return set(cursor)

    return do_sql_get_item_stocks


@pytest.fixture(name='sql_get_option_statuses')
def _sql_get_option_statuses(pgsql):
    def do_sql_get_option_statuses(with_updated_at: bool):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        select = """
            select pmio.id, origin_id, active, deactivated_at,
                   reactivate_at, pmios.deleted_at is not null
             """
        other = """
            from eats_rest_menu_storage.place_menu_item_options pmio
            join eats_rest_menu_storage.place_menu_item_option_statuses pmios
            on pmio.id = pmios.place_menu_item_option_id
             """
        if with_updated_at:
            select += ', pmios.updated_at '
        cursor.execute(select + other)
        return set(cursor)

    return do_sql_get_option_statuses


@pytest.fixture(name='sql_get_item_statuses')
def _sql_get_item_statuses(pgsql):
    def do_get_item_statuses(with_updated_at: bool):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        select = """
            select origin_id, active, deactivated_at,
                   reactivate_at, pmis.deleted_at is not null
            """
        other = """
            from eats_rest_menu_storage.place_menu_items pmi
            join eats_rest_menu_storage.place_menu_item_statuses pmis
            on pmi.id = pmis.place_menu_item_id
            """
        if with_updated_at:
            select += ', pmis.updated_at '
        cursor.execute(select + other)
        return set(cursor)

    return do_get_item_statuses


@pytest.fixture(name='sql_get_category_statuses')
def _sql_get_category_statuses(pgsql):
    def do_get_category_statuses(with_updated_at: bool):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        select = """
            select origin_id, active, deactivated_at,
                   reactivate_at, pmcs.deleted_at is not null
            """
        other = """
            from eats_rest_menu_storage.place_menu_categories pmc
            join eats_rest_menu_storage.place_menu_category_statuses pmcs
            on pmc.id = pmcs.place_menu_category_id
            """
        if with_updated_at:
            select += ', pmcs.updated_at '
        cursor.execute(select + other)
        return set(cursor)

    return do_get_category_statuses


@pytest.fixture(name='sql_uuid_origin_id_mapping')
def _sql_uuid_origin_id_mapping(pgsql):
    def do_sql_uuid_origin_id_mapping(table_name: str):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select {sql.BRAND_ID_NAMES[table_name]}, origin_id
            from eats_rest_menu_storage.{table_name}
            """,
        )
        return {str(row[0]): row[1] for row in cursor}

    return do_sql_uuid_origin_id_mapping


@pytest.fixture(name='sql_origin_id_uuid_mapping')
def _sql_origin_id_uuid_mapping(pgsql):
    def do_sql_origin_id_uuid_mapping(table_name: str):
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            f"""
            select origin_id, {sql.BRAND_ID_NAMES[table_name]}
            from eats_rest_menu_storage.{table_name}
            """,
        )
        return {str(row[0]): row[1] for row in cursor}

    return do_sql_origin_id_uuid_mapping


@pytest.fixture(name='sql_get_place_category_relation')
def _sql_get_place_category_relations(pgsql):
    def do_get_place_category_relations(
            place_id: int,
    ) -> typing.List[models.CategoryRelation]:
        cursor = pgsql['eats_rest_menu_storage'].cursor()
        cursor.execute(
            """
        SELECT
            category_id,
            parent_id,
            deleted_at IS NOT NULL
        FROM eats_rest_menu_storage.category_relations
        WHERE place_id = %s;
        """,
            (place_id,),
        )

        result = []
        for row in list(cursor):
            result.append(
                models.CategoryRelation(
                    place_id,
                    category_id=row[0],
                    parent_id=row[1],
                    deleted=row[2],
                ),
            )

        return result

    return do_get_place_category_relations


@pytest.fixture(name='eats_rest_menu_storage')
def eats_rest_menu_storage(database):
    class Context:
        def __init__(self):
            self.database = database

        def insert_brand_menu_categories(
                self, categories: typing.List[models.BrandMenuCategory],
        ) -> typing.Dict[typing.Tuple[int, str], str]:
            uuid_mapping = {}
            for category in categories:
                uuid_mapping[
                    (category.brand_id, category.origin_id)
                ] = sql.insert_brand_menu_category(self.database, category)
            return uuid_mapping

        def insert_brand_inner_options(
                self,
                inner_options: typing.List[models.BrandMenuItemInnerOption],
        ) -> typing.Dict[typing.Tuple[int, str], str]:
            uuid_mapping = {}
            for inner_option in inner_options:
                uuid_mapping[
                    (inner_option.brand_id, inner_option.origin_id)
                ] = sql.insert_brand_inner_option(self.database, inner_option)
            return uuid_mapping

        def insert_brand_option_groups(
                self,
                option_groups: typing.List[models.BrandMenuItemOptionGroup],
        ) -> typing.Dict[typing.Tuple[int, str], str]:
            uuid_mapping = {}
            for option_group in option_groups:
                uuid_mapping[
                    (option_group.brand_id, option_group.origin_id)
                ] = sql.insert_brand_option_group(self.database, option_group)
            return uuid_mapping

        def insert_brand_menu_item_options(
                self, item_options: typing.List[models.BrandMenuItemOption],
        ) -> typing.Dict[typing.Tuple[int, str], str]:
            uuid_mapping = {}
            for item_option in item_options:
                uuid_mapping[(item_option.brand_id, item_option.origin_id)] = (
                    sql.insert_brand_menu_item_option(
                        self.database, item_option,
                    )
                )
            return uuid_mapping

        def insert_brand_menu_items(
                self, items: typing.List[models.BrandMenuItem],
        ) -> typing.Dict[typing.Tuple[int, str], str]:
            uuid_mapping = {}
            for item in items:
                uuid_mapping[
                    (item.brand_id, item.origin_id)
                ] = sql.insert_brand_menu_item(self.database, item)
            return uuid_mapping

        def insert_brands(self, brands: typing.List[int]):
            for brand in brands:
                sql.insert_brand(self.database, brand)

        def insert_category_pictures(
                self,
                categories_to_pictures: typing.List[models.CategoryPicture],
        ):
            for category_to_picture in categories_to_pictures:
                sql.insert_category_picture(self.database, category_to_picture)

        def insert_category_relations(
                self, category_relations: typing.List[models.CategoryRelation],
        ):
            for category_relation in category_relations:
                sql.insert_place_category_relation(
                    self.database, category_relation,
                )

        def insert_item_pictures(
                self, items_to_pictures: typing.List[models.ItemPicture],
        ):
            for item_to_picture in items_to_pictures:
                sql.insert_item_picture(self.database, item_to_picture)

        def insert_pictures(
                self, pictures: typing.List[models.Picture],
        ) -> typing.Dict[typing.Tuple[str, typing.Optional[float]], int]:
            id_mapping = {}
            for picture in pictures:
                id_mapping[(picture.url, picture.ratio)] = sql.insert_picture(
                    self.database, picture,
                )
            return id_mapping

        def insert_place_menu_categories(
                self, categories: typing.List[models.PlaceMenuCategory],
        ) -> typing.Dict[typing.Tuple[int, str], int]:
            id_mapping = {}
            for category in categories:
                id_mapping[
                    (category.place_id, category.origin_id)
                ] = sql.insert_place_menu_category(self.database, category)
            return id_mapping

        def insert_category_statuses(
                self,
                categories_statuses: typing.List[
                    models.PlaceMenuCategoryStatus
                ],
        ):
            for category_status in categories_statuses:
                sql.insert_category_status(self.database, category_status)

        def insert_item_categories(
                self,
                items_to_categories: typing.List[models.PlaceMenuItemCategory],
        ):
            for item_to_category in items_to_categories:
                sql.insert_item_category(self.database, item_to_category)

        def insert_item_inner_options(
                self,
                inner_options: typing.List[models.PlaceMenuItemInnerOption],
        ) -> typing.Dict[typing.Tuple[int, str], int]:
            id_mapping = {}
            for inner_option in inner_options:
                id_mapping[
                    (inner_option.place_menu_item_id, inner_option.origin_id)
                ] = sql.insert_place_inner_option(self.database, inner_option)
            return id_mapping

        def insert_item_option_groups(
                self,
                option_groups: typing.List[models.PlaceMenuItemOptionGroup],
        ) -> typing.Dict[typing.Tuple[int, str], int]:
            id_mapping = {}
            for option_group in option_groups:
                id_mapping[
                    (option_group.place_menu_item_id, option_group.origin_id)
                ] = sql.insert_place_option_group(self.database, option_group)
            return id_mapping

        def insert_item_option_prices(
                self,
                option_prices: typing.List[models.PlaceMenuItemOptionPrice],
        ):
            for option_price in option_prices:
                sql.insert_option_price(self.database, option_price)

        def insert_item_option_statuses(
                self,
                option_statuses: typing.List[models.PlaceMenuItemOptionStatus],
        ):
            for option_status in option_statuses:
                sql.insert_option_status(self.database, option_status)

        def insert_place_menu_item_options(
                self, options: typing.List[models.PlaceMenuItemOption],
        ) -> typing.Dict[typing.Tuple[int, str], int]:
            id_mapping = {}
            for option in options:
                id_mapping[
                    (option.place_menu_item_option_group_id, option.origin_id)
                ] = sql.insert_place_menu_item_option(self.database, option)
            return id_mapping

        def insert_place_menu_item_prices(
                self, item_prices: typing.List[models.PlaceMenuItemPrice],
        ):
            for item_price in item_prices:
                sql.insert_place_menu_item_price(self.database, item_price)

        def insert_place_menu_item_statuses(
                self, item_statuses: typing.List[models.PlaceMenuItemStatus],
        ):
            for item_status in item_statuses:
                sql.insert_place_menu_item_status(self.database, item_status)

        def insert_place_menu_item_stocks(
                self, item_stocks: typing.List[models.PlaceMenuItemStock],
        ):
            for item_stock in item_stocks:
                sql.insert_place_menu_item_stock(self.database, item_stock)

        def insert_place_menu_items(
                self, items: typing.List[models.PlaceMenuItem],
        ) -> typing.Dict[typing.Tuple[int, str], int]:
            id_mapping = {}
            for item in items:
                id_mapping[
                    (item.place_id, item.origin_id)
                ] = sql.insert_place_menu_item(self.database, item)
            return id_mapping

        def insert_places(self, places: typing.List[models.Place]):
            for place in places:
                sql.insert_place(self.database, place)

    ctx = Context()
    return ctx


@pytest.fixture(name='place_menu_db')
def place_menu_db(
        eats_rest_menu_storage,
):  # pylint: disable=redefined-outer-name
    """
    Возвращает объект для манипуляций с данныи конкретного плейса
    добавляет сущности как в brand_*, так и в place_* таблицы
    """

    class Context:
        def __init__(self, place_id: int, brand_id: int):
            self.db = eats_rest_menu_storage
            self.place_id = place_id
            self.brand_id = brand_id
            self.db.insert_brands([self.brand_id])
            self.db.insert_places(
                [
                    models.Place(
                        place_id=self.place_id,
                        brand_id=self.brand_id,
                        slug=f'slug_{place_id}',
                    ),
                ],
            )

        def __take(self, mapping) -> int:
            """ Извлекает один id из дикста с мапингами"""
            return int(list(mapping.values())[0])

        def add_category(
                self,
                category: models.PlaceMenuCategory,
                return_brand_id: bool = False,
        ):
            brand_ids = self.db.insert_brand_menu_categories(
                [
                    models.BrandMenuCategory(
                        brand_id=self.brand_id,
                        origin_id=category.origin_id,
                        name=category.name or '',
                    ),
                ],
            )
            category.brand_menu_category_id = brand_ids[
                (self.brand_id, category.origin_id)
            ]
            mapping = self.db.insert_place_menu_categories([category])
            if return_brand_id:
                return category.brand_menu_category_id
            return self.__take(mapping)

        def add_item(
                self,
                category_id: int,
                item: models.PlaceMenuItem,
                price: models.PlaceMenuItemPrice = None,
                picture: models.Picture = None,
        ):
            brand_ids = self.db.insert_brand_menu_items(
                [
                    models.BrandMenuItem(
                        brand_id=self.brand_id,
                        origin_id=item.origin_id,
                        name=item.name
                        or 'brand_name_{}'.format(item.origin_id),
                    ),
                ],
            )
            item.brand_menu_item_id = brand_ids[
                (self.brand_id, item.origin_id)
            ]
            mapping = self.db.insert_place_menu_items([item])
            item_id = self.__take(mapping)
            self.db.insert_item_categories(
                [
                    models.PlaceMenuItemCategory(
                        place_id=self.place_id,
                        place_menu_category_id=category_id,
                        place_menu_item_id=item_id,
                    ),
                ],
            )
            self.db.insert_place_menu_item_prices(
                [
                    price
                    or models.PlaceMenuItemPrice(
                        item_id, decimal.Decimal(500),
                    ),
                ],
            )

            if picture:
                picture_mapping = self.db.insert_pictures([picture])
                picture_id = self.__take(picture_mapping)
                self.db.insert_item_pictures(
                    [
                        models.ItemPicture(
                            place_menu_item_id=item_id,
                            picture_id=picture_id,
                            deleted=False,
                        ),
                    ],
                )
            return item_id

        def add_inner_option(
                self, inner_option: models.PlaceMenuItemInnerOption,
        ):
            brand_ids = self.db.insert_brand_inner_options(
                [
                    models.BrandMenuItemInnerOption(
                        brand_id=self.brand_id,
                        origin_id=inner_option.origin_id,
                        name=inner_option.name,
                        group_name=inner_option.group_name,
                        group_origin_id=inner_option.group_origin_id,
                    ),
                ],
            )
            inner_option.brand_menu_item_inner_option = brand_ids[
                (self.brand_id, inner_option.origin_id)
            ]
            mapping = self.db.insert_item_inner_options([inner_option])
            return self.__take(mapping)

        def add_option_group(
                self, option_group: models.PlaceMenuItemOptionGroup,
        ):
            brand_ids = self.db.insert_brand_option_groups(
                [
                    models.BrandMenuItemOptionGroup(
                        brand_id=self.brand_id,
                        origin_id=option_group.origin_id,
                        name=option_group.name or '',
                        min_selected_options=option_group.min_selected_options,
                        max_selected_options=option_group.max_selected_options,
                    ),
                ],
            )
            option_group.brand_menu_item_option_group = brand_ids[
                (self.brand_id, option_group.origin_id)
            ]
            mapping = self.db.insert_item_option_groups([option_group])
            return self.__take(mapping)

        def add_option(self, option: models.PlaceMenuItemOption):
            brand_ids = self.db.insert_brand_menu_item_options(
                [
                    models.BrandMenuItemOption(
                        brand_id=self.brand_id,
                        origin_id=option.origin_id,
                        name=option.name or '',
                    ),
                ],
            )
            option.brand_menu_item_option = brand_ids[
                (self.brand_id, option.origin_id)
            ]
            mapping = self.db.insert_place_menu_item_options([option])
            return self.__take(mapping)

    return Context


@pytest.fixture(name='menu_item_watcher')
def menu_item_watcher(database):  # pylint: disable=redefined-outer-name
    """
    Возвращает объект для манипуляций с данными таблицы
    menu_item_watcher_cursor
    """

    class Context:
        def __init__(self):
            self.db = database

        def set(self, updated_at: str, item_id: int):
            cursor = self.db.cursor()
            cursor.execute(
                """
                INSERT INTO eats_rest_menu_storage.menu_item_watcher_cursor (
                    id,
                    updated_at,
                    menu_item_id
                ) VALUES (
                 %s,
                 %s,
                 %s
                )""",
                (1, updated_at, item_id),
            )

    ctx = Context()

    return ctx
