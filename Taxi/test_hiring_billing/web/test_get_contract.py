import uuid


async def test_get(
        load_json, create_contragent, create_contract, get_contract,
):
    contragent = await create_contragent(load_json('draft.json'))

    exists = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    contract = await get_contract(contract_id=exists['contract_id'])

    assert (
        contract['contract_id'] == exists['contract_id']
    ), 'Контрагент получен'


async def test_not_found(load_json, web_app_client):
    """Договор с неизвестным идентификатором не найден"""

    response = await web_app_client.get(
        '/v1/contract/', params={'contract_id': uuid.uuid4().hex},
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRACT_NOT_FOUND'
