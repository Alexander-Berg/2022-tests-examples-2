from libstall.model.storable.pginshard import PgInShard
# pylint: disable=unused-import
from libstall.model.storable import Attribute, Table


class TstPgModel(PgInShard, table=Table('pginshard', pkey='key')):
    database = 'tlibstall'
    key=Attribute(types=str)
    value=Attribute(types=str)


# pylint: disable=unused-argument
async def test_savesave_load(tap, dbh, uuid):
    tap.plan(17)

    key = uuid()

    o = TstPgModel({'key': key, 'value': 'v1'})
    tap.ok(o, 'модель инстанцирована')

    with tap.raises(RuntimeError, 'без шарда исключение'):
        await o.save()

    saved = await o.save(db={'shard': 1})
    tap.eq(saved.shardno, 1, 'номер шарда')

    tap.ok(saved, 'модель загружена')
    tap.isa_ok(saved, TstPgModel, 'тип')

    tap.eq(saved.key, key, 'значение ключа')
    tap.eq(saved.value, 'v1', 'имя таблицы')

    tap.eq(dict(saved.items('rehashed')), {},
           'нет изменившихся элементов после save')

    with tap.raises(RuntimeError, 'нет шарда - исключение'):
        await TstPgModel.load(key)

    loaded = await TstPgModel.load(key, db={'shard': 1})

    tap.ok(loaded, 'Загружено')
    tap.eq(loaded.shardno, 1, 'Номер шарда после загрузки')
    tap.eq(loaded.value, 'v1', 'Значение')
    tap.eq(loaded.key, key, 'ключ')


    tap.ok(await loaded.rm(), 'Удалено')
    tap.ok(not await TstPgModel.load(key, db={'shard': 1}), 'В БД удалено')
    tap.ok(loaded.shardno is None, 'шард после удаления не определен')

    with tap.raises(RuntimeError, 'Повторное удаление исключение'):
        await loaded.rm()


    tap()




