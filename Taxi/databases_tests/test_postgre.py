"""
Для тестов были определены базы с названиями database_1 и database_3.
База dabatase_3 является шардированной. Схемы этих баз можно найти в папке
example-service/test_example_service/schemas/postgresql.

Наполнение баз происходит в скриптах, расположенных в папке
example-service/test_example_service/schemas/postgresql
Более подробно про заполнение баз postgresql можно прочитать здесь
https://wiki.yandex-team.ru/taxi/backend/testsuite/#postgresql
"""

import pytest


async def test_postgres(web_context, patch):
    @patch('taxi.clients.postgres.PostgresPoolsKeeper.get_pool')
    async def get_pool():
        pass

    await web_context.client_postgres.get_pool()

    assert get_pool.calls == [{}]


def test_foo_first_test_table(pgsql):
    cursor = pgsql['database_1'].cursor()
    cursor.execute('SELECT content from test.test_table_1')
    result = list(row[0] for row in cursor)
    assert result == ['qwe', 'rty', 'cfg', 'tyu']


def test_first_shard_bar_table(pgsql):
    cursor = pgsql['database_3@0'].cursor()
    cursor.execute(
        """
        SELECT tbl.key AS key
             , tbl.number as number
        FROM test.test_table_3 as tbl
        WHERE name LIKE %s
    """,
        ('driver%',),
    )
    assert list(cursor) == [('3', 59), ('6', 234)]


@pytest.mark.pgsql('database_3@1', files=('example_queries_content.sql',))
def test_second_shard_bar_table(pgsql):
    cursor = pgsql['database_3@1'].cursor()
    cursor.execute(
        """
        SELECT name as name
        FROM test.test_table_3
        WHERE key = %s
    """,
        ('25',),
    )
    assert list(cursor) == [('a',)]
    cursor.execute(
        """
        DELETE FROM test.test_table_3
        WHERE key = %s
    """,
        ('6',),
    )
    cursor.execute(
        """
        SELECT name as name
        FROM test.test_table_3
        WHERE key = %s
    """,
        ('6',),
    )
    assert list(cursor) == []
