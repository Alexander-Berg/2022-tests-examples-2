class OpenedDepotsProcessing:
    UPSERT_SQL = """
    INSERT INTO catalog_wms.opened_depots_processing (
        depot_id,
        processed
    )
    VALUES (
        %s, %s
    )
    ON CONFLICT(depot_id)
    DO UPDATE SET
        depot_id = EXCLUDED.depot_id,
        processed = EXCLUDED.processed
    ;
    """

    SELECT_SQL = """
    SELECT
        depot_id,
        processed
    FROM catalog_wms.opened_depots_processing
    WHERE depot_id = %s;
    """

    def __init__(self, pgsql, depot_id, processed=None, insert_in_pg=True):
        self.pg_db = pgsql['overlord_catalog']
        self.depot_id = depot_id
        self.processed = processed

        if insert_in_pg:
            self._update_db()

    def _update_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(self.UPSERT_SQL, [self.depot_id, self.processed])

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(self.SELECT_SQL, [self.depot_id])
        result = cursor.fetchone()

        if result:
            (self.depot_id, self.processed) = result
        else:
            self.processed = None
