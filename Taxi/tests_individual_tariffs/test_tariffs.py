import pytest

MOSCOW_TARIFF_ID = '5caeed9d1bc8d21af5a07a24'


@pytest.mark.parametrize(
    ['category_id', 'expected_status', 'expected_file'],
    [
        ('05156a5d865a429a960ddb4dde20e735', 200, 'moscow.json'),
        ('59d3027127a542989074e7cdfe6122a5', 200, 'moscow.json'),
    ],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_get_tariff_by_category(
        taxi_individual_tariffs,
        category_id,
        expected_status,
        expected_file,
        load_json,
):
    response = await taxi_individual_tariffs.get(
        '/v1/tariff/by_category',
        params={'category_id': category_id, 'requested_categories': 'ALL'},
    )
    data = response.json()
    assert response.status == expected_status
    assert data == load_json(expected_file)


@pytest.mark.parametrize(
    ['category_id', 'expected_status', 'expected_data'],
    [
        (
            'not_found_id',
            404,
            {
                'code': 'category_not_found',
                'message': (
                    'Can not find tariff with category_id: not_found_id'
                ),
            },
        ),
        (
            MOSCOW_TARIFF_ID,
            404,
            {
                'code': 'category_not_found',
                'message': (
                    f'Can not find tariff with category_id: {MOSCOW_TARIFF_ID}'
                ),
            },
        ),
    ],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_get_tariff_by_category_failed(
        taxi_individual_tariffs, category_id, expected_status, expected_data,
):
    response = await taxi_individual_tariffs.get(
        '/v1/tariff/by_category',
        params={'category_id': category_id, 'requested_categories': 'ALL'},
    )
    data = response.json()
    assert response.status == expected_status
    assert data == expected_data


@pytest.mark.parametrize(
    ['test_data_json'],
    [('test_data_if_success.json',), ('test_data_if_failed.json',)],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_get_tariff_category(
        taxi_individual_tariffs, test_data_json, load_json,
):
    test_data = load_json(test_data_json)
    tariff_category_id = test_data['tariff_category_id']
    expected_status = test_data['expected_status']
    expected_data = test_data['expected_data']

    response = await taxi_individual_tariffs.get(
        '/v1/tariff/by_category',
        params={
            'category_id': tariff_category_id,
            'requested_categories': 'SELECTED_ONLY',
        },
    )
    data = response.json()

    assert response.status == expected_status
    assert data == expected_data


EXPECTED_TARIFFS = [
    {
        'id': MOSCOW_TARIFF_ID,
        'home_zone': 'moscow',
        'activation_zone': 'moscow_activation',
        'related_zones': ['moscow', 'moscow_activation', 'foo'],
        'categories': ['econom', 'mkk', 'vip'],
        'city_id': '\\u041c\\u043e\\u0441\\u043a\\u0432\\u0430',
        'country': 'rus',
        'timezone': 'moscow',
    },
    {
        'id': '5caeed9d1bc8d21af5a07a25',
        'home_zone': 'spb',
        'activation_zone': 'spb_activation',
        'related_zones': ['spb', 'spb_activation', 'bar'],
        'categories': [],
        'city_id': '\\u941c\\u043e\\u0441\\u043a\\u0432\\u0430',
        'country': 'rus',
        'timezone': 'spb',
    },
]


@pytest.mark.experiments3(filename='mongo_config_mapping.json')
@pytest.mark.filldb(tariffs='get_tariffs_test')
async def test_get_tariffs(taxi_individual_tariffs, load_json):
    for expected_tariff in EXPECTED_TARIFFS:
        expected_tariff['related_zones'].sort()
        expected_tariff['categories'].sort()
    response = await taxi_individual_tariffs.get(
        '/internal/v1/tariffs/summary',
    )
    data = response.json()
    assert response.status == 200

    minimal_prices = list()
    for tariff in data['tariffs']:
        tariff['related_zones'].sort()
        tariff['categories'].sort()
        if tariff.get('minimal_prices') is not None:
            minimal_prices.extend(tariff.pop('minimal_prices'))

    data['tariffs'].sort(key=lambda x: x['id'])
    assert data['tariffs'] == EXPECTED_TARIFFS
    assert minimal_prices == load_json('extended_with_price.json')
