import asyncpg


async def initialize_state_table(
        pool: asyncpg.Pool, cursor_state_name: str,
) -> None:
    query = """
        insert into
            crontasks_common.cronstate
        values
            (($1), 0);
        """
    async with pool.acquire() as connection:
        await connection.execute(query, cursor_state_name)


async def get_all_cron_state(pool: asyncpg.Pool) -> dict:
    query = """
        select
            *
        from
            crontasks_common.cronstate
        """
    async with pool.acquire() as connection:
        return dict(await connection.fetch(query))
