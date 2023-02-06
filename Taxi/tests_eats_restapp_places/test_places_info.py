PARTNER_ID = 1
PLACE_ID = 42

EXPECTED_200_RESPONSE = {
    'payload': {
        'billing': {
            'inn': '9705114405',
            'kpp': '770501001',
            'bik': '044525225',
            'account': '40702810638000093677',
            'name': 'ООО "ЯНДЕКС.ЕДА"',
            'address': {
                'postcode': '115035',
                'full': 'Москва, ул Садовническая, д 82, стр 2, пом 3',
            },
            'post_address': {
                'postcode': '115035',
                'full': 'Москва, ул Садовническая, д 82, стр 2, пом 3',
            },
            'accountancy_phone': {
                'number': '+79850635243',
                'type': 'accountancy',
                'description': '',
            },
            'accountancy_email': 'lkozhokar@yandex-team.ru',
            'signer': {
                'name': 'Масюк Дмитрий Викторович',
                'position': 'ГЕНЕРАЛЬНЫЙ ДИРЕКТОР',
                'authority_doc': 'Устав',
                'authority_details': None,
            },
            'balance_external_id': '298036/19',
            'balance_date_start': '2019-07-12',
        },
        'billing_info': [
            {'key': 'ИНН', 'value': '9705114405'},
            {'key': 'Расчётный счет', 'value': '40702810638000093677'},
            {'key': 'Почтовый индекс', 'value': '115035'},
            {
                'key': 'Юридический адрес',
                'value': 'Москва, ул Садовническая, д 82, стр 2, пом 3',
            },
        ],
        'has_plus': True,
        'first_plus_activation_date': '2022-05-01T00:00:00+00:00',
        'info': {
            'name': 'В лаваше 1',
            'type': 'native',
            'address': {
                'country': 'Российская Федерация',
                'city': 'Москва',
                'street': 'Лесная улица',
                'building': '5',
                'full': 'Россия, Москва, Лесная улица, 5',
            },
            'phones': [
                {
                    'number': '+79999999991',
                    'type': 'official',
                    'description': 'Коммент14',
                },
                {
                    'number': '+77999999993',
                    'type': 'lpr',
                    'description': 'Коммент13',
                },
            ],
            'email': 'yzdanov@koseleva.com',
            'lpr_email': 'yzdanov4@koseleva.com, yzdanov7@koseleva.com',
            'payments': ['Наличный расчет', 'Безналичный расчет'],
            'address_comment': None,
            'client_comment': 'коммент клиенту 2',
        },
        'commission': [
            {
                'value': 1.0,
                'acquiring': 1.0,
                'fixed': None,
                'type': 'delivery',
            },
        ],
    },
}


async def test_places_info_200_has_plus(
        taxi_eats_restapp_places,
        mock_eats_core_full_info,
        mock_eats_core_billing_info,
        mock_eats_plus_places_has_plus,
        mock_eats_plus_first_date,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/info?place_id={}'.format(PLACE_ID),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': str(PLACE_ID),
            'X-YaEda-Partner-Permissions': (
                'permission.restaurant.functionality'
            ),
        },
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_200_RESPONSE


async def test_places_info_200_no_plus(
        taxi_eats_restapp_places,
        mock_eats_core_full_info,
        mock_eats_core_billing_info,
        mock_eats_plus_places_no_plus,
        mock_eats_plus_first_date,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/info?place_id={}'.format(PLACE_ID),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': str(PLACE_ID),
            'X-YaEda-Partner-Permissions': (
                'permission.restaurant.functionality'
            ),
        },
    )
    expected_response = EXPECTED_200_RESPONSE
    expected_response['payload']['has_plus'] = False
    expected_response['payload']['place_part'] = 12.3

    assert response.status_code == 200
    assert response.json() == expected_response


async def test_places_info_authorizer_403(taxi_eats_restapp_places):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/info?place_id={}'.format(PLACE_ID),
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Error: no access to the place or no permissions',
    }


async def test_places_info_core_info_400(
        taxi_eats_restapp_places, mock_eats_core_full_info_400,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/info?place_id={}'.format(PLACE_ID),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': str(PLACE_ID),
            'X-YaEda-Partner-Permissions': (
                'permission.restaurant.functionality'
            ),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: no place information',
    }


async def test_places_info_core_billing_info_400(
        taxi_eats_restapp_places,
        mock_eats_core_full_info,
        mock_eats_core_billing_info_400,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/info?place_id={}'.format(PLACE_ID),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': str(PLACE_ID),
            'X-YaEda-Partner-Permissions': (
                'permission.restaurant.functionality'
            ),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: no place billing information',
    }


async def test_places_info_plus_400(
        taxi_eats_restapp_places,
        mock_eats_core_full_info,
        mock_eats_core_billing_info,
        mock_eats_plus_places_plus_400,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/info?place_id={}'.format(PLACE_ID),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': str(PLACE_ID),
            'X-YaEda-Partner-Permissions': (
                'permission.restaurant.functionality'
            ),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: no plus information',
    }


async def test_places_info_plus_activation_400(
        taxi_eats_restapp_places,
        mock_eats_core_full_info,
        mock_eats_core_billing_info,
        mock_eats_plus_places_has_plus,
        mock_eats_plus_first_date_400,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/info?place_id={}'.format(PLACE_ID),
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': str(PLACE_ID),
            'X-YaEda-Partner-Permissions': (
                'permission.restaurant.functionality'
            ),
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Error: no plus activation information',
    }
