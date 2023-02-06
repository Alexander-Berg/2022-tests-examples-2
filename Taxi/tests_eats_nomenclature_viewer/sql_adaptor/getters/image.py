from tests_eats_nomenclature_viewer.sql_adaptor.getters import base
from tests_eats_nomenclature_viewer import models

SQL_SELECT_IMAGE = """
select
    url,
    updated_at
from eats_nomenclature_viewer.images
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {models.Image: self._load_all_images}

    def get_load_single_getters(self):
        return {models.Image: self._load_image}

    def _load_all_images(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_IMAGE)

        return [models.Image(**i) for i in pg_cursor.fetchall()]

    def _load_image(self, image_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_IMAGE + 'where id = %s', (image_id,))

        return models.Image(**pg_cursor.fetchone())
