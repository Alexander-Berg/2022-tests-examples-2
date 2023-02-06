import pytest


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_coefficients.sql'],
)
async def test_coefficients_get(taxi_eats_logistics_performer_payouts):
    def sorted_resp(data):
        for element in data:
            for element_cf in element['coefficients']:
                element_cf = dict(element_cf)
            element['coefficients'] = sorted(
                element['coefficients'], key=lambda x: x['name'],
            )
            element['context'] = dict(element['context'])
        return sorted(
            data,
            key=lambda x: (
                x['context']['country_id'],
                x['context']['region_id'],
                x['context']['pool'],
                x['context']['courier_type'],
            ),
        )

    expected_response = [
        {
            'coefficients': [
                {
                    'is_fallback': False,
                    'name': 'fine_thresh_early',
                    'value': 10.0,
                },
            ],
            'context': {
                'country_id': '1',
                'courier_type': 'picker',
                'pool': 'shop',
                'region_id': '1',
            },
        },
        {
            'coefficients': [],
            'context': {
                'country_id': '1',
                'courier_type': 'vehicle',
                'pool': 'shop',
                'region_id': '1',
            },
        },
        {
            'coefficients': [],
            'context': {
                'country_id': '1',
                'courier_type': 'bicycle',
                'pool': 'shop',
                'region_id': '1',
            },
        },
        {
            'coefficients': [],
            'context': {
                'country_id': '1',
                'courier_type': 'vehicle',
                'pool': 'eda',
                'region_id': '1',
            },
        },
        {
            'coefficients': [],
            'context': {
                'country_id': '1',
                'courier_type': 'electric_bicycle',
                'pool': 'eda',
                'region_id': '1',
            },
        },
        {
            'coefficients': [],
            'context': {
                'country_id': '1',
                'courier_type': 'bicycle',
                'pool': 'eda',
                'region_id': '1',
            },
        },
        {
            'coefficients': [],
            'context': {
                'country_id': '1',
                'courier_type': 'motorcycle',
                'pool': 'eda',
                'region_id': '1',
            },
        },
        {
            'coefficients': [
                {
                    'is_fallback': False,
                    'name': 'fine_thresh_early',
                    'value': 10.0,
                },
                {
                    'is_fallback': True,
                    'name': 'fine_thresh_late',
                    'value': 10.0,
                },
            ],
            'context': {
                'country_id': '1',
                'courier_type': 'pedestrian',
                'pool': 'eda',
                'region_id': '1',
            },
        },
    ]

    response = await taxi_eats_logistics_performer_payouts.get(
        '/v1/admin/coefficients', params={'country_id': '1', 'region_id': '1'},
    )
    assert response.status_code == 200
    assert sorted_resp(response.json()['payload']) == sorted_resp(
        expected_response,
    )


async def test_coefficients_post(taxi_eats_logistics_performer_payouts, pgsql):
    request = {
        'context': {
            'country_id': '1',
            'region_id': '1',
            'pool': 'eda',
            'courier_type': 'pedestrian',
        },
        'coefficients': [
            {'name': 'per_hour_guarantee', 'value': 100.0},
            {'name': 'fine_thresh_early', 'value': 10.0},
        ],
    }
    select_coefficients = f"""
    SELECT coefficients
    FROM eats_logistics_performer_payouts.coefficients_values
    WHERE country_id = '1' AND region_id = '1' AND
          pool = 'eda' AND courier_type = 'pedestrian'
    """

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/admin/coefficients', json=request,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_logistics_performer_payouts'].cursor()
    cursor.execute(select_coefficients)
    assert {'fine_thresh_early': 10.0, 'per_hour_guarantee': 100.0} == list(
        cursor,
    )[0][0]


async def test_coefficients_check_post(taxi_eats_logistics_performer_payouts):
    def sorted_resp(data):
        def sort_el(elem):
            for coeff in elem['coefficients']:
                coeff = dict(coeff)
            elem['coefficients'] = sorted(
                elem['coefficients'], key=lambda x: x['name'],
            )
            elem['context'] = dict(elem['context'])

        sort_el(data['data'])
        sort_el(data['diff']['current'])
        sort_el(data['diff']['new'])

        return dict(data)

    request = {
        'context': {
            'country_id': '1',
            'region_id': '1',
            'pool': 'eda',
            'courier_type': 'pedestrian',
        },
        'coefficients': [
            {'name': 'per_hour_guarantee', 'value': 100.0},
            {'name': 'fine_thresh_early', 'value': 10.0},
        ],
    }
    expected_response = {
        'change_doc_id': 'eats-logistics_performer_payouts_1_1_eda_pedestrian',
        'data': {
            'coefficients': [
                {'name': 'per_hour_guarantee', 'value': 100.0},
                {'name': 'fine_thresh_early', 'value': 10.0},
            ],
            'context': {
                'country_id': '1',
                'courier_type': 'pedestrian',
                'pool': 'eda',
                'region_id': '1',
            },
        },
        'diff': {
            'current': {
                'coefficients': [],
                'context': {
                    'country_id': '1',
                    'courier_type': 'pedestrian',
                    'pool': 'eda',
                    'region_id': '1',
                },
            },
            'new': {
                'coefficients': [
                    {'name': 'per_hour_guarantee', 'value': 100.0},
                    {'name': 'fine_thresh_early', 'value': 10.0},
                ],
                'context': {
                    'country_id': '1',
                    'courier_type': 'pedestrian',
                    'pool': 'eda',
                    'region_id': '1',
                },
            },
        },
    }

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/admin/coefficients/check', json=request,
    )
    assert response.status_code == 200
    assert sorted_resp(response.json()) == sorted_resp(expected_response)


