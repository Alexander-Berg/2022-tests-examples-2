PARTNER_ID = 111
PARTNER_PLACES_STR = '11,12,13,14,15'
PARTNER_PLACES = [11, 12, 13, 14, 15]

HANDLE_URL = '/4.0/restapp-front/places/v1/features-statuses-by-features'


def sorted_response(response):
    for feature in response['features']:
        feature['places'] = sorted(
            feature['places'], key=lambda x: x['place_id'],
        )
    response['features'] = sorted(
        response['features'], key=lambda x: x['slug'],
    )
    return response


async def test_features_statuses_403(taxi_eats_restapp_places):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL,
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': PARTNER_PLACES_STR,
        },
        params={'place_ids': '11,22,13'},
    )

    assert response.status_code == 403


async def test_features_statuses_all_places(
        taxi_eats_restapp_places, mockserver,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/admin/communications/v1/telegram/list',
    )
    def _mock_communications(request):
        assert sorted(request.json['place_ids']) == PARTNER_PLACES
        return mockserver.make_response(
            status=200,
            json={
                'payload': [
                    {'place_id': 11, 'logins': ['a', 'b']},
                    {'place_id': 12, 'logins': []},
                ],
                'meta': {'logins_limit': 3},
            },
        )

    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/place/get-subscriptions',
    )
    def _mock_subscriptions(request):
        assert sorted(request.json['place_ids']) == PARTNER_PLACES
        return mockserver.make_response(
            status=200,
            json={
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': True,
                        'need_alerting_about_finishing_trial': True,
                        'place_id': 11,
                        'tariff_info': {
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'valid_until': '01.02.2020',
                        'valid_until_iso': '2020-02-01T12:00:00+00:00',
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': True,
                        'need_alerting_about_finishing_trial': True,
                        'place_id': 12,
                        'tariff_info': {
                            'features': [
                                'daily_billing',
                                'sorry',
                                'boss_bot',
                                'personal_manager',
                            ],
                            'type': 'business_plus',
                        },
                        'valid_until': '01.02.2020',
                        'valid_until_iso': '2020-02-01T12:00:00+00:00',
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': True,
                        'need_alerting_about_finishing_trial': True,
                        'place_id': 13,
                        'tariff_info': {
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                        'valid_until': '01.02.2020',
                        'valid_until_iso': '2020-02-01T12:00:00+00:00',
                        'next_tariff': 'free',
                        'next_tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': True,
                        'need_alerting_about_finishing_trial': True,
                        'place_id': 14,
                        'tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                        'valid_until': '01.02.2020',
                        'valid_until_iso': '2020-02-01T12:00:00+00:00',
                        'next_tariff': 'business',
                        'next_tariff_info': {
                            'features': ['daily_billing', 'sorry', 'boss_bot'],
                            'type': 'business',
                        },
                    },
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': True,
                        'need_alerting_about_finishing_trial': True,
                        'place_id': 15,
                        'tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                        'valid_until': '01.02.2020',
                        'valid_until_iso': '2020-02-01T12:00:00+00:00',
                    },
                ],
            },
        )

    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/places_plus')
    def _mock_plus(request):
        assert sorted(request.json['place_ids']) == PARTNER_PLACES
        return mockserver.make_response(
            status=200,
            json={
                'places': [
                    {'place_id': 11, 'has_plus': True},
                    {'place_id': 12, 'has_plus': False},
                    {'place_id': 13, 'has_plus': True},
                    {'place_id': 14, 'has_plus': False},
                    {'place_id': 15, 'has_plus': True},
                ],
            },
        )

    response = await taxi_eats_restapp_places.get(
        HANDLE_URL,
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': PARTNER_PLACES_STR,
        },
    )

    assert response.status_code == 200
    assert sorted_response(response.json()) == {
        'features': [
            {
                'slug': 'feedback',
                'places': [
                    {'place_id': 11, 'status': 'turned_on'},
                    {'place_id': 12, 'status': 'turned_on'},
                    {
                        'place_id': 13,
                        'status': 'turning_off',
                        'ends_at': '2020-02-01T12:00:00+00:00',
                    },
                    {
                        'place_id': 14,
                        'status': 'turning_on',
                        'ends_at': '2020-02-01T12:00:00+00:00',
                    },
                    {'place_id': 15, 'status': 'turned_off'},
                ],
            },
            {
                'slug': 'personal-manager',
                'places': [
                    {'place_id': 11, 'status': 'turned_off'},
                    {'place_id': 12, 'status': 'turned_on'},
                    {'place_id': 13, 'status': 'turned_off'},
                    {'place_id': 14, 'status': 'turned_off'},
                    {'place_id': 15, 'status': 'turned_off'},
                ],
            },
            {
                'slug': 'plus',
                'places': [
                    {'place_id': 11, 'status': 'turned_on'},
                    {'place_id': 12, 'status': 'turned_off'},
                    {'place_id': 13, 'status': 'turned_on'},
                    {'place_id': 14, 'status': 'turned_off'},
                    {'place_id': 15, 'status': 'turned_on'},
                ],
            },
            {
                'slug': 'telegram',
                'places': [
                    {'place_id': 11, 'status': 'turned_on'},
                    {'place_id': 12, 'status': 'turned_on_unset'},
                    {
                        'place_id': 13,
                        'status': 'turning_off',
                        'ends_at': '2020-02-01T12:00:00+00:00',
                    },
                    {
                        'place_id': 14,
                        'status': 'turning_on',
                        'ends_at': '2020-02-01T12:00:00+00:00',
                    },
                    {'place_id': 15, 'status': 'turned_off'},
                ],
            },
        ],
    }


