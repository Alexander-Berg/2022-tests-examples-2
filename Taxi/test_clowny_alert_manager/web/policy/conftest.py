import pytest


@pytest.fixture
def fetch_db_branch_juggler_host(pgsql):
    def _impl():
        db = pgsql['clowny_alert_manager']
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT
                bjh.clown_branch_id AS clown_branch_id,
                jh.juggler_host AS juggler_host,
                bjh.deleted_at IS NOT NULL
            FROM alert_manager.branch_juggler_host AS bjh
            INNER JOIN alert_manager.juggler_host AS jh
                ON bjh.juggler_host_id = jh.id
            ORDER BY
                bjh.clown_branch_id,
                jh.juggler_host
        """,
        )

        return list(map(list, cursor))

    return _impl
