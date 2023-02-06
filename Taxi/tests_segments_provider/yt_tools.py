import dataclasses

from tests_segments_provider import launch_tools


@dataclasses.dataclass
class YtTable:
    launch_uuid: str
    alias: str
    path: str
    lifespan: str
    is_marked_for_deletion: bool


def find_yt_tables(pgsql, launch_uuid: str):
    launch_id = launch_tools.get_launch_id(pgsql, launch_uuid)

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT
            yt_tables.launch_id,
            yt_tables.alias,
            yt_tables.path,
            yt_tables.lifespan,
            yt_tables.is_marked_for_deletion
        FROM state.yt_tables
        WHERE yt_tables.launch_id = '{launch_id}'
        ORDER BY alias
        """,
    )
    return list(
        YtTable(
            launch_uuid=launch_uuid,
            alias=row[1],
            path=row[2],
            lifespan=row[3],
            is_marked_for_deletion=row[4],
        )
        for row in cursor
    )


def find_all_yt_tables(pgsql):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT
            launches.uuid,
            yt_tables.alias,
            yt_tables.path,
            yt_tables.lifespan,
            yt_tables.is_marked_for_deletion
        FROM state.yt_tables
        JOIN state.launches
            ON yt_tables.launch_id = launches.id
        ORDER BY launches.uuid, yt_tables.alias
        """,
    )
    return list(
        YtTable(
            launch_uuid=row[0],
            alias=row[1],
            path=row[2],
            lifespan=row[3],
            is_marked_for_deletion=row[4],
        )
        for row in cursor
    )


def get_insert_yt_table_query(table: YtTable):
    launch_id = (
        f'(SELECT id FROM state.launches WHERE uuid = \'{table.launch_uuid}\')'
    )

    return f"""
        INSERT INTO state.yt_tables (
            launch_id,
            alias,
            path,
            lifespan,
            is_marked_for_deletion
        ) VALUES (
            {launch_id},
            '{table.alias}',
            '{table.path}',
            '{table.lifespan}',
            '{str(table.is_marked_for_deletion)}'
        )
        """


def insert_yt_table(pgsql, table: YtTable):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(get_insert_yt_table_query(table))
