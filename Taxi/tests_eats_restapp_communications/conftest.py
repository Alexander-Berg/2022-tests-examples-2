import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_restapp_communications_plugins import *  # noqa: F403 F401


@pytest.fixture(name='mock_send_event_200')
def mock_send_event_200(mockserver, request):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_send_event(request):
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    return _mock_send_event


@pytest.fixture(name='mock_get_partners_200')
def mock_get_partners_200(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_eats_partners(request):
        partner_id = int(request.query.get('partner_id'))
        return mockserver.make_response(
            status=200,
            json={
                'payload': {
                    'email': f'user-{partner_id}@mail.ru',
                    'name': 'user_name',
                    'country_code': '',
                    'id': partner_id,
                    'is_blocked': False,
                    'places': [1],
                    'is_fast_food': False,
                    'roles': [],
                    'partner_id': '1a',
                    'timezone': '',
                },
            },
        )

    return _mock_eats_partners


@pytest.fixture(name='mock_get_partnerish_200')
def mock_get_partnerish_200(mockserver, request):
    @mockserver.json_handler(
        '/eats-partners/4.0/restapp-front/partners/v1/login/partnerish/info',
    )
    def _mock_eats_partnerish(request):
        return mockserver.make_response(
            status=200,
            json={
                'email': 'user@mail.ru',
                'name': 'user_name',
                'uuid': '1a',
                'rest_name': 'name',
                'city': 'c',
                'address': 'a',
                'phone_number': '1',
                'consent_to_data_processing': True,
                'is_accepted': True,
            },
        )

    return _mock_eats_partnerish


@pytest.fixture(name='mock_search_partners')
def mock_search_partners(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/search')
    def _mock_search_partners(request):
        return mockserver.make_response(
            status=200,
            json={
                'payload': [
                    {
                        'email': 'user@mail.ru',
                        'name': 'user_name',
                        'country_code': '',
                        'id': 1,
                        'is_blocked': False,
                        'places': [1, 2],
                        'is_fast_food': False,
                        'roles': [],
                        'partner_id': '1a',
                        'timezone': '',
                    },
                ],
                'meta': {'can_fetch_next': True, 'cursor': 0},
            },
        )

    return _mock_search_partners


@pytest.fixture(name='mock_search_all_partners')
def mock_search_all_partners(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/search')
    def _mock_search_partners(request):
        if request.args.get('cursor') == '2':
            return mockserver.make_response(
                status=200,
                json={
                    'payload': [
                        {
                            'email': 'user2@mail.ru',
                            'name': 'user_name2',
                            'country_code': 'ru',
                            'id': 2,
                            'is_blocked': False,
                            'places': [1, 2, 4],
                            'is_fast_food': False,
                            'roles': [],
                            'partner_id': '1a',
                            'timezone': '',
                        },
                    ],
                    'meta': {'can_fetch_next': True, 'cursor': 3},
                },
            )
        if request.query.get('cursor') == '3':
            return mockserver.make_response(
                status=200,
                json={
                    'payload': [
                        {
                            'email': 'user3@mail.ru',
                            'name': 'user_name3',
                            'country_code': 'ru',
                            'id': 3,
                            'is_blocked': False,
                            'places': [1, 2, 4],
                            'is_fast_food': False,
                            'roles': [],
                            'partner_id': '1a',
                            'timezone': '',
                        },
                    ],
                    'meta': {'can_fetch_next': False, 'cursor': 0},
                },
            )
        return mockserver.make_response(
            status=200,
            json={
                'payload': [
                    {
                        'email': 'user1@mail.ru',
                        'name': 'user_name1',
                        'country_code': 'ru',
                        'id': 1,
                        'is_blocked': False,
                        'places': [1, 2, 3],
                        'is_fast_food': False,
                        'roles': [],
                        'partner_id': '1a',
                        'timezone': '',
                    },
                ],
                'meta': {'can_fetch_next': True, 'cursor': 2},
            },
        )

    return _mock_search_partners


@pytest.fixture(name='mock_core_places')
def mock_core_places(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def _mock_core_places(request):
        payload = []
        places = {
            1: {
                'id': 1,
                'name': 'place1',
                'address': {
                    'country': 'country',
                    'city': 'city',
                    'street': 'street',
                    'building': 'building',
                    'full': 'address1',
                },
                'available': True,
                'currency': {
                    'code': 'rub',
                    'sign': 'sign',
                    'decimal_places': 1,
                },
                'show_shipping_time': True,
                'integration_type': 'native',
                'slug': '',
                'country_code': 'ru',
                'emails': [
                    {'email_type': 'my_email_type', 'email': 'common_email'},
                    {'email_type': 'other_email_type', 'email': 'other_email'},
                ],
            },
            2: {
                'id': 2,
                'name': 'place2',
                'address': {
                    'country': 'country',
                    'city': 'city',
                    'street': 'street',
                    'building': 'building',
                    'full': 'address2',
                },
                'available': True,
                'currency': {
                    'code': 'rub',
                    'sign': 'sign',
                    'decimal_places': 1,
                },
                'show_shipping_time': True,
                'integration_type': 'native',
                'slug': '',
                'country_code': 'ru',
                'emails': [{'email_type': 'my_email_type', 'email': 'email2'}],
            },
            3: {
                'id': 3,
                'name': 'place3',
                'address': {
                    'country': 'country',
                    'city': 'city',
                    'street': 'street',
                    'building': 'building',
                    'full': 'address3',
                },
                'available': True,
                'currency': {
                    'code': 'rub',
                    'sign': 'sign',
                    'decimal_places': 1,
                },
                'show_shipping_time': True,
                'integration_type': 'native',
                'slug': '',
                'country_code': 'ru',
                'emails': [
                    {'email_type': 'my_email_type', 'email': 'common_email'},
                ],
            },
            4: {
                'id': 4,
                'name': 'place4',
                'address': {
                    'country': 'country',
                    'city': 'city',
                    'street': 'street',
                    'building': 'building',
                    'full': 'address4',
                },
                'available': True,
                'currency': {
                    'code': 'rub',
                    'sign': 'sign',
                    'decimal_places': 1,
                },
                'show_shipping_time': True,
                'integration_type': 'native',
                'slug': '',
                'country_code': 'ru',
                'emails': [
                    {'email_type': 'other_email_type', 'email': 'other_email'},
                ],
            },
        }
        for place_id in request.json['place_ids']:
            if place_id <= 4:
                payload += [places[place_id]]
        return mockserver.make_response(status=200, json={'payload': payload})

    return _mock_core_places


@pytest.fixture
def mock_authorizer(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_place_access_list(request):
        return mockserver.make_response(
            status=200, json={'is_success': True, 'place_ids': [1]},
        )


@pytest.fixture
def mock_authorizer_allowed(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def mock_authorizer_forbidden(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Forbidden',
                'place_ids': request.json['place_ids'],
            },
        )


@pytest.fixture
def mock_authorizer_500(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_place_access_list(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_authorizer_400(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400,
            json={'code': '400', 'message': 'Пользователь не найден'},
        )

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_place_access_list(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Error'},
        )


@pytest.fixture
def mock_feeds_remove_404(mockserver, request):
    @mockserver.json_handler('/feeds/v1/remove')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )


@pytest.fixture
def mock_feeds_remove_200(mockserver, request):
    @mockserver.json_handler('/feeds/v1/remove')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200,
            json={'statuses': {'cc609ff0e8954f7695520af4a38c79a1': 200}},
        )


@pytest.fixture
def mock_feeds_log_status(mockserver, request):
    @mockserver.json_handler('/feeds/v1/log_status')
    def _mock_sessions(req):
        if req.json['feed_id'] == '7429ad7d21994f298f3685e8f5b50770':
            return mockserver.make_response(
                status=200,
                json={'statuses': {'7429ad7d21994f298f3685e8f5b50770': 200}},
            )

        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )


@pytest.fixture
def mock_eats_feeds_200(mockserver, request):
    @mockserver.json_handler('/feeds/v1/fetch')
    def _mock_sessions(req):
        service = req.json['service']
        if service == 'eats-restaurants-news':
            return mockserver.make_response(
                status=304, json={'code': '', 'message': ''},
            )
        if service == 'eats-restaurants-notification':
            return mockserver.make_response(
                status=500, json={'code': '', 'message': ''},
            )

        data = {
            'polling_delay': 300,
            'etag': 'etag1',
            'has_more': False,
            'feed': [
                {
                    'feed_id': '4ec6a5d00d634f8c9d5605b0fdc2c576',
                    'created': '2020-10-01T12:42:33.689786+0000',
                    'request_id': 'request_id',
                    'service': 'eats-restaurants-survey',
                    'last_status': {
                        'status': 'published',
                        'created': '2020-10-01T12:42:33.689786+0000',
                    },
                    'payload': {'preview': {'title': 'Заголовок'}},
                },
            ],
        }

        return mockserver.make_response(status=200, json=data)


@pytest.fixture
def mock_eats_feeds_200_priority(mockserver, request):
    @mockserver.json_handler('/feeds/v1/fetch')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200,
            json={
                'polling_delay': 300,
                'etag': 'etag1',
                'has_more': False,
                'feed': [
                    {
                        'feed_id': '1',
                        'created': '2020-10-26T19:40:00.689786+0000',
                        'request_id': 'request_id',
                        'service': 'eats-restaurants-news',
                        'last_status': {
                            'status': 'published',
                            'created': '2020-10-26T19:40:00.689786+0000',
                        },
                        'payload': {},
                    },
                    {
                        'feed_id': '2',
                        'created': '2020-10-26T19:41:00.689786+0000',
                        'request_id': 'request_id',
                        'service': 'eats-restaurants-news',
                        'last_status': {
                            'status': 'published',
                            'created': '2020-10-26T19:41:00.689786+0000',
                        },
                        'payload': {
                            'info': {'priority': 5, 'important': False},
                        },
                    },
                    {
                        'feed_id': '3',
                        'created': '2020-10-26T19:42:00.689786+0000',
                        'request_id': 'request_id',
                        'service': 'eats-restaurants-news',
                        'last_status': {
                            'status': 'published',
                            'created': '2020-10-26T19:42:00.689786+0000',
                        },
                        'payload': {
                            'info': {'priority': 2, 'important': True},
                        },
                    },
                    {
                        'feed_id': '4',
                        'created': '2020-10-26T19:43:00.689786+0000',
                        'request_id': 'request_id',
                        'service': 'eats-restaurants-news',
                        'last_status': {
                            'status': 'published',
                            'created': '2020-10-26T19:43:00.689786+0000',
                        },
                        'payload': {
                            'info': {'priority': 2, 'important': False},
                        },
                    },
                    {
                        'feed_id': '5',
                        'created': '2020-10-26T19:44:00.689786+0000',
                        'request_id': 'request_id',
                        'service': 'eats-restaurants-news',
                        'last_status': {
                            'status': 'published',
                            'created': '2020-10-26T19:44:00.689786+0000',
                        },
                        'payload': {
                            'info': {'priority': 5, 'important': False},
                        },
                    },
                ],
            },
        )


@pytest.fixture(name='mock_subscriptions')
def mock_subscriptions(mockserver, request):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    def _mock_subscriptions(request):
        req = request.json
        assert req['feature'] == 'boss_bot'
        resp = {
            'feature': req['feature'],
            'places': {
                'with_enabled_feature': req['place_ids'],
                'with_disabled_feature': [],
            },
        }
        return mockserver.make_response(status=200, json=resp)

    return _mock_subscriptions


@pytest.fixture(name='mock_personal_telegram_retrieve')
def mock_personal_telegram_retrieve(mockserver, request):
    @mockserver.json_handler('/personal/v1/telegram_logins/bulk_retrieve')
    def _mock_personal_telegram_retrieve(request):
        req = request.json
        resp = {
            'items': [
                {'id': i['id'], 'value': 'resolved_' + i['id']}
                for i in req['items']
            ],
        }
        return mockserver.make_response(status=200, json=resp)

    return _mock_personal_telegram_retrieve


@pytest.fixture(name='mock_catalog_storage')
def mock_catalog_storage(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/'
        + 'eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    async def _mock_catalog_storage(request):
        place_ids = request.json['place_ids']
        return {
            'places': [
                {
                    'id': p,
                    'name': 'place' + str(p),
                    'address': {'city': 'Moscow', 'short': 'address' + str(p)},
                    'type': 'native',
                    'region': {
                        'id': 1,
                        'geobase_ids': [],
                        'time_zone': 'Europe/Moscow',
                    },
                    'revision_id': 1,
                    'updated_at': '2022-04-22T11:44:47.385057+00:00',
                }
                for p in place_ids
            ],
            'not_found_place_ids': [],
        }

    return _mock_catalog_storage
