from tests_eats_nomenclature_viewer.sql_adaptor.getters import base
from tests_eats_nomenclature_viewer import models

SQL_SELECT_CATEGORY = """
select
    id,
    nmn_id,
    origin_id,
    assortment_id,
    name,
    type,
    updated_at
from eats_nomenclature_viewer.categories
"""

SQL_SELECT_CATEGORY_RELATION = """
select
    assortment_id,
    category_id,
    parent_category_id,
    sort_order,
    updated_at
from eats_nomenclature_viewer.categories_relations
"""

SQL_SELECT_CATEGORY_IMAGE = """
select
    assortment_id,
    category_id,
    image_id,
    sort_order,
    updated_at
from eats_nomenclature_viewer.categories_images
"""

SQL_SELECT_CATEGORY_PRODUCT = """
select
    assortment_id,
    category_id,
    product_nmn_id,
    sort_order,
    updated_at
from eats_nomenclature_viewer.categories_products
"""

SQL_SELECT_PLACE_CATEGORY = """
select
    assortment_id,
    place_id,
    category_id,
    active_items_count,
    created_at,
    updated_at
from eats_nomenclature_viewer.places_categories
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.Category: self._load_all_categories,
            models.PlaceCategory: self._load_all_place_categories,
        }

    def get_load_single_getters(self):
        return {}

    def _load_all_categories(self):
        return list(self._load_all_categories_raw().values())

    def _load_all_categories_raw(self):
        pg_cursor = self._pg_cursor

        pg_cursor.execute(SQL_SELECT_CATEGORY)
        db_categories = pg_cursor.fetchall()

        # load all categories first
        id_to_category = {}
        for db_category in db_categories:
            category_id = db_category['id']
            db_category.pop('id')

            db_category['assortment'] = self._parent.load_single(
                models.Assortment, db_category['assortment_id'],
            )
            db_category.pop('assortment_id')

            db_category['type'] = models.CategoryType(db_category['type'])

            id_to_category[category_id] = models.Category(**db_category)

        # than set their relations
        pg_cursor.execute(SQL_SELECT_CATEGORY_RELATION)
        db_category_relations = {
            i['category_id']: i for i in pg_cursor.fetchall()
        }
        for category_id, category in id_to_category.items():
            db_category_relation = db_category_relations[category_id]
            parent_category_id = db_category_relation['parent_category_id']
            parent_category = (
                id_to_category[parent_category_id]
                if parent_category_id
                else None
            )
            category.category_relation = models.CategoryRelation(
                category=category,
                parent_category=parent_category,
                sort_order=db_category_relation['sort_order'],
                updated_at=db_category_relation['updated_at'],
            )

        for category_id, category in id_to_category.items():
            category.category_images = self._load_category_images(category_id)

        for category_id, category in id_to_category.items():
            category.category_products = self._load_category_products(
                category_id,
            )

        return id_to_category

    def _load_category_images(self, category_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(
            SQL_SELECT_CATEGORY_IMAGE + 'where category_id = %s',
            (category_id,),
        )

        category_images = []
        for db_image in pg_cursor.fetchall():
            db_image.pop('category_id')
            db_image.pop('assortment_id')

            db_image['image'] = self._parent.load_single(
                models.Image, db_image['image_id'],
            )
            db_image.pop('image_id')

            category_images.append(models.CategoryImage(**db_image))

        return category_images

    def _load_category_products(self, category_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(
            SQL_SELECT_CATEGORY_PRODUCT + 'where category_id = %s',
            (category_id,),
        )

        category_products = []
        for db_product in pg_cursor.fetchall():
            db_product.pop('category_id')
            db_product.pop('assortment_id')

            db_product['product'] = self._parent.load_single(
                models.Product, db_product['product_nmn_id'],
            )
            db_product.pop('product_nmn_id')

            category_products.append(models.CategoryProduct(**db_product))

        return category_products

    def _load_all_place_categories(self):
        pg_cursor = self._pg_cursor

        pg_cursor.execute(SQL_SELECT_PLACE_CATEGORY)
        db_place_categories = pg_cursor.fetchall()

        id_to_category = self._load_all_categories_raw()

        place_categories = []
        for db_place_category in db_place_categories:
            db_place_category.pop('assortment_id')

            db_place_category['category'] = id_to_category[
                db_place_category['category_id']
            ]
            db_place_category.pop('category_id')

            place_categories.append(models.PlaceCategory(**db_place_category))

        return place_categories
