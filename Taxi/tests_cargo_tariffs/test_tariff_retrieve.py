async def test_simple_retrieve(
        v1_tariff_retriever, v1_tariff_creator, mock_drafts_list,
):
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 200
    tariff_id = resp.json()['id']
    resp = await v1_tariff_retriever.retrieve(tariff_id)
    assert resp.status_code == 200
    assert mock_drafts_list.request == {
        'statuses': ['need_approval'],
        'change_doc_ids': [f'cargo-tariffs_{tariff_id}'],
    }
    response = resp.json()
    assert resp.json()['id'] == tariff_id
    assert response['service'] == 'ndd_client'
    assert not response['conditions']
    assert not response['documents']


async def test_retrieve_with_active_draft(
        v1_tariff_retriever,
        v1_tariff_creator,
        default_drafts_list_response,
        mock_drafts_list,
):
    resp = await v1_tariff_creator.create()
    assert resp.status_code == 200
    tariff_id = resp.json()['id']
    resp = await v1_tariff_retriever.retrieve(
        tariff_id, with_active_draft=True,
    )
    assert mock_drafts_list.request == {
        'statuses': ['need_approval'],
        'change_doc_ids': [f'cargo-tariffs_{tariff_id}'],
    }
    assert resp.status_code == 200
    response = resp.json()
    assert resp.json()['id'] == tariff_id
    assert response['service'] == 'ndd_client'
    assert response['active_draft']['data']['tariff_id'] == tariff_id
    assert response['active_draft'] == default_drafts_list_response[0]
    assert not response['conditions']
    assert not response['documents']


async def test_retrieve_with_conditions_and_documents(
        v1_tariff_retriever,
        insert_tariffs_to_db,
        zero_ndd_client_tariff,
        default_source_zone_condition,
):
    tariff_id, document_id = await insert_tariffs_to_db.insert_dummy()
    resp = await v1_tariff_retriever.retrieve(tariff_id)
    assert resp.status_code == 200
    response = resp.json()
    assert response['id'] == tariff_id
    assert response['service'] == 'ndd_client'
    assert len(response['conditions']) == 1
    assert response['conditions'][0] == default_source_zone_condition
    assert len(response['documents']) == 1
    assert response['documents'][0]['id'] == document_id
    assert response['documents'][0]['status'] == 'active'
    assert response['documents'][0]['details'] == zero_ndd_client_tariff


async def test_retrieve_non_exist(v1_tariff_retriever):
    resp = await v1_tariff_retriever.retrieve('some_tariff_id')
    assert resp.status_code == 404
    response = resp.json()
    assert response['code'] == 'not_found'


async def test_retrieve_without_id(v1_tariff_retriever):
    resp = await v1_tariff_retriever.retrieve()
    assert resp.status_code == 400
    response = resp.json()
    assert response['code'] == '400'
