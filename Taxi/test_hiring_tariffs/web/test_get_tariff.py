# pylint: disable=unused-variable


async def test_get_last_revision(
        load_json, create_tariff, update_tariff, get_tariff,
):
    """Получение текущей ревизии без фильтров"""
    data = load_json('draft.json')

    tariff_v1 = await create_tariff(data)
    tariff_v2 = await update_tariff(tariff_v1['tariff_id'], data)  # noqa: F841
    tariff_v3 = await update_tariff(tariff_v1['tariff_id'], data)

    received = await get_tariff(tariff_id=tariff_v1['tariff_id'])
    assert received['tariff_id'] == tariff_v3['tariff_id'], 'Тариф тот же'
    assert (
        received['revision'] == tariff_v3['revision']
    ), 'Получена последняя ревизия'


async def test_get_current_revision(
        load_json, create_tariff, update_tariff, get_tariff,
):
    """Проверка получения текущей ревизии без будущих ревизий"""
    tariff_v1 = await create_tariff(load_json('draft.json'))
    tariff_v2 = await update_tariff(
        tariff_id=tariff_v1['tariff_id'], data=load_json('draft.json'),
    )
    tariff_v3 = await update_tariff(  # noqa: F841
        tariff_id=tariff_v1['tariff_id'], data=load_json('draft_future.json'),
    )

    received = await get_tariff(tariff_id=tariff_v1['tariff_id'])
    assert received['tariff_id'] == tariff_v2['tariff_id'], 'Тариф тот же'
    assert (
        received['revision'] == tariff_v2['revision']
    ), 'Получена последняя действующая на данный момент ревизия'


async def test_get_by_revision(
        load_json, create_tariff, update_tariff, get_tariff,
):
    """Проверка получения по номеру ревизии"""
    data = load_json('draft.json')

    tariff_v1 = await create_tariff(data)
    tariff_v2 = await update_tariff(tariff_v1['tariff_id'], data)
    tariff_v3 = await update_tariff(tariff_v1['tariff_id'], data)  # noqa: F841

    received = await get_tariff(
        tariff_id=tariff_v2['tariff_id'], revision=tariff_v2['revision'],
    )
    assert received['tariff_id'] == tariff_v2['tariff_id'], 'Тариф тот же'
    assert (
        received['revision'] == tariff_v2['revision']
    ), 'Получена указанная ревизия'


async def test_get_future_by_revision(load_json, create_tariff, get_tariff):
    """Проверка получения по номеру ревизии не зависимо от времени действия"""
    tariff_v1 = await create_tariff(load_json('draft_future.json'))

    received = await get_tariff(
        tariff_id=tariff_v1['tariff_id'], revision=tariff_v1['revision'],
    )
    assert received['tariff_id'] == tariff_v1['tariff_id'], 'Тариф тот же'
    assert (
        received['revision'] == tariff_v1['revision']
    ), 'Получена запрошенная ревизия'


async def test_get_after_start(load_json, create_tariff, get_tariff):
    """Проверка получения ревизии на дату"""
    tariff_v1 = await create_tariff(load_json('draft_future.json'))

    received1 = await get_tariff(
        tariff_id=tariff_v1['tariff_id'], time_ts=tariff_v1['start_ts'],
    )
    assert received1['tariff_id'] == tariff_v1['tariff_id'], 'Тариф тот же'
    assert (
        received1['revision'] == tariff_v1['revision']
    ), 'Получена запрошенная ревизия после начала действия'

    received2 = await get_tariff(
        tariff_id=tariff_v1['tariff_id'], time_ts=tariff_v1['start_ts'] + 1,
    )
    assert received2['tariff_id'] == tariff_v1['tariff_id'], 'Тариф тот же'
    assert (
        received2['revision'] == tariff_v1['revision']
    ), 'Получена запрошенная ревизия много после начала действия'


async def test_get_before_start(
        web_app_client, load_json, create_tariff, get_tariff,
):
    """Проверка получения ревизии до даты начала действия"""
    tariff_v1 = await create_tariff(load_json('draft_future.json'))

    response = await web_app_client.get(
        '/v1/tariff/',
        params={
            'tariff_id': tariff_v1['tariff_id'],
            'time_ts': tariff_v1['start_ts'] - 1,
        },
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'TARIFF_NOT_FOUND'


async def test_not_found(web_app_client):
    unknown_uuid = 'b203883efc21433e9e5a638c1e58bbdb'
    response = await web_app_client.get(
        '/v1/tariff/', params={'tariff_id': unknown_uuid},
    )
    assert response.status == 404, await response.text()
    content = await response.json()

    assert content['code'] == 'TARIFF_NOT_FOUND'
