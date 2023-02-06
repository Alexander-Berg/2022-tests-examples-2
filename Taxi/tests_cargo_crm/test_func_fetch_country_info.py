COUNTRY_ALPHA3 = 'rus'

EXPECTED_JSON_RUS = {
    'id': {'alpha3': 'rus', 'geoid': 225},
    'names': {'ru': 'Россия', 'en': 'Russia'},
    'registration': {
        'is_phoenix_available': True,
        'methods': {
            'card_enabled': True,
            'paper_postpaid_enabled': False,
            'paper_prepaid_enabled': False,
            'offer_enabled': True,
        },
    },
    'phones': {
        'national_access_code': '8',
        'phone_code': '7',
        'phone_mask': '([000]) [000]-[00]-[00]',
        'phone_max_length': 11,
        'phone_min_length': 11,
    },
    'currency': {'code': 'RUB', 'sign': '₽', 'localized_sign': '₽'},
    'permits': {
        'access_to_balance_enabled': True,
        'payment_upon_receipt_enabled': False,
        'section_closing_documents_enabled': True,
        'sms_confirmation_enabled': True,
    },
    'languages': {
        'default_language': {'code': 'ru', 'right_left': False},
        'web_ui_languages': [
            {'code': 'ru', 'right_left': False},
            {'code': 'en', 'right_left': True},
        ],
    },
    'managing_clients': {},
    'links': {'legal': {}},
    'legal_entity_details_list': [],
    'tanker_keys': {},
}


LANGUAGES = {
    'languages': {'default_language': {'code': 'ru', 'right_left': False}},
}


async def test_func_fetch_country_info(taxi_cargo_crm, mockserver):
    @mockserver.json_handler('cargo-corp/v1/country/info')
    def _handler(request):
        assert request.headers['Accept-Language'] == 'ru'
        assert request.json['country_alpha3'] == COUNTRY_ALPHA3
        return mockserver.make_response(status=200, json=EXPECTED_JSON_RUS)

    response = await taxi_cargo_crm.post(
        '/functions/fetch-country-info',
        json={'country_alpha3': COUNTRY_ALPHA3},
    )

    assert response.status_code == 200
    assert response.json() == LANGUAGES
