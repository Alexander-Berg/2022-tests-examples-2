async def test_commit(load_json, create_draft, commit_draft):
    data = load_json('draft.json')
    approve = await create_draft(data)

    tariff = await commit_draft(
        tariff_id=approve['data']['tariff_id'],
        revision=approve['data']['revision'],
    )
    assert (
        tariff['tariff_id'] == approve['data']['tariff_id']
    ), 'Идентификатор сохранен'
    assert tariff['revision'] == 1, 'Ревизия сохранена'


async def test_unique_labels(load_json, create_tariff):
    data = load_json('draft_non_unique_labels.json')
    tariff = await create_tariff(data)

    assert tariff['labels'] == list(
        set(data['labels']),
    ), 'Только уникальные метки'


async def test_not_found(web_app_client):
    unknown_uuid = 'b203883efc21433e9e5a638c1e58bbdb'
    response = await web_app_client.post(
        '/v1/tariff/commit/', json={'tariff_id': unknown_uuid, 'revision': 1},
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'TARIFF_NOT_FOUND'
