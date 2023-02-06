from tests_eats_nomenclature_viewer import models
from tests_eats_nomenclature_viewer.sql_adaptor.getters import base

SQL_SELECT_PLACE_AVAILABILITY_FILE = """
select
    place_id,
    file_path,
    file_datetime,
    updated_at
from eats_nomenclature_viewer.place_availability_files
"""

SQL_SELECT_PLACE_FALLBACK_FILE = """
select
    place_id,
    task_type,
    file_path,
    file_datetime,
    updated_at
from eats_nomenclature_viewer.place_fallback_files
"""

SQL_SELECT_PLACE_TASK_STATUS = """
select
    place_id,
    task_type,
    task_started_at,
    task_is_in_progress,
    task_finished_at,
    updated_at
from eats_nomenclature_viewer.place_task_statuses
"""

SQL_SELECT_PLACE_ENRICHMENT_STATUS = """
select
    place_id,
    are_prices_ready,
    are_stocks_ready,
    is_vendor_data_ready,
    updated_at
from eats_nomenclature_viewer.place_enrichment_statuses
"""


class SqlGetterImpl(base.SqlGetterImplBase):
    def get_load_all_getters(self):
        return {
            models.PlaceAvailabilityFile: (
                self._load_all_place_availability_files
            ),
            models.PlaceFallbackFile: self._load_all_place_fallback_files,
            models.PlaceTaskStatus: self._load_all_place_task_statuses,
            models.PlaceEnrichmentStatus: (
                self._load_all_place_enrichment_statuses
            ),
        }

    def get_load_single_getters(self):
        return {}

    def _load_all_place_availability_files(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_AVAILABILITY_FILE)

        return [
            models.PlaceAvailabilityFile(**i) for i in pg_cursor.fetchall()
        ]

    def _load_all_place_fallback_files(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_FALLBACK_FILE)

        db_data = pg_cursor.fetchall()
        for i in db_data:
            i['task_type'] = models.PlaceTaskType(i['task_type'])

        return [models.PlaceFallbackFile(**i) for i in db_data]

    def _load_all_place_task_statuses(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_TASK_STATUS)

        db_data = pg_cursor.fetchall()
        for i in db_data:
            i['task_type'] = models.PlaceTaskType(i['task_type'])

        return [models.PlaceTaskStatus(**i) for i in db_data]

    def _load_all_place_enrichment_statuses(self):
        pg_cursor = self._pg_cursor
        pg_cursor.execute(SQL_SELECT_PLACE_ENRICHMENT_STATUS)

        return [
            models.PlaceEnrichmentStatus(**i) for i in pg_cursor.fetchall()
        ]
