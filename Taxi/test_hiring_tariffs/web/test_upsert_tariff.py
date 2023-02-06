async def test_creation(load_json, create_draft):
    data = load_json('draft.json')
    approve = await create_draft(data)

    assert approve['change_doc_id'], 'Идентификатор операции назначен'
    assert approve['data'], 'Данные тарифа переданы'

    assert approve['data']['tariff_id'], 'Идентификатор назначен'
    assert approve['data']['revision'] == 1, 'Ревизия первая'


async def test_update(load_json, create_draft):
    data1 = load_json('draft.json')
    approve1 = await create_draft(data1)

    data2 = load_json('draft.json')
    data2['tariff_id'] = approve1['data']['tariff_id']
    approve2 = await create_draft(data2)

    assert (
        approve2['data']['tariff_id'] == approve1['data']['tariff_id']
    ), 'Идентификатор сохранен'
    assert approve2['data']['revision'] == 2, 'Новая ревизия'


async def test_duplicates(web_app_client, load_json):
    data = load_json('draft_has_duplicates.json')
    response = await web_app_client.post('/v1/tariff/', json=data)
    assert response.status == 400, await response.text()
    content = await response.json()

    assert content['code'] == 'TARIFF_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'DUPLICATE_TARGET'
    assert content['details']['errors'][0]['field'] == 'test'
    assert content['details']['errors'][0]['index'] == 2
