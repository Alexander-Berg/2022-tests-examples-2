# pylint: disable=unused-variable


async def test_list(load_json, create_tariff, list_tariffs):
    """Получение списка тарифов"""
    data = load_json('draft.json')

    tariff1 = await create_tariff(data)  # noqa: F841
    tariff2 = await create_tariff(data)  # noqa: F841
    tariff3 = await create_tariff(data)  # noqa: F841

    received = await list_tariffs()

    assert received['time_ts'], 'Время актуальности тарифов установлено'
    assert len(received['tariffs']) == 3, 'Тарифы получены'


async def test_list_active(
        load_json, create_tariff, update_tariff, list_tariffs,
):
    """Получаем только активные ревизии"""
    data = load_json('draft.json')

    tariff_v1 = await create_tariff(data)
    tariff_v2 = await update_tariff(tariff_v1['tariff_id'], data)  # noqa: F841
    tariff_v3 = await update_tariff(tariff_v1['tariff_id'], data)

    received = await list_tariffs()

    assert len(received['tariffs']) == 1, 'Тарифы получены'
    assert (
        received['tariffs'][0]['revision'] == tariff_v3['revision']
    ), 'Список только актуальных ревизий'


async def test_list_after_start(load_json, create_tariff, list_tariffs):
    """Проверка получения списка на будущее время"""
    tariff1 = await create_tariff(load_json('draft.json'))  # noqa: F841
    tariff2 = await create_tariff(load_json('draft_future.json'))  # noqa: F841

    received = await list_tariffs(time_ts=tariff2['start_ts'] + 1)

    assert len(received['tariffs']) == 2, 'Тарифы получены'
    assert (
        received['tariffs'][0]['tariff_id'] == tariff1['tariff_id']
    ), 'Подходящий тариф'
    assert (
        received['tariffs'][1]['tariff_id'] == tariff2['tariff_id']
    ), 'Подходящий тариф'


async def test_list_before_start(load_json, create_tariff, list_tariffs):
    """Проверка получения списка без будущих тарифов"""
    tariff1 = await create_tariff(load_json('draft.json'))  # noqa: F841
    tariff2 = await create_tariff(load_json('draft_future.json'))  # noqa: F841

    received = await list_tariffs(time_ts=tariff2['start_ts'] - 1)

    assert len(received['tariffs']) == 1, 'Тарифы получены'
    assert (
        received['tariffs'][0]['tariff_id'] == tariff1['tariff_id']
    ), 'Подходящий тариф'


async def test_labels(load_json, create_tariff, list_tariffs):
    """Получаем только тарифы с указанными метками"""
    data = load_json('draft.json')

    await create_tariff(data)
    await create_tariff(data, labels=['test1'])
    await create_tariff(data, labels=['test2'])
    matched1 = await create_tariff(data, labels=['test1', 'test3'])
    await create_tariff(data, labels=['test2', 'test3'])
    await create_tariff(data, labels=['test3'])

    received = await list_tariffs(labels=['test1', 'test3'])

    assert len(received['tariffs']) == 1, 'Тарифы получены'
    assert (
        received['tariffs'][0]['tariff_id'] == matched1['tariff_id']
    ), 'Подходящий тариф'
