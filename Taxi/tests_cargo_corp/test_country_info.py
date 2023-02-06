import pytest

from tests_cargo_corp import utils

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
    'managing_clients': {'threshold': 0},
    'links': {
        'offer': 'link_offer',
        'documentation': 'link_documentation',
        'support_topics': 'link_support_topics',
        'contact_email': 'link_contact_email',
        'contact_phone': 'link_contact_phone',
        'legal': {
            'card': 'legal_card',
            'offer': 'legal_offer',
            'paper': 'legal_paper',
        },
    },
    'legal_entity_details_list': [
        {'label': 'address', 'text': '121099, Moscow'},
        {'label': 'name', 'text': 'Yandex.Delivery LLC'},
        {'label': 'taxpayer_id', 'text': '7716760301'},
    ],
    'tanker_keys': {'tariffs_disclaimer': 'disclaimer.tanker.key.rus'},
    'extra': {'name': 'extra_shown'},
}

EXPECTED_JSON_BLR = {
    'id': {'alpha3': 'blr', 'geoid': 149},
    'names': {'ru': 'Беларусь'},
    'registration': {
        'is_phoenix_available': False,
        'methods': {
            'card_enabled': False,
            'paper_postpaid_enabled': False,
            'paper_prepaid_enabled': False,
            'offer_enabled': False,
        },
    },
    'phones': {
        'national_access_code': '80',
        'phone_code': '375',
        'phone_max_length': 12,
        'phone_min_length': 12,
    },
    'currency': {'code': 'BYN', 'localized_sign': 'BYN'},
    'permits': {
        'access_to_balance_enabled': False,
        'payment_upon_receipt_enabled': False,
        'section_closing_documents_enabled': False,
        'sms_confirmation_enabled': False,
    },
    'languages': {
        'default_language': {'code': 'ru', 'right_left': False},
        'web_ui_languages': [],
    },
    'managing_clients': {},
    'links': {'legal': {}},
    'legal_entity_details_list': [],
    'tanker_keys': {},
}

EXPECTED_JSON_BR_UNKNOWN = {
    'id': {'alpha3': 'br_unknown'},
    'names': {},
    'registration': {
        'is_phoenix_available': False,
        'methods': {
            'card_enabled': False,
            'paper_postpaid_enabled': False,
            'paper_prepaid_enabled': False,
            'offer_enabled': False,
        },
    },
    'phones': {},
    'currency': {'localized_sign': ''},
    'permits': {
        'access_to_balance_enabled': False,
        'payment_upon_receipt_enabled': False,
        'section_closing_documents_enabled': False,
        'sms_confirmation_enabled': False,
    },
    'languages': {
        'default_language': {'code': 'en', 'right_left': False},
        'web_ui_languages': [],
    },
    'managing_clients': {},
    'links': {'legal': {}},
    'legal_entity_details_list': [],
    'tanker_keys': {},
}

EXPECTED_JSON_UNKNOWN = {
    'id': {},
    'names': {},
    'registration': {
        'is_phoenix_available': False,
        'methods': {
            'card_enabled': False,
            'paper_postpaid_enabled': False,
            'paper_prepaid_enabled': False,
            'offer_enabled': False,
        },
    },
    'phones': {},
    'currency': {'localized_sign': ''},
    'permits': {
        'access_to_balance_enabled': False,
        'payment_upon_receipt_enabled': False,
        'section_closing_documents_enabled': False,
        'sms_confirmation_enabled': False,
    },
    'languages': {
        'default_language': {'code': 'en', 'right_left': False},
        'web_ui_languages': [],
    },
    'managing_clients': {},
    'links': {'legal': {}},
    'legal_entity_details_list': [],
    'tanker_keys': {},
}

CARGO_CORP_COUNTRY_SPECIFICS = {
    'rus': {
        'names': {'ru': 'Россия', 'en': 'Russia'},
        'registration': {
            'is_phoenix_available': True,
            'methods': {'card_enabled': True, 'offer_enabled': True},
        },
        'phones': {
            'phone_mask': '([000]) [000]-[00]-[00]',
            'phone_code': '7',
            'national_access_code': '8',
            'phone_min_length': 11,
            'phone_max_length': 11,
        },
        'currency': {
            'code': 'RUB',
            'sign': '₽',
            'localized_sign': 'currency_sign.rub',
        },
        'permits': {
            'section_closing_documents_enabled': True,
            'access_to_balance_enabled': True,
            'sms_confirmation_enabled': True,
        },
        'languages': {
            'default_language': {'code': 'ru'},
            'web_ui_languages': [
                {'code': 'ru'},
                {'code': 'en', 'right_left': True},
            ],
        },
        'managing_clients': {'threshold': 0},
        'links': {
            'offer': 'link_offer',
            'documentation': 'link_documentation',
            'support_topics': 'link_support_topics',
            'contact_email': 'link_contact_email',
            'contact_phone': 'link_contact_phone',
            'legal': {
                'card': 'legal_card',
                'offer': 'legal_offer',
                'paper': 'legal_paper',
            },
        },
        'legal_entity_details_list': [
            {'label': 'address', 'text': '121099, Moscow'},
            {'label': 'name', 'text': 'Yandex.Delivery LLC'},
            {'label': 'taxpayer_id', 'text': '7716760301'},
        ],
        'tanker_keys': {'tariffs_disclaimer': 'disclaimer.tanker.key.rus'},
        'extra': {
            'shown': {'name': 'extra_shown'},
            'hidden': {'name': 'extra_hidden'},
        },
    },
}


@pytest.mark.config(CARGO_CORP_COUNTRY_SPECIFICS=CARGO_CORP_COUNTRY_SPECIFICS)
@pytest.mark.parametrize(
    ('country_alpha3', 'corp_client_id', 'expected_response_json'),
    (
        pytest.param(
            'rus', None, EXPECTED_JSON_RUS, id='country_alpha3 = rus',
        ),
        pytest.param(
            'blr', None, EXPECTED_JSON_BLR, id='country_alpha3 = blr',
        ),
        pytest.param(
            'br_unknown',
            None,
            EXPECTED_JSON_BR_UNKNOWN,
            id='country_alpha3 = br_unknown',
        ),
        pytest.param(
            None, None, EXPECTED_JSON_UNKNOWN, id='country_alpha3 = None',
        ),
        pytest.param(
            None,
            utils.CORP_CLIENT_ID,
            EXPECTED_JSON_RUS,
            id='corp_client_id = utils.CORP_CLIENT_ID',
        ),
    ),
)
async def test_country_info(
        taxi_cargo_corp,
        country_alpha3,
        corp_client_id,
        expected_response_json,
):
    headers = {'Accept-Language': 'ru'}
    if corp_client_id is not None:
        headers['X-B2B-Client-Id'] = corp_client_id

    request_json = {}
    if country_alpha3 is not None:
        request_json['country_alpha3'] = country_alpha3

    response = await taxi_cargo_corp.post(
        '/v1/country/info', json=request_json, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == expected_response_json
