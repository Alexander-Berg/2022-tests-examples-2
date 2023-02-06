from .record import PgRecord

# pylint: disable=unused-argument,too-many-statements


async def test_condition_simple(tap):
    with tap.plan(3):
        cursor = await PgRecord.list(by='full', full=True, conditions=(
            'test_id', '111'
        ))
        tap.ok(cursor, 'Простое сравнение')

        cursor = await PgRecord.list(by='full', full=True, conditions=(
            'test_id', ['111', '222']
        ))
        tap.ok(cursor, 'IN')

        cursor = await PgRecord.list(by='full', full=True, conditions=(
            'test_id', None
        ))
        tap.ok(cursor, 'NULL')


async def test_condition_simple_op(tap):
    with tap.plan(1):
        cursor = await PgRecord.list(by='full', full=True, conditions=(
            'test_id', '=', '111'
        ))
        tap.ok(cursor, 'Простое сравнение')


async def test_condition_and(tap):
    with tap.plan(1):
        cursor = await PgRecord.list(by='full', full=True, conditions=[
            {'name': 'test_id', 'value': '111'},
            {'name': 'test_id', 'value': '222'},
            {'name': 'test_id', 'value': '333'},
        ])
        tap.ok(cursor, 'Курсор получен')


async def test_condition_and_simpe(tap):
    with tap.plan(1):
        cursor = await PgRecord.list(by='full', full=True, conditions=[
            ('test_id', '111')
        ])
        tap.ok(cursor, 'Курсор получен')


async def test_condition_or(tap):
    with tap.plan(1):
        cursor = await PgRecord.list(by='full', full=True, conditions=[
            [
                {'name': 'test_id', 'value': '111'},
                {'name': 'test_id', 'value': '222'},
            ],
            [
                {'name': 'test_id', 'value': '333'},
            ]
        ])
        tap.ok(cursor, 'Курсор получен')


async def test_condition_or_simple(tap):
    with tap.plan(1):
        cursor = await PgRecord.list(by='full', full=True, conditions=[
            [
                ('test_id', '111'),
                ('test_id', ['222']),
            ],
            [
                ('test_id', '333'),
            ]
        ])
        tap.ok(cursor, 'Курсор получен')


async def test_condition_in(tap):
    with tap.plan(1):
        cursor = await PgRecord.list(by='full', full=True, conditions=[
            ('test_id', 'IN', ['222']),
            ('test_id', 'NOT IN', ['333']),
        ])
        tap.ok(cursor, 'Курсор получен')
