from test_chatterbox import plugins as conftest


async def test_in_additional_to_offline(cbox: conftest.CboxWrap):
    await cbox.app.supporters_manager.switch_in_additional_to_offline(
        ['user_in_additional', 'user_online'],
    )

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT supporter_login, in_additional, status '
            'FROM chatterbox.online_supporters ORDER BY supporter_login',
        )

    result = [dict(record) for record in result]
    assert result == [
        {
            'supporter_login': 'user_in_additional',
            'in_additional': False,
            'status': 'offline',
        },
        {
            'supporter_login': 'user_online',
            'in_additional': False,
            'status': 'online',
        },
    ]
