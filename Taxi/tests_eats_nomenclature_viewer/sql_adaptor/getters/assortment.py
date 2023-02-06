from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer.sql_adaptor.getters import base


SQL_SELECT_ASSORTMENT = """
select
    id as assortment_id,
    updated_at,
    created_at
from eats_nomenclature_viewer.assortments
"""

SQL_SELECT_ASSORTMENT_NAME = """
select
    id,
    name,
    updated_at
from eats_nomenclature_viewer.assortment_names
"""

SQL_SELECT_PLACE_ASSORTMENT = """
select
    place_id,
    assortment_name_id,
    active_assortment_id,
    in_progress_assortment_id,
    updated_at
from eats_nomenclature_viewer.place_assortments
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.AssortmentName: self._load_all_assortment_names,
            models.PlaceAssortment: self._load_all_place_assortments,
        }

    def get_load_single_getters(self):
        return {
            models.Assortment: self._load_assortment,
            models.AssortmentName: self._load_assortment_name,
        }

    def get_object_id_getters(self):
        return {models.AssortmentName: self._get_assortment_name_id}

    def _load_all_place_assortments(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_ASSORTMENT)

        place_assortments = []
        for db_place_assortment in pg_cursor.fetchall():
            assortment_name = self._parent.load_single(
                models.AssortmentName,
                db_place_assortment['assortment_name_id'],
            )
            db_place_assortment.pop('assortment_name_id')

            active_assortment = (
                self._parent.load_single(
                    models.Assortment,
                    db_place_assortment['active_assortment_id'],
                )
                if db_place_assortment['active_assortment_id']
                else None
            )
            db_place_assortment.pop('active_assortment_id')

            in_progress_assortment = (
                self._parent.load_single(
                    models.Assortment,
                    db_place_assortment['in_progress_assortment_id'],
                )
                if db_place_assortment['in_progress_assortment_id']
                else None
            )
            db_place_assortment.pop('in_progress_assortment_id')
            place_assortments.append(
                models.PlaceAssortment(
                    assortment_name=assortment_name,
                    active_assortment=active_assortment,
                    in_progress_assortment=in_progress_assortment,
                    **db_place_assortment,
                ),
            )

        return place_assortments

    def _load_all_assortment_names_raw(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_ASSORTMENT_NAME)

        return pg_cursor.fetchall()

    def _load_all_assortment_names(self):
        db_data = self._load_all_assortment_names_raw()
        for i in db_data:
            i.pop('id')

        return [models.AssortmentName(**i) for i in db_data]

    def _load_assortment_name(self, assortment_name_id):
        db_assortment_name = [
            i
            for i in self._load_all_assortment_names_raw()
            if i['id'] == assortment_name_id
        ][0]
        db_assortment_name.pop('id')

        return models.AssortmentName(**db_assortment_name)

    def _get_assortment_name_id(self, assortment_name: models.AssortmentName):
        db_assortment_name = [
            i
            for i in self._load_all_assortment_names_raw()
            if i['name'] == assortment_name.name
        ][0]
        return db_assortment_name['id']

    def _load_assortment(self, assortment_id):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(
            SQL_SELECT_ASSORTMENT + 'where id = %s', (assortment_id,),
        )

        return models.Assortment(**pg_cursor.fetchone())
