import asyncpg

from taxi_antifraud.generated.cron.yt_wrapper import plugin as yt_plugin
from test_taxi_antifraud.cron.utils import state


async def prepare_data(
        data: dict,
        yt_client: yt_plugin.AsyncYTClient,
        master_pool: asyncpg.Pool,
        cursor_state_name: str,
        yt_directory_path: str,
        yt_table_path: str,
):
    await state.initialize_state_table(master_pool, cursor_state_name)
    yt_client.create(
        'map_node',
        path=yt_directory_path,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(yt_table_path, data)
