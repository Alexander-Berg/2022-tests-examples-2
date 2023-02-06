import uuid


async def test_commit(
        load_json,
        create_contragent,
        create_contract_draft,
        commit_contract_draft,
):
    contragent = await create_contragent(load_json('draft.json'))

    approve = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    contract = await commit_contract_draft(approve['data'])
    assert (
        contract['contract_id'] == approve['data']['contract_id']
    ), 'Идентификатор сохранен'
    assert contract['revision'] == 1, 'Ревизия сохранена'


async def test_mass_edit(
        load_json,
        create_contragent,
        create_contract_draft,
        commit_contract_draft,
):
    contragent = await create_contragent(load_json('draft.json'))

    approve1 = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    contract1 = await commit_contract_draft(approve1['data'])
    assert (
        contract1['contract_id'] == approve1['data']['contract_id']
    ), 'Идентификатор сохранен'
    assert contract1['revision'] == 1, 'Ревизия сохранена'

    approve2 = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contract_id=contract1['contract_id'],
        contragent_id=contragent['contragent_id'],
    )

    contract2 = await commit_contract_draft(approve2['data'])
    assert (
        contract2['contract_id'] == approve1['data']['contract_id']
    ), 'Идентификатор сохранен'
    assert contract2['revision'] == 2, 'Ревизия сохранена'


async def test_not_found(
        web_app_client, load_json, create_contragent, create_contract_draft,
):
    contragent = await create_contragent(load_json('draft.json'))

    approve = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    data = approve['data']
    data['contract_id'] = uuid.uuid4().hex
    response = await web_app_client.post('/v1/contract/commit/', json=data)
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRACT_NOT_FOUND'


async def test_already_commited(
        web_app_client,
        load_json,
        create_contragent,
        create_contract_draft,
        commit_contract_draft,
):
    contragent = await create_contragent(load_json('draft.json'))

    approve = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    await commit_contract_draft(approve['data'])

    response = await web_app_client.post(
        '/v1/contract/commit/', json=approve['data'],
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRACT_NOT_FOUND'


async def test_old_revision_error(
        web_app_client,
        load_json,
        create_contragent,
        create_contract_draft,
        commit_contract_draft,
):
    """Проверка получения ошибки при попытке коммита старой ревизии"""

    contragent = await create_contragent(load_json('draft.json'))

    approve1 = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    approve2 = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contract_id=approve1['data']['contract_id'],
        contragent_id=contragent['contragent_id'],
    )

    await commit_contract_draft(approve2['data'])

    response = await web_app_client.post(
        '/v1/contract/commit/', json=approve1['data'],
    )
    assert response.status == 400, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRACT_COMMIT_ERROR'


async def test_intersection(
        web_app_client,
        load_json,
        create_contragent,
        create_contract,
        create_contract_draft,
        commit_contract_draft,
):
    """Проверка получения ошибки при попытке коммита старой ревизии"""

    contragent = await create_contragent(load_json('draft.json'))

    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    approve = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    response = await web_app_client.post(
        '/v1/contract/commit/', json=approve['data'],
    )
    assert response.status == 400, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRACT_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'CONTRACT_INTERSECTION'
