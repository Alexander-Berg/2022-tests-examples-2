from libstall.model.storable.pg import Pg
# pylint: disable=unused-import
from libstall.model.storable import Attribute, Table


class TstPgModel(Pg, table=Table('pginshard', pkey='key')):
    database = 'tlibstall'
    key=Attribute(types=str)
    value=Attribute(types=str)


# pylint: disable=unused-argument
async def test_savesave_load(tap, dbh, uuid):
    tap.plan(11)

    key = uuid()

    o = TstPgModel({'key': key, 'value': 'v1'})
    tap.ok(o, 'модель инстанцирована')

    saved = await o.save()

    tap.ok(saved, 'модель загружена')
    tap.isa_ok(saved, TstPgModel, 'тип')

    tap.eq(saved.key, key, 'значение ключа')
    tap.eq(saved.value, 'v1', 'имя таблицы')

    tap.eq(dict(saved.items('rehashed')), {},
           'нет изменившихся элементов после save')


    loaded = await TstPgModel.load(key)

    tap.ok(loaded, 'Загружено')
    tap.eq(loaded.value, 'v1', 'Значение')
    tap.eq(loaded.key, key, 'ключ')


    tap.ok(await loaded.rm(), 'Удалено')

    tap.ok(not await TstPgModel.load(key), 'В БД удалено')


    tap()


