import pytest

DEFAULT_HEADERS = {
    'X-Yandex-UID': 'uid_1',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
    'User-Agent': 'android',
    'X-Request-Language': 'ru',
}

DEFAULT_INFORMER = {
    'id': 'some_uuid',
    'options': {
        'name': 'test_informer',
        'source': 'tracking',
        'priority': 1,
        'max_shown_count': 3,
        'same_priority_order': 2,
    },
    'payload': {
        'text': 'Some text, like, who cares',
        'picture': 'www.image.com',
        'text_color': '#rrggbb',
        'background_color': '#rrggbb',
        'extra_data': {'additional_text': 'More text to the god of the text'},
        'modal': {
            'text': 'Referral args: 4 8 15 16 23 42',
            'title': 'The Title',
            'picture': 'www.image.com/modal',
            'text_color': '#rrggbb',
            'background_color': '#rrggbb',
            'full_screen': True,
            'buttons': [
                {
                    'action': 'deeplink',
                    'deeplink': 'deeplink://somewhere',
                    'text': 'OK',
                    'text_color': '#rrggbb',
                    'background_color': '#rrggbb',
                },
                {
                    'action': 'deeplink',
                    'deeplink': 'deeplink://somewhere',
                    'text': 'Cancel',
                    'text_color': '#rrggbb',
                    'background_color': '#rrggbb',
                },
            ],
        },
    },
}

DEFAULT_CAMPAIGN = {
    'campaign_label': 'crm_test_label',
    'starts_at': '2020-01-01T09:00:00.000000Z',
    'ends_at': '2023-06-01T09:00:00.000000Z',
    'is_test_publication': False,
}


@pytest.mark.experiments3(filename='exp3_grocery_informers.json')
async def test_informers_by_exp(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    _communications_audience([])
    _user_api()

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions():
        result = load_json('promotions_response_informers.json')
        result['grocery_informers'][0]['options'][
            'experiment'
        ] = 'grocery_informer_exp'
        return result

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/grocery-communications',
        {'optional_kwargs': {}},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['informers']
    assert response.json()['informers'][0] == DEFAULT_INFORMER


@pytest.mark.now('2022-03-01T12:00:00+0000')
async def test_informers_by_campaign(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    _communications_audience([DEFAULT_CAMPAIGN['campaign_label']])
    _user_api()

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions():
        result = load_json('promotions_response_informers.json')
        result['grocery_informers'][0]['campaigns'] = [DEFAULT_CAMPAIGN]
        return result

    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/grocery-communications',
        {'optional_kwargs': {}},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['informers']
    assert response.json()['informers'][0] == DEFAULT_INFORMER


@pytest.mark.parametrize('has_donated', [True, False])
@pytest.mark.experiments3(filename='exp3_helping_hand_informer.json')
async def test_informer_helping_hand(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
        has_donated,
):
    _communications_audience([])
    _user_api()

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions():
        result = load_json('promotions_response_informers.json')
        result['grocery_informers'][0]['options'][
            'experiment'
        ] = 'grocery_informer_exp'
        return result

    optional_kwargs = {
        'country_iso3': 'RUS',
        'persey_subscription_status': 'was_subscribed',
        'persey_user_has_donations': has_donated,
    }
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/grocery-communications',
        {'optional_kwargs': optional_kwargs},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    if has_donated:
        assert response.json()['informers']
        assert response.json()['informers'][0] == DEFAULT_INFORMER
    else:
        assert not response.json()['informers']


@pytest.mark.experiments3(filename='exp3_grocery_informers.json')
async def test_informer_translation(
        taxi_inapp_communications,
        mockserver,
        load_json,
        _communications_audience,
        _user_api,
):
    _communications_audience([])
    _user_api()

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions():
        result = load_json('promotions_response_informers_translation.json')
        result['grocery_informers'][0]['options'][
            'experiment'
        ] = 'grocery_informer_exp'
        return result

    tanker_args = {
        'a': '4',
        'b': '8',
        'c': '15',
        'd': '16',
        'e': '23',
        'f': '42',
    }
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/grocery-communications',
        {'optional_kwargs': {}, 'tanker_args': tanker_args},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['informers']
    assert response.json()['informers'][0] == DEFAULT_INFORMER
