from tests_eats_nomenclature_viewer.sql_adaptor.getters import base
from tests_eats_nomenclature_viewer import models

SQL_SELECT_PRODUCT = """
select
    nmn_id,
    brand_id,
    origin_id,
    sku_id,
    name,
    quantum,
    measure_unit,
    measure_value,
    updated_at
from eats_nomenclature_viewer.products
"""

SQL_SELECT_PRODUCT_IMAGE = """
select
    image_id,
    sort_order,
    updated_at
from eats_nomenclature_viewer.product_images
"""

SQL_SELECT_PRODUCT_ATTRIBUTE = """
select
    attribute_id,
    attribute_value,
    updated_at
from eats_nomenclature_viewer.product_attributes
"""

SQL_SELECT_ATTRIBUTE = """
select
    name,
    updated_at
from eats_nomenclature_viewer.attributes
"""

SQL_SELECT_PRODUCT_USAGE = """
select
    product_nmn_id,
    last_referenced_at,
    updated_at,
    created_at
from eats_nomenclature_viewer.product_usage
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.Attribute: self._load_all_attributes,
            models.Product: self._load_all_products,
            models.ProductAttribute: self._load_all_product_attributes,
            models.ProductImage: self._load_all_product_images,
            models.ProductUsage: self._load_all_product_usage,
        }

    def get_load_single_getters(self):
        return {
            models.Attribute: self._load_attribute,
            models.Product: self._load_product,
        }

    def _load_all_products(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PRODUCT)

        return [self._load_product_impl(i) for i in pg_cursor.fetchall()]

    def _load_product(self, nmn_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PRODUCT + 'where nmn_id = %s', (nmn_id,))

        return self._load_product_impl(pg_cursor.fetchone())

    def _load_all_product_images(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PRODUCT_IMAGE)

        product_images = []
        for db_image in pg_cursor.fetchall():
            image = self._parent.load_single(
                models.Image, db_image['image_id'],
            )
            db_image.pop('image_id')
            product_images.append(models.ProductImage(image=image, **db_image))

        return product_images

    def _load_all_product_attributes(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PRODUCT_ATTRIBUTE)

        product_images = []
        for db_attribute in pg_cursor.fetchall():
            attribute = self._parent.load_single(
                models.Attribute, db_attribute['attribute_id'],
            )
            db_attribute.pop('attribute_id')
            product_images.append(
                models.ProductAttribute(attribute=attribute, **db_attribute),
            )

        return product_images

    def _load_all_attributes(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_ATTRIBUTE)

        return [models.Attribute(**i) for i in pg_cursor.fetchall()]

    def _load_all_product_usage(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PRODUCT_USAGE)

        return [models.ProductUsage(**i) for i in pg_cursor.fetchall()]

    def _load_product_images(self, product_nmn_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(
            SQL_SELECT_PRODUCT_IMAGE + 'where product_nmn_id = %s',
            (product_nmn_id,),
        )

        product_images = []
        for db_image in pg_cursor.fetchall():
            image = self._parent.load_single(
                models.Image, db_image['image_id'],
            )
            db_image.pop('image_id')
            product_images.append(models.ProductImage(image=image, **db_image))

        return product_images

    def _load_product_attributes(self, product_nmn_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(
            SQL_SELECT_PRODUCT_ATTRIBUTE + 'where product_nmn_id = %s',
            (product_nmn_id,),
        )

        product_attributes = []
        for db_attribute in pg_cursor.fetchall():
            attribute = self._parent.load_single(
                models.Attribute, db_attribute['attribute_id'],
            )
            db_attribute.pop('attribute_id')
            product_attributes.append(
                models.ProductAttribute(attribute=attribute, **db_attribute),
            )

        return product_attributes

    def _load_attribute(self, attribute_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(
            SQL_SELECT_ATTRIBUTE + 'where id = %s', (attribute_id,),
        )

        return models.Attribute(**pg_cursor.fetchone())

    def _load_product_impl(self, db_product):
        product = models.Product(**db_product)
        product.product_images = self._load_product_images(product.nmn_id)
        product.product_attributes = self._load_product_attributes(
            product.nmn_id,
        )

        return product
