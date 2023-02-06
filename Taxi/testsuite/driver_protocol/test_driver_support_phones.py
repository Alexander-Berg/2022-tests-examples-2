# encoding=utf-8
import pytest


DEFAULT_CALLBACK_TYPES = {
    'call': {'priority': 1, 'tags': ['callback_premium', 'PREMIUM']},
    'recall': {
        'priority': 2,
        'tags': ['callback_blogger'],
        'chat_preferred_tags': ['bad_driver'],
    },
}

DEFAULT_SUPPORT_PHONES = {
    'ru': {
        'default_callback': ['test'],
        'cities': {
            'Москва': {
                'phone': '+74732029291',
                'formatted_phone': '+7 (473) 202 92 91',
            },
            'moscow': {
                'phone': '+70001112233',
                'formatted_phone': '+7 (000) 111 22 33',
            },
            'Казань': {
                'phone': '+79991112233',
                'formatted_phone': '+7 (999) 111 22 33',
            },
        },
    },
}


@pytest.mark.translations(geoareas={'moscow': {'ru': 'Москва'}})
@pytest.mark.config(
    DRIVER_SUPPORT_PHONES=DEFAULT_SUPPORT_PHONES,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    EXTRA_EXAMS_INFO={
        'business': {
            'description': 'Допуск к Бизнес тарифу',
            'permission': ['kids'],
            'requires': [],
        },
    },
    DRIVER_CALLBACK_TYPES=DEFAULT_CALLBACK_TYPES,
)
@pytest.mark.parametrize(
    'session,phone,driver_id,license,callback,tags,chat_preferred',
    [
        (
            'session_1',
            '+79150000001',
            '2eaf04fe6dec4330a6f29a6a7701c451',
            'driver_license_1',
            ['recall', 'call'],
            ['callback_premium', 'callback_blogger'],
            False,
        ),
        (
            'session_1',
            '+79150000001',
            '2eaf04fe6dec4330a6f29a6a7701c451',
            'driver_license_1',
            ['recall', 'call'],
            ['callback_premium', 'PREMIUM', 'callback_blogger'],
            False,
        ),
        (
            'session_2',
            '+79150000001',
            '2eaf04fe6dec4330a6f29a6a7701c451',
            'driver_license_1',
            ['call'],
            ['callback_premium'],
            False,
        ),
        (
            'session_3',
            '+79150000003',
            '2eaf04fe6dec4330a6f29a6a7701c453',
            'driver_license_3',
            ['test'],
            [],
            False,
        ),
        (
            'session_4',
            '+79150000004',
            '2eaf04fe6dec4330a6f29a6a7701c454',
            'driver_license_4',
            ['recall'],
            ['callback_blogger', 'bad_driver'],
            True,
        ),
    ],
)
def test_support_phones(
        taxi_driver_protocol,
        mockserver,
        session,
        phone,
        driver_id,
        license,
        callback,
        tags,
        chat_preferred,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741', session, driver_id,
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def driver_profiles(request):
        assert request.json == {
            'query': {
                'park': {
                    'driver_profile': {'id': [driver_id]},
                    'id': '16de978d526e40c0bf91e847245af741',
                },
            },
            'fields': {
                'driver_profile': ['license', 'driver_license_pd_id'],
                'park': ['city'],
            },
            'removed_drivers_mode': 'as_normal_driver',
        }
        return {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': driver_id,
                        'license': {'normalized_number': license},
                        'driver_license_pd_id': license,
                        'phones': [phone],
                    },
                },
            ],
            'parks': [{'city': 'Москва'}],
        }

    @mockserver.json_handler('/tags/v2/match_single')
    def match_tags(request):
        return {'tags': tags}

    @mockserver.json_handler('/tags/v1/upload')
    def upload_tags(request):
        return {'status': 'ok'}

    response = taxi_driver_protocol.post(
        '/driver/support/phones',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': session,
            'lon': '37.590533',
            'lat': '55.733863',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_response = {
        'callback': callback,
        'support_phones': [
            {
                'city': 'Москва',
                'phone': '+74732029291',
                'formatted_phone': '+7 (473) 202 92 91',
            },
        ],
    }
    if chat_preferred:
        expected_response['chat_preferred'] = True

    assert response_json == expected_response


@pytest.mark.translations(geoareas={'moscow': {'ru': 'Москва'}})
@pytest.mark.config(
    DRIVER_SUPPORT_PHONES=DEFAULT_SUPPORT_PHONES,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    EXTRA_EXAMS_INFO={
        'business': {
            'description': 'Допуск к Бизнес тарифу',
            'permission': ['kids'],
            'requires': [],
        },
    },
    DRIVER_CALLBACK_TYPES=DEFAULT_CALLBACK_TYPES,
)
@pytest.mark.parametrize(
    'session,phone,driver_id,license,callback,'
    'park_tags,udid_tags,dbid_uuid_tags',
    [
        (
            'session_1',
            '+79150000001',
            '2eaf04fe6dec4330a6f29a6a7701c451',
            'driver_license_1',
            ['recall', 'call'],
            ['callback_premium'],
            ['callback_blogger', 'PREMIUM'],
            ['bad_driver'],  # chat_preferred == True
        ),
    ],
)
def test_dbid_uuid_tags(
        taxi_driver_protocol,
        mockserver,
        session,
        phone,
        driver_id,
        license,
        callback,
        park_tags,
        udid_tags,
        dbid_uuid_tags,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741', session, driver_id,
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def driver_profiles(request):
        assert request.json == {
            'query': {
                'park': {
                    'driver_profile': {'id': [driver_id]},
                    'id': '16de978d526e40c0bf91e847245af741',
                },
            },
            'fields': {
                'driver_profile': ['license', 'driver_license_pd_id'],
                'park': ['city'],
            },
            'removed_drivers_mode': 'as_normal_driver',
        }
        return {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': driver_id,
                        'license': {'normalized_number': license},
                        'driver_license_pd_id': license,
                        'phones': [phone],
                    },
                },
            ],
            'parks': [{'city': 'Москва'}],
        }

    @mockserver.json_handler('/tags/v2/match_single')
    def match_tags(request):
        tags = []
        for record in request.json['match']:
            if record['type'] == 'udid':
                tags.extend(udid_tags)
            elif record['type'] == 'park':
                tags.extend(park_tags)
            elif record['type'] == 'dbid_uuid':
                tags.extend(dbid_uuid_tags)
        return {'tags': tags}

    @mockserver.json_handler('/tags/v1/upload')
    def upload_tags(request):
        return {'status': 'ok'}

    response = taxi_driver_protocol.post(
        '/driver/support/phones',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': session,
            'lon': '37.590533',
            'lat': '55.733863',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_response = {
        'chat_preferred': True,
        'callback': callback,
        'support_phones': [
            {
                'city': 'Москва',
                'phone': '+74732029291',
                'formatted_phone': '+7 (473) 202 92 91',
            },
        ],
    }
    assert response_json == expected_response


@pytest.mark.translations(geoareas={'moscow': {'ru': 'Москва'}})
@pytest.mark.config(
    DRIVER_SUPPORT_PHONES=DEFAULT_SUPPORT_PHONES,
    DRIVER_CALLBACK_TYPES=DEFAULT_CALLBACK_TYPES,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
)
@pytest.mark.parametrize(
    'check_recall, loyalty_callback, callback',
    [
        (False, {'recall_type': 'recall'}, ['test']),
        (True, {}, ['test']),
        (True, {'recall_type': 'recall'}, ['recall']),
    ],
)
def test_loyalty_rewards(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        config,
        check_recall,
        loyalty_callback,
        callback,
):
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741',
        'session',
        '2eaf04fe6dec4330a6f29a6a7701c451',
    )

    config.set_values(dict(LOYALTY_CHECK_RECALL=check_recall))

    @mockserver.json_handler('/parks/driver-profiles/list')
    def driver_profiles(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': '2eaf04fe6dec4330a6f29a6a7701c451',
                        'license': {'normalized_number': 'driver_license_1'},
                        'driver_license_pd_id': 'driver_license_1',
                        'phones': ['+79150000001'],
                    },
                },
            ],
            'parks': [{'city': 'Москва'}],
        }

    @mockserver.json_handler('/tags/v2/match_single')
    def match_tags(request):
        return {'tags': []}

    @mockserver.json_handler('/tags/v1/upload')
    def upload_tags(request):
        return {'status': 'ok'}

    @mockserver.json_handler('/loyalty/service/loyalty/v1/rewards')
    def loyalty_rewards(request):
        assert request.json == {
            'data': {
                'zone_name': 'moscow',
                'park_id': '16de978d526e40c0bf91e847245af741',
                'driver_profile_id': '2eaf04fe6dec4330a6f29a6a7701c451',
                'unique_driver_id': '543eac8978f3c2a8d7983621',
            },
            'driver_rewards': ['recall'],
        }
        return {'matched_driver_rewards': {'recall': loyalty_callback}}

    response = taxi_driver_protocol.post(
        '/driver/support/phones',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': 'session',
            'lon': '37.590533',
            'lat': '55.733863',
        },
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'callback': callback,
        'support_phones': [
            {
                'city': 'Москва',
                'phone': '+74732029291',
                'formatted_phone': '+7 (473) 202 92 91',
            },
        ],
    }


