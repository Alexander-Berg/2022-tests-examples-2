import pytest

from libstall.model.storable.pg_cursor import (
    CursorReplication,
    CursorWalk,
)
from libstall.model.storable.sharded_cursor import CursorSharded


def test_cursor(tap):
    with tap.plan(4):
        cursor = CursorSharded({'type': 'replication'}, nshards=10)
        tap.ok(cursor, 'Курсор создан')

        tap.ok(cursor.cursor_str, 'Сериализация')

        restored = CursorSharded(cursor.cursor_str, nshards=2)
        tap.ok(restored, 'Десериализация')
        tap.eq(restored.type, cursor.type, 'Тип восстановлен')


@pytest.mark.parametrize(
    'typename,instance',
    [
        ('replication', CursorReplication),
        ('walk', CursorWalk),
    ]
)
def test_cursor_shards(tap, typename, instance):
    with tap.plan(10, 'Проверяем пересоздание курсора'):
        cursor = CursorSharded({'type': typename}, nshards=2)
        tap.ok(cursor, 'Курсор создан')
        tap.eq(len(cursor.shards), 2, 'Список курсоров')
        tap.isa_ok(cursor.shards[0], instance, f'шард 0: {instance}')
        tap.isa_ok(cursor.shards[1], instance, f'шард 1: {instance}')

        tap.ok(cursor.cursor_str, 'Сериализация')

        restored = CursorSharded(cursor.cursor_str, nshards=2)
        tap.ok(restored, 'Десериализация')
        tap.eq(restored.type, cursor.type, 'Тип восстановлен')
        tap.eq(len(restored.shards), 2, 'Список курсоров')
        tap.isa_ok(restored.shards[0], instance, f'шард 0:{instance}')
        tap.isa_ok(restored.shards[1], instance, f'шард 1:{instance}')


def test_cursor_time(tap):
    with tap.plan(8):
        cursor = CursorSharded(
            {'type': 'replication', 'time': 123456},
            nshards=2
        )
        tap.ok(cursor, 'Курсор создан')
        tap.eq(cursor.time, 123456, 'Время создания сохранено')
        tap.eq(cursor.shards[0].time, 123456, 'Время по основному курсору')

        tap.ok(cursor.cursor_str, 'Сериализация')

        restored = CursorSharded(cursor.cursor_str, nshards=2)
        tap.ok(restored, 'Десериализация')
        tap.eq(restored.type, cursor.type, 'Тип восстановлен')
        tap.eq(restored.time, 123456, 'Время создания сохранено')
        tap.eq(restored.shards[0].time, 123456, 'Время по основному курсору')
