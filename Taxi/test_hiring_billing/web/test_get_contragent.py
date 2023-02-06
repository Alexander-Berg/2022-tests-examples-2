import uuid


async def test_get(load_json, create_contragent, get_contragent):
    data = load_json('draft.json')
    exists = await create_contragent(data)

    contragent = await get_contragent(contragent_id=exists['contragent_id'])

    assert (
        contragent['contragent_id'] == exists['contragent_id']
    ), 'Контрагент получен'


async def test_not_found(load_json, web_app_client):
    """Контрагент с неизвестным идентификатором не найден"""

    response = await web_app_client.get(
        '/v1/contragent/', params={'contragent_id': uuid.uuid4().hex},
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRAGENT_NOT_FOUND'
