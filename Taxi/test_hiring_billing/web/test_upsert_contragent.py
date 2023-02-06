async def test_creation(load_json, create_contragent_draft):
    approve = await create_contragent_draft(data=load_json('draft.json'))

    assert approve['change_doc_id'], 'Идентификатор операции назначен'
    assert approve['data'], 'Данные переданы'

    assert approve['data']['contragent_id'], 'Идентификатор'
    assert approve['data']['revision'] == 1, 'Ревизия'


async def test_update(load_json, create_contragent_draft):
    """Создание черновиков"""
    approve1 = await create_contragent_draft(data=load_json('draft.json'))

    approve2 = await create_contragent_draft(
        data=load_json('draft.json'),
        contragent_id=approve1['data']['contragent_id'],
    )

    assert (
        approve2['data']['contragent_id'] == approve1['data']['contragent_id']
    ), 'Идентификатор сохранен'
    assert approve2['data']['revision'] == 2, 'Новая ревизия 2'

    approve3 = await create_contragent_draft(
        data=load_json('draft.json'),
        contragent_id=approve1['data']['contragent_id'],
    )

    assert (
        approve3['data']['contragent_id'] == approve1['data']['contragent_id']
    ), 'Идентификатор сохранен'
    assert approve3['data']['revision'] == 3, 'Новая ревизия 3'


async def test_failed_name(load_json, web_app_client):
    """Запрещенные символы в названии"""

    data = load_json('draft_failed_name.json')
    response = await web_app_client.post('/v1/contragent/', json=data)
    assert response.status == 400, await response.text()
    content = await response.json()

    assert content['code'] == 'REQUEST_VALIDATION_ERROR'
