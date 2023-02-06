import datetime
from stall.sql_resolver import SimpleSqlResolver


TEST_QUERY_RENDERED = '''
raw sql
column "column_alias"
key: '2022-01-01 12:34:56+0000'
'''


TEST_QUERY_ESCAPE_RENDERED = '''
SELECT
    'Rock''n''Roll' as "single_value",
    ('Rock''n''Roll','Rock"n"Roll') as "list_value"
'''


async def test_resolve_template(tap):
    with tap.plan(1, 'Поиск sqlt шаблона'):
        template_path = SimpleSqlResolver.resolve_template(
            by='tests.insert_variable'
        )
        tap.eq(template_path, 'tests/insert_variable.sqlt', 'path')


async def test_sql(tap, tzone):
    with tap.plan(3, 'Подстановка переменных в sql'):
        tz = tzone('UTC')
        sql = SimpleSqlResolver.sql(
            by='tests.insert_variable',
            alias='column_alias',
            value=datetime.datetime(2022, 1, 1, 12, 34, 56, 375316, tzinfo=tz),
        )

        sql_lines = sql.strip(' \n').split('\n')
        test_lines = TEST_QUERY_RENDERED.strip(' \n').split('\n')

        tap.eq(sql_lines[0], test_lines[0], 'Ничего не заменяем')
        tap.eq(sql_lines[1], test_lines[1], '{{ value |i }} оставляем as-is')
        tap.eq(sql_lines[2], test_lines[2],
               '{{ value }} заменим с заключением кавычки')

async def test_escape(tap):
    with tap.plan(3, 'Подстановка переменных в sql'):
        sql = SimpleSqlResolver.sql(
            by='tests.escape_variable',
            single_value='''Rock'n'Roll''',
            list_value=['''Rock'n'Roll''', '''Rock"n"Roll'''],
        )

        sql_lines = sql.strip(' \n').split('\n')
        test_lines = TEST_QUERY_ESCAPE_RENDERED.strip(' \n').split('\n')

        tap.eq(sql_lines[0], test_lines[0], 'select')
        tap.eq(sql_lines[1], test_lines[1], 'одно значение')
        tap.eq(sql_lines[2], test_lines[2], 'список значений')