@pytest.mark.parametrize(
    'route_input',
    [
        (
            {
                'context': {
                    'country_id': '1',
                    'region_id': '1',
                    'pool': 'eda',
                    'courier_type': 'picker',
                },
                'coefficients': {
                    'per_hour_guarantee': 100.0,
                    'fine_thresh_early': 10.0,
                },
            }
        ),
        (
            {
                'context': {
                    'country_id': '1',
                    'region_id': '1',
                    'pool': 'eda',
                    'courier_type': 'predestrian',
                },
                'coefficients': {'random_coefficient': 10.0},
            }
        ),
    ],
)
async def test_coefficients_post_400(
        taxi_eats_logistics_performer_payouts, route_input,
):
    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/admin/coefficients', json=route_input,
    )
    assert response.status_code == 400
    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/admin/coefficients/check', json=route_input,
    )
    assert response.status_code == 400


async def test_coefficients_layout_get(taxi_eats_logistics_performer_payouts):
    def sorted_resp(data):
        for data_el in data['coefficients']:
            data_el = dict(data_el)
        data['coefficients'] = sorted(
            data['coefficients'], key=lambda x: x['name'],
        )

        for data_el in data['contexts']:
            data_el = dict(data_el)
            if 'available_values' in data_el:
                for data_el_av in data_el['available_values']:
                    data_el_av = dict(data_el_av)
                    if 'available_pools' in data_el_av:
                        data_el_av['available_pools'] = sorted(
                            data_el_av['available_pools'],
                        )
                data_el['available_values'] = sorted(
                    data_el['available_values'], key=lambda x: x['value'],
                )
        data['contexts'] = sorted(data['contexts'], key=lambda x: x['name'])

        for data_el in data['sections']:
            data_el = dict(data_el)
        data['sections'] = sorted(data['sections'], key=lambda x: x['name'])

    expected_response = {
        'coefficients': [
            {
                'description': 'Ранний уход со смены (мин)',
                'name': 'fine_thresh_early',
                'section': 'guarantee',
                'type': 'decimal',
            },
            {
                'description': 'Опоздание на смену (мин)',
                'name': 'fine_thresh_late',
                'section': 'guarantee',
                'type': 'decimal',
            },
            {
                'description': 'Ранний уход со смены (мин)',
                'name': 'fine_thresh_max_early',
                'section': 'fines',
                'type': 'decimal',
            },
            {
                'description': 'Опоздание на смену (мин)',
                'name': 'fine_thresh_max_late',
                'section': 'fines',
                'type': 'decimal',
            },
            {
                'description': 'Время оффлайн (%)',
                'name': 'fine_thresh_offline',
                'section': 'guarantee',
                'type': 'decimal',
            },
            {
                'description': 'Длинный путь до ресторана начинается от (м)',
                'name': 'long_to_rest_thresh_m',
                'section': 'settings',
                'type': 'decimal',
            },
            {
                'description': (
                    'Оплата за вовремя доставленный заказ ' '(валюта страны)'
                ),
                'name': 'per_drop_off',
                'section': 'rates',
                'type': 'decimal',
            },
            {
                'description': 'Минималка в час (валюта страны)',
                'name': 'per_hour_guarantee',
                'section': 'guarantee',
                'type': 'decimal',
            },
            {
                'description': 'Оплата за путь до клиента (валюта страны)',
                'name': 'per_km_to_client',
                'section': 'rates',
                'type': 'decimal',
            },
            {
                'description': 'Оплата за путь до ресторана (валюта страны)',
                'name': 'per_long_to_rest',
                'section': 'rates',
                'type': 'decimal',
            },
            {
                'description': (
                    'Оплата за вовремя взятый заказ (валюта страны)'
                ),
                'name': 'per_pickup',
                'section': 'rates',
                'type': 'decimal',
            },
        ],
        'contexts': [
            {'name': 'country_id', 'description': 'Страна'},
            {
                'name': 'courier_type',
                'description': 'Тип курьера',
                'available_values': [
                    {
                        'value': 'picker',
                        'description': 'Сборщик',
                        'available_pools': ['shop'],
                    },
                    {
                        'value': 'vehicle',
                        'description': 'Авто',
                        'available_pools': ['shop', 'eda'],
                    },
                    {
                        'value': 'electric_bicycle',
                        'description': 'Электровелосипед',
                        'available_pools': ['eda'],
                    },
                    {
                        'value': 'bicycle',
                        'description': 'Велосипед',
                        'available_pools': ['shop', 'eda'],
                    },
                    {
                        'value': 'motorcycle',
                        'description': 'Мотоцикл',
                        'available_pools': ['eda'],
                    },
                    {
                        'value': 'pedestrian',
                        'description': 'Пешеход',
                        'available_pools': ['eda'],
                    },
                ],
            },
            {
                'name': 'pool',
                'description': 'Поставщик заказов',
                'available_values': [
                    {'value': 'shop', 'description': 'Ритейл'},
                    {'value': 'eda', 'description': 'Еда'},
                ],
            },
            {'name': 'region_id', 'description': 'Регион'},
        ],
        'sections': [
            {'name': 'fines', 'description': 'Штрафы'},
            {'name': 'guarantee', 'description': 'Гарантия минималки'},
            {'name': 'rates', 'description': 'Ставки'},
            {'name': 'settings', 'description': 'Настройки'},
        ],
    }

    response = await taxi_eats_logistics_performer_payouts.get(
        '/v1/admin/coefficients/layout',
    )
    assert response.status_code == 200
    assert sorted_resp(response.json()) == sorted_resp(expected_response)