async def test_features_statuses_requested_places(
        taxi_eats_restapp_places, mockserver,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/admin/communications/v1/telegram/list',
    )
    def _mock_communications(request):
        assert sorted(request.json['place_ids']) == [13]
        return mockserver.make_response(
            status=200,
            json={
                'payload': [{'place_id': 13, 'logins': []}],
                'meta': {'logins_limit': 3},
            },
        )

    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/place/get-subscriptions',
    )
    def _mock_subscriptions(request):
        assert sorted(request.json['place_ids']) == [13]
        return mockserver.make_response(
            status=200,
            json={
                'subscriptions': [
                    {
                        'activated_at': '28.04.2020',
                        'activated_at_iso': '2020-04-28T12:00:00+00:00',
                        'is_partner_updated': False,
                        'is_trial': True,
                        'need_alerting_about_finishing_trial': True,
                        'place_id': 13,
                        'tariff_info': {
                            'features': ['weekly_billing'],
                            'type': 'free',
                        },
                        'valid_until': '01.02.2020',
                        'valid_until_iso': '2020-02-01T12:00:00+00:00',
                    },
                ],
            },
        )

    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/places_plus')
    def _mock_plus(request):
        assert sorted(request.json['place_ids']) == [13]
        return mockserver.make_response(
            status=200, json={'places': [{'place_id': 13, 'has_plus': False}]},
        )

    response = await taxi_eats_restapp_places.get(
        HANDLE_URL,
        headers={
            'X-YaEda-PartnerId': str(PARTNER_ID),
            'X-YaEda-Partner-Places': PARTNER_PLACES_STR,
        },
        params={'place_ids': '13'},
    )

    assert response.status_code == 200
    assert sorted_response(response.json()) == {
        'features': [
            {
                'slug': 'feedback',
                'places': [{'place_id': 13, 'status': 'turned_off'}],
            },
            {
                'slug': 'personal-manager',
                'places': [{'place_id': 13, 'status': 'turned_off'}],
            },
            {
                'slug': 'plus',
                'places': [{'place_id': 13, 'status': 'turned_off'}],
            },
            {
                'slug': 'telegram',
                'places': [{'place_id': 13, 'status': 'turned_off'}],
            },
        ],
    }
