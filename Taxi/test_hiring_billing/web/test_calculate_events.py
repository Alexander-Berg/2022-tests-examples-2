import re
import uuid


async def test_basic(
        load_json, create_contragent, create_contract, calculate_events,
):
    contragent = await create_contragent(load_json('draft.json'))
    contract = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    data = load_json('events_basic.json')
    data['topics'][0]['events'][0]['meta']['contragent_id'] = contragent[
        'contragent_id'
    ]
    data['topics'][0]['events'][0]['meta']['contract_id'] = contract[
        'contract_id'
    ]
    result = await calculate_events(data=data)

    assert result['orders'][0], 'Распоряжение создано'

    assert (
        result['orders'][0]['topic']
        == f'taxi/partners/partners_learning_center/{contract["contract_id"]}'
    )
    assert result['orders'][0]['kind'] == 'partners_payment'
    assert re.match(
        '^1/[0-9]{4}-[0-9]{2}$', result['orders'][0]['external_ref'],
    ), 'Ссылка соостветствует схеме: ревизия/месяц'

    assert result['orders'][0]['data']['event_version'] == 1
    assert result['orders'][0]['data']['schema_version'] == '1'
    assert result['orders'][0]['data']['topic_begin_at']

    assert (
        result['orders'][0]['data']['entries'][0]['agreement_id']
        == f'hiring/{contract["contract_id"]}'
    )
    assert result['orders'][0]['data']['entries'][0]['currency'] == 'RUB'
    assert (
        result['orders'][0]['data']['entries'][0]['entity_external_id']
        == f'hiring_partner/{contragent["contragent_id"]}'
    )
    assert (
        result['orders'][0]['data']['entries'][0]['sub_account']
        == 'test/payment'
    )
    assert result['orders'][0]['data']['entries'][0]['amount'] == '100.0'

    assert result['orders'][0]['data']['payments'][0]['currency'] == 'RUB'
    assert result['orders'][0]['data']['payments'][0]['amount'] == '100.0'
    assert (
        result['orders'][0]['data']['payments'][0]['payment_kind']
        == 'partners_learning_center'
    )


async def test_contragent_fail(load_json, web_app_client):
    data = load_json('events_basic.json')
    data['topics'][0]['events'][0]['meta']['contragent_id'] = uuid.uuid4().hex
    data['topics'][0]['events'][0]['meta']['contract_id'] = uuid.uuid4().hex

    response = await web_app_client.post('/v1/events/calculate/', json=data)
    assert response.status == 500, await response.text()


async def test_contract_fail(
        load_json, web_app_client, create_contragent, mock_parks_replica,
):
    contragent = await create_contragent(load_json('draft.json'))

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    async def handler(request):  # pylint: disable=unused-variable
        return load_json('billing_client_id.json')

    data = load_json('events_basic.json')
    data['topics'][0]['events'][0]['meta']['contragent_id'] = contragent[
        'contragent_id'
    ]
    data['topics'][0]['events'][0]['meta']['contract_id'] = uuid.uuid4().hex

    response = await web_app_client.post('/v1/events/calculate/', json=data)
    assert response.status == 500, await response.text()
