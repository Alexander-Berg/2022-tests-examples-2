from agent.generated.cron import run_cron


async def test_import_lavka_persons(cron_context, mock_lavka1c):
    await run_cron.main(['agent.crontasks.import_lavka1c_persons', '-t', '0'])

    query = 'SELECT * FROM agent.users ORDER BY login'
    async with cron_context.pg.slave_pool.acquire() as conn:
        result = [
            {
                'login': row['login'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'en_first_name': row['en_first_name'],
                'en_last_name': row['en_last_name'],
                'source': row['source'],
                'hr_position': row['hr_position'],
                'email': row['email'],
            }
            for row in await conn.fetch(query)
        ]
    assert len(result) == 3

    assert result == [
        {
            'login': 'liambaev',
            'first_name': 'Лиам',
            'last_name': 'Баев',
            'en_first_name': 'Liam',
            'en_last_name': 'Baev',
            'source': 'lavka_external_offline',
            'hr_position': 'Заместитель директора склада',
            'email': 'liambaev@lavka-team.ru',
        },
        {
            'login': 'webalex',
            'first_name': 'Александр',
            'last_name': 'Иванов',
            'en_first_name': None,
            'en_last_name': None,
            'source': None,
            'hr_position': None,
            'email': None,
        },
        {
            'login': 'webalex_external',
            'first_name': 'Александр',
            'last_name': 'Иванов',
            'en_first_name': 'Aleksandr',
            'en_last_name': 'Ivanov',
            'source': 'lavka_external_offline',
            'hr_position': 'Директор склада',
            'email': 'webalex_external@lavka-team.ru',
        },
    ]

    query_check_roles = """SELECT login,key FROM agent.users_roles
ORDER BY login,key"""
    async with cron_context.pg.slave_pool.acquire() as conn:
        result = [
            {'login': row['login'], 'role': row['key']}
            for row in await conn.fetch(query_check_roles)
        ]

        assert [
            {'login': 'liambaev', 'role': 'lavkastorekeeper'},
            {'login': 'webalex_external', 'role': 'lavkastorekeeper'},
            {'login': 'webalex_external', 'role': 'lavkastorekeeper_director'},
        ] == result
