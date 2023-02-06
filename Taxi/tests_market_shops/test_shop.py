# flake8: noqa
# pylint: disable=import-error,wildcard-import


async def test_shop_not_found(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [0]},
    )
    assert response.status_code == 200
    assert response.json() == {'shops': []}


async def test_shop(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [1]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'shops': [
            {
                'id': 1,
                'name': 'Одинокий FBY 5',
                'business_id': 11299027,
                'business_name': 'Одинокий FBY 5',
                'slug': 'odinokii-fby-5',
                'grades_count': 0,
                'quality_rating': 0,
                'shop_new_rating': {
                    'rating_type': 6,
                    'final_rating': 0,
                    'new_grades_count_3m': 0,
                    'new_grades_count_total': 1,
                    'overall_grades_count': 1,
                    'abo_grade_base': 0,
                    'abo_grade_total': 0,
                    'new_rating_3m': 0,
                    'new_rating_total': 0,
                    'skk_disabled': False,
                    'abo_old_rating': 0,
                    'abo_old_raw_rating': 0,
                },
                'is_global': False,
                'is_cpa_prior': False,
                'is_cpa_partner': True,
                'supplier_type': '3',
                'tax_system': 'OSN',
                'warehouse_id': 300,
                'work_schedule': 'Пн-Пт: 10:00-19:00, Сб-Вс: 10:00-18:00',
                'loyalty_program_status': 'DISABLED',
                'is_eats': False,
                'logo': {
                    'width': 14,
                    'height': 14,
                    'url': (
                        '//avatars.mds.yandex.net/get-market-shop-logo/1/small'
                    ),
                    'extension': 'PNG',
                    'thumbnails': [
                        {
                            'id': '14x14',
                            'container_width': 14,
                            'container_height': 14,
                            'width': 14,
                            'height': 14,
                            'densities': [
                                {
                                    'id': '1',
                                    'url': '//avatars.mds.yandex.net/get-market-shop-logo/1/small',
                                },
                                {
                                    'id': '2',
                                    'url': '//avatars.mds.yandex.net/get-market-shop-logo/1/orig',
                                },
                            ],
                        },
                    ],
                },
                'created_at': '2021-04-05T11:22:15',
                'main_created_at': '2021-04-05T11:22:15',
                'phones': {
                    'raw': '+7 (495) 2323232',
                    'sanitized': '+74952323232',
                },
                'home_region': {'id': 225, 'name': 'Россия'},
                'feeds': {
                    'first_id': 201195634,
                    'last_id': 201195643,
                    'count': 2,
                },
                'is_fulfillment_program': True,
                'is_click_and_collect': False,
            },
        ],
    }


async def test_shop_new_rating(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [6]},
    )
    assert response.status_code == 200
    assert 'shopNewRating' not in response.json()['shops'][0]

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [9]},
    )
    assert response.status_code == 200
    assert (
        response.json()['shops'][0]['shop_new_rating']['new_rating_total']
        == 4.430167597765363
    )
    assert (
        response.json()['shops'][0]['shop_new_rating'][
            'new_grades_count_total'
        ]
        == 179
    )


async def test_shop_oper_rating(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [4]},
    )
    assert response.status_code == 200
    assert 'operationalRating' not in response.json()['shops'][0]

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [5]},
    )
    assert response.status_code == 200
    assert (
        response.json()['shops'][0]['operational_rating']['calc_time']
        == 1647824512473
    )
    assert (
        response.json()['shops'][0]['operational_rating']['late_ship_rate']
        == 100.0
    )


async def test_shop_logo(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [1]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['logo'] == {
        'width': 14,
        'height': 14,
        'url': '//avatars.mds.yandex.net/get-market-shop-logo/1/small',
        'extension': 'PNG',
        'thumbnails': [
            {
                'id': '14x14',
                'container_width': 14,
                'container_height': 14,
                'width': 14,
                'height': 14,
                'densities': [
                    {
                        'id': '1',
                        'url': '//avatars.mds.yandex.net/get-market-shop-logo/1/small',
                    },
                    {
                        'id': '2',
                        'url': '//avatars.mds.yandex.net/get-market-shop-logo/1/orig',
                    },
                ],
            },
        ],
    }

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [2]},
    )
    assert response.status_code == 200
    assert 'logo' not in response.json()['shops'][0]

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [10]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['logo'] == {
        'width': 20,
        'height': 20,
        'url': '//avatars.mds.yandex.net/get-market-shop-logo/2/small',
        'extension': 'PNG',
        'thumbnails': [
            {
                'id': '20x20',
                'container_width': 20,
                'container_height': 20,
                'width': 20,
                'height': 20,
                'densities': [
                    {
                        'id': '1',
                        'url': '//avatars.mds.yandex.net/get-market-shop-logo/2/small',
                    },
                ],
            },
        ],
    }


async def test_shop_clones(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [1]},
    )
    assert response.status_code == 200
    assert (
        response.json()['shops'][0]['created_at']
        == response.json()['shops'][0]['main_created_at']
    )

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [3]},
    )
    assert response.status_code == 200
    assert 'created_at' not in response.json()['shops'][0]
    assert 'main_created_at' not in response.json()['shops'][0]

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [5]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['created_at'] == '2021-01-01T00:00:00'
    assert (
        response.json()['shops'][0]['main_created_at'] == '2021-01-01T00:00:00'
    )

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [9]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['created_at'] == '2021-01-02T00:00:00'
    assert (
        response.json()['shops'][0]['main_created_at'] == '2021-01-01T00:00:00'
    )


async def test_shop_phones(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [1]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['phones'] == {
        'raw': '+7 (495) 2323232',
        'sanitized': '+74952323232',
    }

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [2]},
    )
    assert response.status_code == 200
    assert 'phones' not in response.json()['shops'][0]

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [3]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['phones'] == {
        'raw': '8 800 200-22-33',
        'sanitized': '88002002233',
    }


async def test_shop_regions(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [1]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['home_region'] == {
        'id': 225,
        'name': 'Россия',
    }

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [2]},
    )
    assert response.status_code == 200
    assert 'home_region' not in response.json()['shops'][0]

    response = await taxi_market_shops.post(
        'market-shops/v1/shop', {'ids': [3]},
    )
    assert response.status_code == 200
    assert response.json()['shops'][0]['home_region'] == {
        'id': 134,
        'name': 'Китай',
    }
