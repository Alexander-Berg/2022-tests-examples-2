from aiohttp import web


async def test_creation(load_json, create_contragent, create_contract_draft):
    contragent = await create_contragent(load_json('draft.json'))

    approve = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contragent_id=contragent['contragent_id'],
    )

    assert approve['change_doc_id'], 'Идентификатор операции назначен'
    assert approve['data'], 'Данные переданы'

    assert approve['data']['contract_id'], 'Идентификатор'
    assert approve['data']['revision'] == 1, 'Ревизия'


async def test_update(load_json, create_contragent, create_contract_draft):
    """Создание черновиков"""
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

    assert (
        approve2['data']['contract_id'] == approve1['data']['contract_id']
    ), 'Идентификатор сохранен'
    assert approve2['data']['revision'] == 2, 'Новая ревизия 2'

    approve3 = await create_contract_draft(
        data=load_json('draft_contract.json'),
        contract_id=approve1['data']['contract_id'],
        contragent_id=contragent['contragent_id'],
    )

    assert (
        approve3['data']['contract_id'] == approve1['data']['contract_id']
    ), 'Идентификатор сохранен'
    assert approve3['data']['revision'] == 3, 'Новая ревизия 3'


async def test_fail_start_after_finish(
        load_json,
        create_contragent,
        web_app_client,
        mock_hiring_tariffs,
        mock_taxi_tariffs,
):
    contragent = await create_contragent(load_json('draft.json'))

    draft = load_json('fail_start_after_finish.json')
    draft['contragent_id'] = contragent['contragent_id']

    @mock_hiring_tariffs('/v1/tariff/')
    async def handler1(request):  # pylint: disable=unused-variable
        return load_json('tariff.json')

    @mock_taxi_tariffs('/v1/tariff_zones')
    async def handler2(request):  # pylint: disable=unused-variable
        return load_json('zones.json')

    response = await web_app_client.post('/v1/contract/', json=draft)
    assert response.status == 400, await response.text()

    content = await response.json()
    assert content['code'] == 'CONTRACT_DEFINITION_ERROR'
    assert (
        content['details']['errors'][0]['code']
        == 'CONTRACT_START_AFTER_FINISH'
    )


async def test_fail_contragent_not_found(
        load_json, web_app_client, mock_hiring_tariffs, mock_taxi_tariffs,
):
    draft = load_json('fail_contragent_not_found.json')

    @mock_hiring_tariffs('/v1/tariff/')
    async def handler1(request):  # pylint: disable=unused-variable
        return load_json('tariff.json')

    @mock_taxi_tariffs('/v1/tariff_zones')
    async def handler2(request):  # pylint: disable=unused-variable
        return load_json('zones.json')

    response = await web_app_client.post('/v1/contract/', json=draft)
    assert response.status == 400, await response.text()

    content = await response.json()
    assert content['code'] == 'CONTRACT_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'CONTRAGENT_NOT_FOUND'


async def test_tariff_not_found(
        load_json,
        create_contragent,
        web_app_client,
        mock_hiring_tariffs,
        mock_taxi_tariffs,
):
    contragent = await create_contragent(load_json('draft.json'))

    draft = load_json('fail_tariff_not_found.json')
    draft['contragent_id'] = contragent['contragent_id']

    @mock_hiring_tariffs('/v1/tariff/')
    async def handler1(request):  # pylint: disable=unused-variable
        return web.json_response(
            {'code': 'TARIFF_NOT_FOUND', 'message': 'Tariff not found'},
            status=404,
        )

    @mock_taxi_tariffs('/v1/tariff_zones')
    async def handler2(request):  # pylint: disable=unused-variable
        return load_json('zones.json')

    response = await web_app_client.post('/v1/contract/', json=draft)
    assert response.status == 400, await response.text()

    content = await response.json()
    assert content['code'] == 'CONTRACT_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'TARIFF_NOT_FOUND'


async def test_time_before(
        load_json,
        create_contragent,
        web_app_client,
        mock_hiring_tariffs,
        mock_taxi_tariffs,
):
    contragent = await create_contragent(load_json('draft.json'))

    draft = load_json('fail_start_before_tariff.json')
    draft['contragent_id'] = contragent['contragent_id']

    @mock_hiring_tariffs('/v1/tariff/')
    async def handler1(request):  # pylint: disable=unused-variable
        return load_json('tariff.json')

    @mock_taxi_tariffs('/v1/tariff_zones')
    async def handler2(request):  # pylint: disable=unused-variable
        return load_json('zones.json')

    response = await web_app_client.post('/v1/contract/', json=draft)
    assert response.status == 400, await response.text()

    content = await response.json()
    assert content['code'] == 'CONTRACT_DEFINITION_ERROR'
    assert (
        content['details']['errors'][0]['code']
        == 'CONTRACT_START_BEFORE_TARIFF'
    )


async def test_geo_not_found(
        load_json,
        create_contragent,
        web_app_client,
        mock_hiring_tariffs,
        mock_taxi_tariffs,
):
    contragent = await create_contragent(load_json('draft.json'))

    draft = load_json('fail_geo_not_found.json')
    draft['contragent_id'] = contragent['contragent_id']

    @mock_hiring_tariffs('/v1/tariff/')
    async def handler1(request):  # pylint: disable=unused-variable
        return load_json('tariff.json')

    @mock_taxi_tariffs('/v1/tariff_zones')
    async def handler2(request):  # pylint: disable=unused-variable
        return load_json('zones.json')

    response = await web_app_client.post('/v1/contract/', json=draft)
    assert response.status == 400, await response.text()

    content = await response.json()
    assert content['code'] == 'CONTRACT_DEFINITION_ERROR'
    assert content['details']['errors'][0]['code'] == 'TARIFF_ZONE_NOT_FOUND'
