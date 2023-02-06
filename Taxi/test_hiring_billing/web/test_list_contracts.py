# pylint: disable=unused-variable
import datetime


async def test_list(
        load_json, create_contragent, create_contract, list_contracts,
):
    """Получение списка договоров"""

    contragent1 = await create_contragent(
        data=load_json('draft.json'), name='Тест 1',
    )
    contract1 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent1['contragent_id'],
    )

    contragent2 = await create_contragent(
        data=load_json('draft.json'), name='Тест 2',
    )
    contract2 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent2['contragent_id'],
    )

    received = await list_contracts()

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 2, 'Договора получены'

    assert received['contracts'][0]['contract_id'] == (
        contract1['contract_id']
    ), 'Правильный порядок сортировки'
    assert received['contracts'][1]['contract_id'] == (
        contract2['contract_id']
    ), 'Правильный порядок сортировки'


async def test_contragent_filter(
        load_json, create_contragent, create_contract, list_contracts,
):
    contragent1 = await create_contragent(
        data=load_json('draft.json'), name='Тест 1',
    )
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent1['contragent_id'],
    )

    contragent2 = await create_contragent(
        data=load_json('draft.json'), name='Тест 2',
    )
    contract2 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent2['contragent_id'],
    )

    received = await list_contracts(contragent_id=contragent2['contragent_id'])

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 1, 'Договора получены'

    assert received['contracts'][0]['contract_id'] == (
        contract2['contract_id']
    ), 'Только выбранный контрагент'


async def test_medium_filter(
        load_json, create_contragent, create_contract, list_contracts,
):
    contragent = await create_contragent(data=load_json('draft.json'))
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        medium='partners',
    )
    contract2 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        medium='scouts',
    )

    received = await list_contracts(medium='scouts')

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 1, 'Договора получены'

    assert received['contracts'][0]['contract_id'] == (
        contract2['contract_id']
    ), 'Только выбранный контрагент'


async def test_geo_filter(
        load_json, create_contragent, create_contract, list_contracts,
):
    contragent = await create_contragent(data=load_json('draft.json'))
    contract1 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        geo=['zvenigorod'],
    )
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        geo=['belgrade'],
    )

    received = await list_contracts(geo='zvenigorod')

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 1, 'Договора получены'

    assert received['contracts'][0]['contract_id'] == (
        contract1['contract_id']
    ), 'Только выбранный контрагент'


async def test_time_ts_filter(
        load_json, create_contragent, create_contract, list_contracts,
):
    contragent = await create_contragent(data=load_json('draft.json'))
    contract1 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        start_ts=datetime.datetime.fromtimestamp(2000000000 + 1000),
        geo=['zvenigorod'],
    )
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        start_ts=datetime.datetime.fromtimestamp(2000000000 + 1000),
        finish_ts=datetime.datetime.fromtimestamp(2000000000 + 2000),
        geo=['belgrade'],
    )
    contract3 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        start_ts=datetime.datetime.fromtimestamp(2000000000 + 1000),
        finish_ts=datetime.datetime.fromtimestamp(2000000000 + 3000),
        geo=['astana'],
    )
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        start_ts=datetime.datetime.fromtimestamp(2000000000 + 4000),
        geo=['electrostal'],
    )

    received = await list_contracts(
        time_ts=datetime.datetime.fromtimestamp(2000000000 + 2500),
    )

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 2, 'Договора получены'

    assert received['contracts'][0]['contract_id'] == (
        contract1['contract_id']
    ), 'Бессрочный договор'
    assert received['contracts'][1]['contract_id'] == (
        contract3['contract_id']
    ), 'Укладывается в период'


async def test_status_filter(
        load_json,
        create_contragent,
        create_contract_draft,
        create_contract,
        list_contracts,
):
    contragent = await create_contragent(data=load_json('draft.json'))
    contract1 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )
    approve1 = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    received = await list_contracts(status='all')

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 2, 'История получена'

    assert received['contracts'][0]['contract_id'] == (
        contract1['contract_id']
    ), 'Договор'
    assert received['contracts'][1]['contract_id'] == (
        approve1['data']['contract_id']
    ), 'Черновик'


async def test_search_filter(
        load_json, create_contragent, create_contract, list_contracts,
):
    contragent1 = await create_contragent(
        data=load_json('draft.json'), name='ABC',
    )
    contract1 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent1['contragent_id'],
    )

    contragent2 = await create_contragent(
        data=load_json('draft.json'), name='XYZ',
    )
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent2['contragent_id'],
    )

    received = await list_contracts(search='ab')

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 1, 'Договора получены'

    assert received['contracts'][0]['contract_id'] == (
        contract1['contract_id']
    ), 'Только выбранный контрагент'


async def test_offset_limit(
        load_json, create_contragent, create_contract, list_contracts,
):
    """Пагинация"""
    data = load_json('draft.json')

    contragent = await create_contragent(data)
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        geo=['zvenigorod'],
    )
    contract2 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        geo=['belgrade'],
    )
    contract3 = await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        geo=['astana'],
    )
    await create_contract(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
        geo=['electrostal'],
    )

    received = await list_contracts(offset=1, limit=2)

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contracts']) == 2, 'Договора получены'

    assert received['contracts'][0]['contract_id'] == (
        contract2['contract_id']
    ), 'Только выбранный договор'
    assert received['contracts'][1]['contract_id'] == (
        contract3['contract_id']
    ), 'Только выбранный договор'
