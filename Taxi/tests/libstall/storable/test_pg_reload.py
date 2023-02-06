# pylint: disable=unused-import
from libstall.model.storable import Attribute, Table
from libstall.model.storable.pg import Pg


class TstPgModel(Pg, table=Table('pginshard', pkey='key')):
    database = 'tlibstall'

    key=Attribute(types=str)
    value=Attribute(types=str)



# pylint: disable=unused-argument
async def test_reload(tap, dbh, uuid):
    with tap.plan(8):
        key = uuid()

        o1 = TstPgModel({'key': key, 'value': '111'})
        tap.ok(o1, 'модель инстанцирована')

        await o1.save()
        tap.ok(o1, 'модель сохранена')
        tap.eq(o1.value, '111', 'Старое значение')

        o2 = await TstPgModel.load(key)
        tap.ok(o2, 'объект получен')

        o2.rehash(value='222')
        await o2.save()
        tap.ok(o2, 'модель сохранена')
        tap.eq(o2.value, '222', 'Новое значение')

        tap.ok(await o1.reload(), 'Модель перезагружена')
        tap.eq(o1.value, '222', 'Новое значение загружено')


