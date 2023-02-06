import uuid


async def test_commit(
        load_json, create_contragent_draft, commit_contragent_draft,
):
    data = load_json('draft.json')
    approve = await create_contragent_draft(data)

    contragent = await commit_contragent_draft(approve['data'])
    assert (
        contragent['contragent_id'] == approve['data']['contragent_id']
    ), 'Идентификатор сохранен'
    assert contragent['revision'] == 1, 'Ревизия сохранена'
    assert contragent['name'] == data['name'], 'Имя сохранено'


async def test_mass_edit(
        load_json, create_contragent_draft, commit_contragent_draft,
):
    data1 = load_json('draft.json')
    approve1 = await create_contragent_draft(data1)

    contragent1 = await commit_contragent_draft(approve1['data'])
    assert (
        contragent1['contragent_id'] == approve1['data']['contragent_id']
    ), 'Идентификатор сохранен'
    assert contragent1['revision'] == 1, 'Ревизия сохранена'

    data2 = load_json('draft.json')
    approve2 = await create_contragent_draft(
        data2, contragent_id=contragent1['contragent_id'],
    )

    contragent2 = await commit_contragent_draft(approve2['data'])
    assert (
        contragent2['contragent_id'] == approve1['data']['contragent_id']
    ), 'Идентификатор сохранен'
    assert contragent2['revision'] == 2, 'Ревизия сохранена'


async def test_not_found(web_app_client, load_json, create_contragent_draft):
    approve = await create_contragent_draft(data=load_json('draft.json'))

    data = approve['data']
    data['contragent_id'] = uuid.uuid4().hex
    response = await web_app_client.post('/v1/contragent/commit/', json=data)
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRAGENT_NOT_FOUND'


async def test_already_commited(
        web_app_client,
        load_json,
        create_contragent_draft,
        commit_contragent_draft,
):
    data = load_json('draft.json')
    approve = await create_contragent_draft(data)

    await commit_contragent_draft(approve['data'])

    response = await web_app_client.post(
        '/v1/contragent/commit/', json=approve['data'],
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRAGENT_NOT_FOUND'


async def test_name_duplicate(
        web_app_client,
        load_json,
        create_contragent_draft,
        commit_contragent_draft,
):
    data = load_json('draft.json')
    approve1 = await create_contragent_draft(
        data, contragent_id=uuid.uuid4().hex,
    )
    approve2 = await create_contragent_draft(
        data, contragent_id=uuid.uuid4().hex,
    )

    await commit_contragent_draft(approve1['data'])

    response = await web_app_client.post(
        '/v1/contragent/commit/', json=approve2['data'],
    )
    assert response.status == 400, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRAGENT_DEFINITION_ERROR'
    assert (
        content['details']['errors'][0]['code'] == 'DUPLICATE_CONTRAGENT_NAME'
    )


async def test_old_revision_error(
        web_app_client,
        load_json,
        create_contragent_draft,
        commit_contragent_draft,
):
    """Проверка получения ошибки при попытке коммита старой ревизии"""

    data = load_json('draft.json')
    approve1 = await create_contragent_draft(data)

    data = load_json('draft.json')
    approve2 = await create_contragent_draft(
        data, contragent_id=approve1['data']['contragent_id'],
    )

    await commit_contragent_draft(approve2['data'])

    response = await web_app_client.post(
        '/v1/contragent/commit/', json=approve1['data'],
    )
    assert response.status == 400, await response.text()
    content = await response.json()

    assert content['code'] == 'CONTRAGENT_COMMIT_ERROR'