@pytest.mark.config(DRIVER_SUPPORT_PHONES={})
def test_support_phones_block_for_country(
        taxi_driver_protocol, driver_authorizer_service, mockserver,
):
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741',
        'driver_session_1',
        '2eaf04fe6dec4330a6f29a6a7701c451',
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def driver_profiles(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': '2eaf04fe6dec4330a6f29a6a7701c451',
                        'license': {'normalized_number': 'driver_license_1'},
                        'driver_license_pd_id': 'driver_license_1',
                        'phones': ['+79150000001'],
                    },
                },
            ],
            'parks': [{'city': 'Москва'}],
        }

    @mockserver.json_handler('/tags/v2/match_single')
    def match_tags(request):
        return {'tags': []}

    @mockserver.json_handler('/tags/v1/upload')
    def upload_tags(request):
        return {'status': 'ok'}

    response = taxi_driver_protocol.post(
        '/driver/support/phones',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': 'driver_session_1',
            'lon': '37.590533',
            'lat': '55.733863',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {'callback': [], 'support_phones': []}


# cargo
@pytest.mark.translations(geoareas={'moscow': {'ru': 'Москва'}})
@pytest.mark.config(
    DRIVER_SUPPORT_PHONES=DEFAULT_SUPPORT_PHONES,
    CARGO_SUPPORT_PHONES={
        'rus': {
            'default_callback': ['test'],
            'cities': {
                'moscow': {
                    'phone': '+79123456789',
                    'formatted_phone': '+7 (912) 345 67 89',
                },
            },
        },
    },
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    EXTRA_EXAMS_INFO={
        'business': {
            'description': 'Допуск к Бизнес тарифу',
            'permission': ['kids'],
            'requires': [],
        },
    },
    DRIVER_CALLBACK_TYPES=DEFAULT_CALLBACK_TYPES,
)
@pytest.mark.experiments3(
    name='driver_protocol_cargo_support_phones',
    consumers=['driver_protocol/cargo_support_phones'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'use_cargo_support_phones': True},
    is_config=True,
)
@pytest.mark.parametrize(
    'callback',
    (
        pytest.param(
            ['recall'],
            id='Before 9:00 Msk',
            marks=pytest.mark.now('2020-04-15T03:00:00+0000'),
        ),
        pytest.param(
            ['recall', 'call'],
            id='Working ours',
            marks=pytest.mark.now('2020-04-15T12:00:00+0000'),
        ),
        pytest.param(
            ['recall'],
            id='After 21:00 Msk',
            marks=pytest.mark.now('2020-04-15T20:00:00+0000'),
        ),
    ),
)
def test_cargo_support_phones(
        driver_authorizer_service,
        taxi_driver_protocol,
        mockserver,
        callback,
        session='session_1',
        phone='+79150000004',
        driver_id='2eaf04fe6dec4330a6f29a6a7701c454',
        license='driver_license_1',
        tags=['callback_premium', 'callback_blogger'],
        chat_preferred=False,
):
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741', session, driver_id,
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def driver_profiles(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': driver_id,
                        'license': {'normalized_number': license},
                        'driver_license_pd_id': license,
                        'phones': [phone],
                    },
                },
            ],
            'parks': [{'city': 'Москва'}],
        }

    @mockserver.json_handler('/tags/v2/match_single')
    def match_tags(request):
        return {'tags': tags}

    @mockserver.json_handler('/tags/v1/upload')
    def upload_tags(request):
        return {'status': 'ok'}

    response = taxi_driver_protocol.post(
        '/driver/support/phones',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': session,
            'lon': '37.590533',
            'lat': '55.733863',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_response = {
        'callback': callback,
        'support_phones': [
            {
                'city': 'Москва',
                'phone': '+79123456789',
                'formatted_phone': '+7 (912) 345 67 89',
            },
        ],
    }
    if chat_preferred:
        expected_response['chat_preferred'] = True

    assert response_json == expected_response
