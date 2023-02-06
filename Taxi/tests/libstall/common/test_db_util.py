# pylint: disable=unused-import
import typing
import pytest
from easytap.pytest_plugin import PytestTap

from libstall.model.storable import Table, Attribute
from libstall.model.storable.pg import Pg
from libstall.pg.util import (
    fetch_estimate_count_by_shards,
    fetch_estimate_count
)


class TstPgModel(Pg, table=Table('pg_class', pkey='key')):
    database = 'tlibstall'
    key = Attribute(types=str)
    value = Attribute(types=str)


class TstPgModelUnknown(Pg, table=Table('unknown_table', pkey='key')):
    database = 'tlibstall'
    key = Attribute(types=str)


class TstPgModelWoTable(Pg):
    database = 'tlibstall'
    key = Attribute(types=str)
    value = Attribute(types=str)


class TstCustomModel:
    key = Attribute(types=str)
    value = Attribute(types=str)


@pytest.mark.parametrize('obj_or_model,', (
    TstPgModel, # обращение к реальной модели
    TstPgModel(), # обращение к объекту
))
async def test_fetch_estimate_count_shard(
        tap: PytestTap,
        obj_or_model: typing.Union[Pg, typing.Type[Pg]]):

    with tap:
        # получаем примерный размер таблицы
        res = await fetch_estimate_count_by_shards(obj_or_model)
        shards_amount = len(res)
        tap.ne_ok(shards_amount, 0,
                  'В текущем окружении {shards_amount} шардов')

        for est_shard, est_count in res.items():
            tap.ok(est_count > 0,
                   f'fetch for shard {est_shard} returned int ({est_count})')


@pytest.mark.parametrize('obj_or_model,', (
    TstPgModelWoTable, # обращение к модели без таблицы
    TstCustomModel, # обращение не к Pg
    TstPgModelUnknown, # обращение к неизвестной таблице
))
async def test_estimate_count_failed(
        tap: PytestTap,
        obj_or_model: typing.Union[Pg, typing.Type[Pg]]):

    with tap:
        with tap.raises(ValueError):
            await fetch_estimate_count_by_shards(obj_or_model)

        with tap.raises(ValueError):
            await fetch_estimate_count(obj_or_model)


@pytest.mark.parametrize('obj_or_model,', (
    TstPgModel, # обращение к реальной модели
    TstPgModel(), # обращение к объекту
))
async def test_fetch_estimate_count(
        tap: PytestTap,
        obj_or_model: typing.Union[Pg, typing.Type[Pg]]):
    with tap:
        # получаем примерный размер таблицы
        res = await fetch_estimate_count(obj_or_model)
        tap.ok(res > 0, f'fetch returned int ({res})')
