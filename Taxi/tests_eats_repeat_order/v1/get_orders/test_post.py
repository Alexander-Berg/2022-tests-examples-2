import pytest

PATH = '/v1/get-orders'
MOCK_HANDLER = '/eats-ordershistory/v1/get-orders'


@pytest.mark.parametrize(
    'params',
    [
        # without params
        {},
        # only one param
        {'user_id': 123},
        {'places': [1, 2, 3]},
        # wrong types
        {'user_id': '123', 'places': [1, 2, 3]},
        {'user_id': 123, 'places': ['a', 'b', 'c']},
        # empty places
        {'user_id': '123', 'places': []},
    ],
)
async def test_wrong_input(taxi_eats_repeat_order, params):
    # проверка некорректного ввода
    response = await taxi_eats_repeat_order.post(PATH, json=params)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'body, fixture_file, expected_orders_ids',
    [
        ({'user_id': 1, 'places': [1]}, 'unordered-orders.json', ['oid-3']),
        ({'user_id': 1, 'places': [2]}, 'unordered-orders.json', ['oid-5']),
        (
            {'user_id': 1, 'places': [1, 2]},
            'unordered-orders.json',
            ['oid-3', 'oid-5'],
        ),
    ],
)
async def test_find_last_order(
        taxi_eats_repeat_order,
        mockserver,
        load_json,
        body,
        fixture_file,
        expected_orders_ids,
):
    # тест проверяет, что по запрошенному ресторану
    # выбирается самый последний по хронологии заказ
    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory(request):
        return load_json(fixture_file)

    response = await taxi_eats_repeat_order.post(PATH, json=body)

    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == len(expected_orders_ids)
    for order in orders:
        assert order['order_id'] in expected_orders_ids


@pytest.mark.parametrize(
    'body, fixture_file, expected_places_ids',
    [
        ({'user_id': 1, 'places': [1]}, 'many-places.json', [1]),
        ({'user_id': 1, 'places': [2]}, 'many-places.json', [2]),
        (
            {'user_id': 1, 'places': [1, 2, 5, 6, 7]},
            'many-places.json',
            [1, 2, 5],
        ),
    ],
)
async def test_find_places(
        taxi_eats_repeat_order,
        mockserver,
        load_json,
        body,
        fixture_file,
        expected_places_ids,
):
    # тест проверяет, что ответ содержит
    # только запрашиваемые рестораны
    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory(request):
        return load_json(fixture_file)

    response = await taxi_eats_repeat_order.post(PATH, json=body)

    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == len(expected_places_ids)
    for order in orders:
        assert order['place_id'] in expected_places_ids


@pytest.mark.parametrize(
    'body, fixture_file, expected_orders',
    [
        (
            {'user_id': 1, 'places': [1]},
            'response-content.json',
            [
                {
                    'description': '4x title-1',
                    'order_id': 'oid-1',
                    'place_id': 1,
                },
            ],
        ),
        (
            {'user_id': 1, 'places': [2]},
            'response-content.json',
            [
                {
                    'description': (
                        '2x title-1, 1x яблоко, 2x соус «хайнс» сырный'
                    ),
                    'order_id': 'oid-2',
                    'place_id': 2,
                },
            ],
        ),
        (
            {'user_id': 1, 'places': [3, 4]},
            'response-content.json',
            [
                {
                    'description': (
                        '1x This is very long '
                        + 'string very long string '
                        + 'very long string veryvery long '
                        + 'string, 2x This '
                        + 'is very long string very '
                        + 'long string very long '
                        + 'string veryvery long string, '
                        + '3x This is very long string v...'
                    ),
                    'order_id': 'oid-3',
                    'place_id': 3,
                },
                {
                    'description': '10x title-1',
                    'order_id': 'oid-4',
                    'place_id': 4,
                },
            ],
        ),
    ],
)
async def test_response_content(
        taxi_eats_repeat_order,
        mockserver,
        load_json,
        body,
        fixture_file,
        expected_orders,
):
    # тест проверяет «содержимое» возвращаемых моделей
    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory(request):
        return load_json(fixture_file)

    response = await taxi_eats_repeat_order.post(PATH, json=body)

    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == len(expected_orders)
    for order in orders:
        assert order in expected_orders


