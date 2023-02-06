# pylint: disable=unused-variable


async def test_list(load_json, create_contragent, list_contragents):
    """Получение списка контрагентов"""
    data = load_json('draft.json')

    contragent1 = await create_contragent(data, name='Тест 2')
    contragent2 = await create_contragent(data, name='Тест 1')
    contragent3 = await create_contragent(data, name='Тест 3')

    received = await list_contragents()

    assert received['time_ts'], 'Время актуальности установлено'
    assert len(received['contragents']) == 3, 'Контрагенты получены'

    assert received['contragents'][0]['contragent_id'] == (
        contragent2['contragent_id']
    ), 'Правильный порядок сортировки'
    assert received['contragents'][1]['contragent_id'] == (
        contragent1['contragent_id']
    ), 'Правильный порядок сортировки'
    assert received['contragents'][2]['contragent_id'] == (
        contragent3['contragent_id']
    ), 'Правильный порядок сортировки'


async def test_categories(load_json, create_contragent, list_contragents):
    """Получаем только контрагента с указанным типом"""
    data = load_json('draft.json')

    await create_contragent(data, category='taxiparks', name='Тест 1')
    contragent2 = await create_contragent(data, category='foo', name='Тест 2')
    contragent3 = await create_contragent(data, category='bar', name='Тест 3')

    received = await list_contragents(categories=['foo', 'bar'])
    assert len(received['contragents']) == 2, 'Контрагенты получены'

    contragent_ok1 = received['contragents'][0]
    assert (
        contragent_ok1['contragent_id'] == contragent2['contragent_id']
    ), 'Подходящий контрагент'

    contragent_ok2 = received['contragents'][1]
    assert (
        contragent_ok2['contragent_id'] == contragent3['contragent_id']
    ), 'Подходящий контрагент'


async def test_offset_limit(load_json, create_contragent, list_contragents):
    """Пагинация"""
    data = load_json('draft.json')

    await create_contragent(data, name='Тест 1')
    contragent2 = await create_contragent(data, name='Тест 2')
    contragent3 = await create_contragent(data, name='Тест 3')
    await create_contragent(data, name='Тест 4')

    received = await list_contragents(offset=1, limit=2)
    assert len(received['contragents']) == 2, 'Контрагенты получены'

    contragent_ok2 = received['contragents'][0]
    assert (
        contragent_ok2['contragent_id'] == contragent2['contragent_id']
    ), 'Подходящий контрагент'
    contragent_ok3 = received['contragents'][1]
    assert (
        contragent_ok3['contragent_id'] == contragent3['contragent_id']
    ), 'Подходящий контрагент'
