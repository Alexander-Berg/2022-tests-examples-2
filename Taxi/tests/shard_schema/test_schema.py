from random import randrange

import pytest

from stall.shard_schema import shard_by_idstr_0001 as handle_v1
from stall.shard_schema import shard_by_idstr_0002 as handle_v2
from stall.shard_schema import shard_by_eid, eid_for_shard


def test_schema_v1(tap, uuid):
    with tap.plan(5):
        res = [ handle_v1(uuid()) for _ in range(1000) ]
        tap.eq(len(res), 1000, 'тысяча шардов посчитана')

        zeros = list(filter(lambda x: x == 0, res))
        ones  = list(filter(lambda x: x == 1, res))

        tap.ok(zeros, 'нули есть')
        tap.ok(ones, 'единицы есть')
        tap.eq(len(zeros) + len(ones), len(res), 'других нет')


        res = [ (uuid(), randrange(2)) for _ in range(1000) ]
        res = [ (x + (handle_v1(x[0], x[1]),)) for x in res ]
        res = [
            (x + ('%s%04x%04x%04x' % (x[0], x[2], 1, x[1]),)) for x in res
        ]
        res = [ (x + (handle_v1(x[-1][:32+4]) == x[1],)) for x in res ]

        tap.eq(len(list(filter(lambda x: x[-1], res))), 1000,
               'вся тысяча скорректирована верно')



def test_schema_v2(tap, uuid):
    with tap.plan(6):
        res = [ handle_v2(uuid()) for _ in range(1000) ]
        tap.eq(len(res), 1000, 'тысяча шардов посчитана')

        zeros = list(filter(lambda x: x == 0, res))
        ones  = list(filter(lambda x: x == 1, res))
        twos  = list(filter(lambda x: x == 2, res))

        tap.ok(zeros, 'нули есть')
        tap.ok(ones, 'единицы есть')
        tap.ok(twos, 'двойки есть')
        tap.eq(len(zeros) + len(ones) + len(twos), len(res), 'других нет')


        res = [ (uuid(), randrange(3)) for _ in range(1000) ]
        res = [ (x + (handle_v2(x[0], x[1]),)) for x in res ]
        res = [
            (x + ('%s%04x%04x%04x' % (x[0], x[2], 2, x[1]),)) for x in res
        ]
        res = [ (x + (handle_v2(x[-1][:32+4]) == x[1],)) for x in res ]

        tap.eq(len(list(filter(lambda x: x[-1], res))), 1000,
               'вся тысяча скорректирована верно')

@pytest.mark.parametrize('current_version', [2])
@pytest.mark.parametrize('shard', [0, 1, 2])
def test_fail_jcdenton_v2(tap, shard, current_version):
    with tap.plan(5, f'Тестирование проблемного uuid шард {shard}'):
        uuid = '509615719b324db4a60672833b00320f'
        tap.eq(len(uuid), 32, 'длина')
        res = handle_v2('ha509615719b324db4a60672833b00320f', shard)
        tap.ok(0 <= res <= 128, f'размер фикса шард {shard}')
        eid = '%s%04x%04x%04x' % (uuid, res, current_version, shard)
        tap.eq(len(eid), 44, 'размер eid')
        tap.eq(shard_by_eid(eid), shard, 'шард получен')
        tap.eq(
            eid_for_shard(2, shard, uuid=uuid),
            eid,
            'сгенерирован корректно'
        )