@pytest.mark.config(
    EATS_REPEAT_ORDER_SETTINGS={
        'history_days': 60,
        'max_history_size': 100,
        'max_description_length': 200,
    },
)
async def test_using_cache(taxi_eats_repeat_order, mockserver, load_json):
    # тест проверяет что данные берутся из кэша
    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory1(request):
        return load_json('first.json')

    response = await taxi_eats_repeat_order.post(
        PATH, json={'user_id': 1, 'places': [1, 2]},
    )
    assert response.status_code == 200

    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory2(request):
        return load_json('second.json')

    response = await taxi_eats_repeat_order.post(
        PATH, json={'user_id': 1, 'places': [1, 2]},
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == 1
    expected_orders_ids = ['oid-1']
    for order in orders:
        assert order['order_id'] in expected_orders_ids


@pytest.mark.parametrize('max_history_size', [1, 2, 3, 4, 5])
async def test_max_history_size(
        taxi_eats_repeat_order,
        mockserver,
        load_json,
        taxi_config,
        max_history_size,
):
    # тест проверяет параметр конфигцрации `max_history_size`
    config = {
        'history_days': 60,
        'max_history_size': max_history_size,
        'max_description_length': 200,
    }
    taxi_config.set(EATS_REPEAT_ORDER_SETTINGS=config)

    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory(request):
        return load_json('many-places.json')

    response = await taxi_eats_repeat_order.post(
        PATH, json={'user_id': 1, 'places': [1, 2, 3, 4, 5]},
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == max_history_size


@pytest.mark.parametrize(
    'max_history_size, expected_orders_ids',
    [
        (1, ['oid-6']),
        (2, ['oid-6', 'oid-8']),
        (3, ['oid-6', 'oid-8', 'oid-7']),
        (4, ['oid-6', 'oid-8', 'oid-7', 'oid-3']),
    ],
)
async def test_cache_history(
        taxi_eats_repeat_order,
        mockserver,
        load_json,
        taxi_config,
        max_history_size,
        expected_orders_ids,
):
    # тест проверяет что если сервис получает от сервиса
    # `eats-ordershistory` больше ресторанов чем параметр
    # конфигурирования `max_history_size`, то в этом случае
    # в выборку попадут наиболее «свежие» заказы
    config = {
        'history_days': 60,
        'max_history_size': max_history_size,
        'max_description_length': 200,
    }
    # await taxi_eats_repeat_order.invalidate_caches()
    taxi_config.set(EATS_REPEAT_ORDER_SETTINGS=config)

    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory(request):
        return load_json('unordered-orders.json')

    response = await taxi_eats_repeat_order.post(
        PATH, json={'user_id': 1, 'places': [1, 2, 3, 4, 5, 6]},
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == len(expected_orders_ids)
    for order in orders:
        assert order['order_id'] in expected_orders_ids


def limit_string(string, limit, ellipsis):
    if len(string) <= limit:
        return string
    return string[0 : limit - len(ellipsis)] + ellipsis


@pytest.mark.parametrize('max_description_length', [5, 10, 20, 30, 100])
async def test_max_description_length(
        taxi_eats_repeat_order,
        mockserver,
        load_json,
        taxi_config,
        max_description_length,
):
    # тест проверяет параметр конфигцрации `max_description_length`
    config = {
        'history_days': 60,
        'max_history_size': 100,
        'max_description_length': max_description_length,
    }
    taxi_config.set(EATS_REPEAT_ORDER_SETTINGS=config)

    @mockserver.json_handler(MOCK_HANDLER)
    def _mock_eats_ordershistory(request):
        return load_json('unordered-orders.json')

    response = await taxi_eats_repeat_order.post(
        PATH, json={'user_id': 1, 'places': [1, 2, 3, 4, 5, 6]},
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    expected_descriptions = {
        'oid-1': '1x большая строка с русскими символами',
        'oid-2': '1x title-1',
        'oid-3': '4x title-1 с русскими символами',
        'oid-4': '1x title-1 парам-па-пам пурум-пум пум',
        'oid-5': '4x title-1 о-ло-ло-тро-ло-ло',
        'oid-6': (
            '1x This is very long string very long '
            + 'string very long string veryvery long string, '
            + '1x This is very long string very long string '
            + 'very long string veryvery long string'
        ),
        'oid-7': '1x title-1',
        'oid-8': (
            '1x ооочень длинная строка с русскими и английскими '
            + 'символами title-1 This is very long string very long '
            + 'string very long string veryvery long string'
        ),
        'oid-9': '1x title-1 The quick brown fox jumps over the lazy dog',
    }
    for order in orders:
        assert order['description'] == limit_string(
            expected_descriptions[order['order_id']],
            max_description_length,
            '...',
        )
        # assert len(order['description']) <= max_description_length
