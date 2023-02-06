async def test_country_config_get_one_country(taxi_eats_restapp_places):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/country-config?countries=RU',
    )

    assert response.status_code == 200
    assert response.json() == {
        'countries': {
            'RU': {
                'country_name': {
                    'english': 'Russian Federation',
                    'russian': 'Российская Федерация',
                },
                'currency': {
                    'name': 'российский рубль',
                    'short_name': 'руб.',
                    'sign': '₽',
                },
                'language': {'base': 'ru', 'fallback': 'en'},
                'links': {
                    'clients': {
                        'help': 'cl_help',
                        'user_aggreement': 'cl_aggreement',
                    },
                    'couriers': {
                        'help': 'co_help',
                        'user_aggreement': 'co_aggreement',
                    },
                    'partners': {
                        'help': 'pa_help',
                        'user_aggreement': 'pa_aggreement',
                    },
                },
                'maximum_coupon_sum': '3000',
                'minimal_order_sum': '200',
                'phone': {
                    'code': '+7',
                    'digits_number': 10,
                    'format': '+79000000000',
                    'mask': '+79000000000',
                },
                'region_id': 'ru',
                'support': {
                    'email_ids': ['ru_email1', 'ru_email2'],
                    'phone_ids': ['ru_phone1', 'ru_phone2'],
                },
                'vat': ['0', '10', '18', '20'],
            },
        },
    }


async def test_country_config_get_two_country_one_not_found(
        taxi_eats_restapp_places,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/country-config?countries=BY,AR',
    )

    assert response.status_code == 200
    assert response.json() == {
        'countries': {
            'BY': {
                'country_name': {
                    'english': 'Republic of Belarus',
                    'russian': 'Республика Беларусь',
                },
                'currency': {
                    'name': 'Белорусский рубль',
                    'short_name': 'руб.',
                    'sign': 'Br',
                },
                'language': {'base': 'ru', 'fallback': 'en'},
                'links': {
                    'clients': {
                        'help': 'cl_help_by',
                        'user_aggreement': 'cl_aggreement_by',
                    },
                    'couriers': {
                        'help': 'co_help_by',
                        'user_aggreement': 'co_aggreement_by',
                    },
                    'partners': {
                        'help': 'pa_help_by',
                        'user_aggreement': 'pa_aggreement_by',
                    },
                },
                'maximum_coupon_sum': '300',
                'minimal_order_sum': '10',
                'phone': {
                    'code': '+375',
                    'digits_number': 9,
                    'format': '+375000000000',
                    'mask': '+375000000000',
                },
                'region_id': 'by',
                'support': {
                    'email_ids': ['by_email1', 'by_email2'],
                    'phone_ids': ['by_phone1', 'by_phone2'],
                },
                'vat': ['0', '10', '20', '25'],
            },
        },
    }


async def test_country_config_get_one_country_not_found(
        taxi_eats_restapp_places,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/country-config?countries=AR',
    )

    assert response.status_code == 200
    assert response.json() == {'countries': {}}
