"""
Если требуется поместить данные в коллекцию, то можно эти данные сохранить в
файл.
Файл, из которого происходит наливка данных в тестовую базу данных,
расположен по пути
example-service/test_example_service/web/static/test_mongo_operations
/db_users.json

О том, из каких файлов происходит заполнение базой данных, можно почитать
здесь
https://wiki.yandex-team.ru/taxi/backend/testsuite/#rabotasostaticheskimifajjlami
"""


async def test_mongo_update(mongo):
    _id = '0fb55c6031a145568d11e7d7d5bd2d46'
    await mongo.users.update_one({'_id': _id}, {'$set': {'name': 'John'}})

    order = await mongo.users.find_one({'_id': _id})
    assert order == {'_id': _id, 'greetings': 'Zeta', 'name': 'John'}


async def test_mongo_insert(mongo):
    _id = 'bb4a034bfa894604aa4f32185330be94'
    await mongo.users.insert_one(
        {'_id': _id, 'greetings': 'Yo', 'name': 'dawg'},
    )

    order = await mongo.users.find_one({'_id': _id})
    assert order == {'_id': _id, 'greetings': 'Yo', 'name': 'dawg'}


async def test_mongo_remove(mongo):
    _id = '9be906950cd3440c95938abe18903f69'
    order = await mongo.users.find_one({'_id': _id})
    assert order == {'_id': _id, 'greetings': 'Hello', 'name': 'World'}
    await mongo.users.remove({'_id': _id})
    order = await mongo.users.find_one({'_id': _id})
    assert order is None
