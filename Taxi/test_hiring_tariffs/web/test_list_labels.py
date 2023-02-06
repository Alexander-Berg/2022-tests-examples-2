# pylint: disable=unused-variable


async def test_list_labels(
        load_json, create_tariff, update_tariff, list_labels,
):
    """Получение списка тарифов"""

    tariff1 = await create_tariff(
        data=load_json('draft.json'), labels=['test1'],
    )
    await update_tariff(
        tariff_id=tariff1['tariff_id'],
        data=load_json('draft.json'),
        labels=['test4'],
    )
    await create_tariff(
        data=load_json('draft.json'), labels=['test2', 'test3'],
    )
    await create_tariff(
        data=load_json('draft.json'), labels=['test1', 'test4'],
    )

    received = await list_labels()

    assert received['time_ts'], 'Время актуальности меток установлено'
    assert received['labels'] == [
        'test1',
        'test2',
        'test3',
        'test4',
    ], 'Метки получены'


async def test_list_labels_after_start(load_json, create_tariff, list_labels):
    """Проверка получения списка на будущее время"""
    tariff1 = await create_tariff(  # noqa: F841
        data=load_json('draft.json'), labels=['test1'],
    )
    tariff2 = await create_tariff(
        data=load_json('draft_future.json'), labels=['test2'],
    )

    received = await list_labels(time_ts=tariff2['start_ts'] + 1)

    assert received['labels'] == ['test1', 'test2'], 'Метки получены'


async def test_list_labels_before_start(load_json, create_tariff, list_labels):
    """Проверка получения списка без будущих тарифов"""
    tariff1 = await create_tariff(  # noqa: F841
        data=load_json('draft.json'), labels=['test1'],
    )
    tariff2 = await create_tariff(
        data=load_json('draft_future.json'), labels=['test2'],
    )

    received = await list_labels(time_ts=tariff2['start_ts'] - 1)

    assert received['labels'] == ['test1'], 'Метки получены'
