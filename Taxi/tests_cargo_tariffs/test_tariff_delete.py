async def test_simple_delete(
        v1_tariff_creator, v1_tariff_retriever, v1_tariff_deleter,
):
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 200
    tariff_id = resp.json()['id']

    resp = await v1_tariff_retriever.retrieve(tariff_id)
    assert resp.status_code == 200
    assert resp.json()['id'] == tariff_id

    resp = await v1_tariff_deleter.delete(tariff_id)
    assert resp.status_code == 200
    assert resp.json() == {}

    resp = await v1_tariff_retriever.retrieve(tariff_id)
    assert resp.status_code == 404
    assert resp.json()['code'] == 'not_found'


async def test_tariff_not_exist(v1_tariff_deleter):
    resp = await v1_tariff_deleter.delete('some_tariff_id')
    assert resp.status_code == 404
    assert resp.json()['code'] == 'not_found'


async def test_active_documents_exist(v1_tariff_deleter, insert_tariffs_to_db):
    tariff_id, _ = await insert_tariffs_to_db.insert_dummy()
    resp = await v1_tariff_deleter.delete(tariff_id)
    assert resp.status_code == 409
    assert resp.json()['code'] == 'active_documents_exist'


async def test_delete_without_id(v1_tariff_deleter):
    resp = await v1_tariff_deleter.delete()
    assert resp.status_code == 400
    assert resp.json()['code'] == '400'
