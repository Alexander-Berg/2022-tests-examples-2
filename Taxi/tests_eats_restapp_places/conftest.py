# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name, too-many-lines
import pytest

from eats_restapp_places_plugins import *  # noqa: F403 F401


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
def mock_eats_core(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/service-schedule/update')
    def _mock_sessions(req):
        return mockserver.make_response(status=200, json={'isSuccess': True})


@pytest.fixture
def mock_eats_core_500(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/service-schedule/update')
    def _mock_sessions(req):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/eats-core/v1/places/info')
    def _mock_places_info(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_eats_core_404(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/service-schedule/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )

    @mockserver.json_handler('/eats-core/v1/places/delivery-zones')
    def _mock_places_delivery_zones(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'error'},
        )

    @mockserver.json_handler('/eats-core/v1/places/42/order-editing-settings')
    def _mock_places_order_editing_settings(request):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )

    @mockserver.json_handler('/eats-core/v1/places/42/disable')
    def _mock_disable(request):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )


@pytest.fixture
def mock_eats_core_400(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def _mock_places_info(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': 400,
                'type': 'error',
                'errors': [],
                'context': '',
            },
        )

    @mockserver.json_handler('/eats-core/v1/places/42/disable')
    def _mock_disable(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': 400,
                'type': 'Error',
                'errors': [{'message': 'error'}],
                'context': '',
            },
        )

    @mockserver.json_handler('/eats-core/v1/places/42/order-editing-settings')
    def _mock_order_editing_settings(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': 400,
                'type': 'Error',
                'errors': [{'message': 'error'}],
                'context': '',
            },
        )

    @mockserver.json_handler('/eats-core/v1/places/delivery-zones')
    def _mock_delivery_zones(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )


@pytest.fixture
def mock_eats_core_update_201(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )


@pytest.fixture
def mock_eats_core_update_201_data(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        assert req.json == {
            'address': {'address': 'Льва Толстого 16', 'city': 'Moscow'},
            'comments': [{'text': 'its good', 'type': 'client'}],
            'emails': [{'address': 'admin@admin.com', 'type': 'main'}],
            'name': 'place-name',
            'paymentMethods': ['cash', 'card'],
            'phones': [{'number': '+78005553535', 'type': 'official'}],
        }

        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )


@pytest.fixture
def mock_eats_core_update_201_bel(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        assert req.json == {
            'name': 'place-name',
            'address': {'city': 'Минск', 'address': 'Максима Богдановича 16'},
            'phones': [{'type': 'official', 'number': '+375291234567'}],
            'emails': [{'type': 'main', 'address': 'admin@admin.com'}],
            'paymentMethods': ['cash', 'card'],
            'comments': [{'type': 'client', 'text': 'its good'}],
        }

        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )


@pytest.fixture
def mock_eats_core_update_any_data(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )


@pytest.fixture
def mock_eats_core_update_data_43(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/43/update')
    def _mock_sessions(req):
        assert req.json == {
            'address': {'address': 'Льва Толстого 16', 'city': 'Moscow'},
            'comments': [{'text': 'its good', 'type': 'client'}],
            'emails': [{'address': 'admin@admin.com', 'type': 'main'}],
            'name': 'place-name',
            'paymentMethods': ['cash', 'card'],
            'phones': [{'number': '+78005553535', 'type': 'official'}],
        }

        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )


@pytest.fixture
def mock_eats_core_update_data_44(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/44/update')
    def _mock_sessions(req):
        assert req.json == {
            'address': {'address': 'Льва Толстого 16', 'city': 'Moscow'},
            'comments': [{'text': 'its good', 'type': 'client'}],
            'emails': [{'address': 'admin@admin.com', 'type': 'main'}],
            'name': 'place-name',
            'paymentMethods': ['cash', 'card'],
            'phones': [{'number': '+78005553535', 'type': 'official'}],
        }

        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )


@pytest.fixture
def mock_eats_core_update_404(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404, json={'errors': ['ресторан не найден']},
        )


@pytest.fixture
def mock_eats_core_update_400(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=400,
            json={
                'errors': [
                    {'name': 'address', 'error': 'адрес не существует'},
                ],
            },
        )


@pytest.fixture
def mock_eats_core_update400invald(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/43/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=400, json={'errors': ['Request format is invalid']},
        )


@pytest.fixture
def mock_eats_service_schedule(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/service-schedule')
    def _mock_sessions_42(req):
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': {
                    'default': [{'day': 1, 'from': 480, 'to': 540}],
                    'redefined': [
                        {'date': '2020-09-24', 'from': 480, 'to': 960},
                    ],
                },
            },
        )

    @mockserver.json_handler('/eats-core/v1/places/43/service-schedule')
    def _mock_sessions_43(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )


@pytest.fixture
def mock_eats_redefined_schedule(mockserver, request):
    @mockserver.json_handler(
        '/eats-core/v1/places/42/schedule-redefined-dates',
    )
    def _mock_sessions_42(req):
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': [{'date': '2020-09-24', 'from': 480, 'to': 960}],
            },
        )

    @mockserver.json_handler(
        '/eats-core/v1/places/43/schedule-redefined-dates',
    )
    def _mock_sessions_43(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )


@pytest.fixture
def mock_eats_redefined_update(mockserver, request):
    @mockserver.json_handler(
        '/eats-core/v1/places/43/schedule-redefined-dates',
    )
    def _mock_sessions_43(req):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    @mockserver.json_handler(
        '/eats-core/v1/places/44/schedule-redefined-dates',
    )
    def _mock_sessions_44(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )


@pytest.fixture
def mock_eats_redefined_update_500(mockserver, request):
    @mockserver.json_handler(
        '/eats-core/v1/places/43/schedule-redefined-dates',
    )
    def _mock_sessions(req):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_eats_redefined_update_404(mockserver, request):
    @mockserver.json_handler(
        '/eats-core/v1/places/43/schedule-redefined-dates',
    )
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )


@pytest.fixture
def mock_eats_get_schedule(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/schedule')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200,
            json={'intervals': [{'day': 1, 'from': 480, 'to': 540}]},
        )


@pytest.fixture
def mock_eats_get_schedule_404(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/schedule')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )


@pytest.fixture
def mock_eats_update_status_200(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200, json={'result': ['Place updating is not in progress']},
        )


@pytest.fixture
def mock_eats_update_status_202(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=202, json={'result': ['Place updating is in progress']},
        )


@pytest.fixture
def mock_eats_update_status_404(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404, json={'errors': ['place not found']},
        )


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_restapp_places'].dict_cursor()

    return create_cursor


@pytest.fixture()
def get_info_by_place(get_cursor):
    def do_get_info_by_place(place_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_restapp_places.place_info '
            'WHERE place_id = %s',
            [place_id],
        )
        return cursor.fetchone()

    return do_get_info_by_place


@pytest.fixture()
def get_count_by_place(get_cursor):
    def do_get_count_by_place(place_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_restapp_places.update_rates_by_place '
            'WHERE place_id = %s',
            [place_id],
        )
        return cursor.fetchone()

    return do_get_count_by_place


@pytest.fixture()
def get_count_by_partner(get_cursor):
    def do_get_count_by_partner(partner_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_restapp_places.update_rates_by_partner '
            'WHERE partner_id = %s',
            [partner_id],
        )
        return cursor.fetchone()

    return do_get_count_by_partner


@pytest.fixture(name='mock_avatars_delete_200')
def _mock_avatars_delete_200(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/delete-eda/(?P<group_id>\w+)/(?P<imagename>\w+)',
        regex=True,
    )
    def _mock_avatars(request, group_id, imagename):
        return mockserver.make_response(status=200)

    return _mock_avatars


@pytest.fixture(name='mock_avatars_delete_202')
def mock_avatars_delete_202(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/delete-eda/(?P<group_id>\w+)/(?P<imagename>\w+)',
        regex=True,
    )
    def _mock_avatars(request, group_id, imagename):
        return mockserver.make_response(status=202)

    return _mock_avatars


@pytest.fixture(name='mock_avatars_delete_404')
def mock_avatars_delete_404(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/delete-eda/(?P<group_id>\w+)/(?P<imagename>\w+)',
        regex=True,
    )
    def _mock_avatars(request, group_id, imagename):
        return mockserver.make_response(status=404)

    return _mock_avatars


@pytest.fixture(name='mock_avatar_mds')
def _mock_avatar_mds(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_authorizer(request, imagename):
        return mockserver.make_response(
            status=200,
            json={
                'imagename': 'test_image_name',
                'group-id': 1234567,
                'meta': {'orig-format': 'jpeg'},
                'sizes': {'orig': {'width': 1600, 'height': 1200, 'path': ''}},
            },
        )


@pytest.fixture
def mock_avatar_mds_400(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_authorizer(request, imagename):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )


@pytest.fixture
def mock_eats_moderation(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _mock_authorizer(request):
        assert request.json == {
            'context': '{"place_id":"42","partner_id":"1","city":"Москва"}',
            'payload': (
                '{"picture":"test_image_name.jpg",'
                '"identity":"1234567/test_image_name",'
                '"photo_url":"http://avatars.mds.yandex.net/get-eda'
                '/1234567/test_image_name/1600x1200",'
                '"current_identity":"fake_identity42"}'
            ),
            'queue': 'restapp_moderation_hero',
            'scope': 'eda',
        }
        return mockserver.make_response(status=200, json={'task_id': '12qwas'})


@pytest.fixture
def mock_eats_moderation_no_info(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task')
    def _mock_authorizer(request):
        assert request.json == {
            'context': '{"place_id":"42","partner_id":"1"}',
            'payload': (
                '{"picture":"test_image_name.jpg",'
                '"identity":"1234567/test_image_name",'
                '"photo_url":"http://avatars.mds.yandex.net/get-eda'
                '/1234567/test_image_name/1600x1200",'
                '"current_identity":"fake_identity42"}'
            ),
            'queue': 'restapp_moderation_hero',
            'scope': 'eda',
        }
        return mockserver.make_response(status=200, json={'task_id': '12qwas'})


@pytest.fixture
def mock_eats_core_full_info(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/full-info')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': {
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
                        'lpr_email': (
                            'yzdanov4@koseleva.com, yzdanov7@koseleva.com'
                        ),
                        'payments': ['Наличный расчет', 'Безналичный расчет'],
                        'address_comment': None,
                        'client_comment': 'коммент клиенту 2',
                    },
                    'billing': {
                        'inn': '9705114405',
                        'kpp': '770501001',
                        'bik': '044525225',
                        'account': '40702810638000093677',
                        'name': 'ООО "ЯНДЕКС.ЕДА"',
                        'address': {
                            'postcode': '115035',
                            'full': (
                                'Москва, ул Садовническая, д 82, стр 2, пом 3'
                            ),
                        },
                        'post_address': {
                            'postcode': '115035',
                            'full': (
                                'Москва, ул Садовническая, д 82, стр 2, пом 3'
                            ),
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
                    'commission': [
                        {
                            'value': 1,
                            'acquiring': 1,
                            'fixed': None,
                            'type': 'delivery',
                        },
                    ],
                },
            },
        )


@pytest.fixture
def mock_eats_core_full_info_400(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/full-info')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': '400',
                'type': 'Error',
                'errors': ['error'],
                'context': '',
            },
        )


@pytest.fixture
def mock_eats_plus_places_plus(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/42/full-info')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400,
            json={
                'isSuccess': False,
                'statusCode': '400',
                'type': 'Error',
                'errors': ['error'],
                'context': '',
            },
        )


@pytest.fixture
def mock_eats_plus_places_has_plus(mockserver, request):
    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/places_plus')
    def _mock_plus(request):
        return mockserver.make_response(
            status=200, json={'places': [{'has_plus': True, 'place_id': 42}]},
        )


@pytest.fixture
def mock_eats_plus_places_no_plus(mockserver, request):
    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/places_plus')
    def _mock_plus(request):
        return mockserver.make_response(
            status=200,
            json={
                'places': [
                    {'has_plus': False, 'place_id': 42, 'place_part': 12.3},
                ],
            },
        )


@pytest.fixture
def mock_eats_plus_places_plus_400(mockserver, request):
    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/places_plus')
    def _mock_plus(request):
        return mockserver.make_response(status=400)


@pytest.fixture
def mock_restapp_authorizer(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def mock_restapp_authorizer_403(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'forbidden',
                'details': {
                    'permissions': ['permission.restaurant.functionality'],
                    'place_ids': [123],
                },
            },
        )


@pytest.fixture
def mock_restapp_authorizer_400(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'bad request'},
        )


@pytest.fixture
def mock_eats_moderation_list(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/tasks/list')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200,
            json={
                'items': [
                    {
                        'task_id': 'task1111',
                        'tag': 'tag2222',
                        'status': 'process',
                        'payload': '{"qqq":"www"}',
                        'actual_payload': 'null',
                        'moderator_context': '{"moderator_id": "Ivanov  "}',
                        'context': (
                            '{"place_id": "1","partner_id": "2",'
                            ' "city": "Saint-Petersburg"}'
                        ),
                        'queue': 'restapp_moderation_hero',
                        'reasons': [],
                    },
                ],
            },
        )


@pytest.fixture
def mock_eats_moderation_list_400(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/tasks/list')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )


@pytest.fixture
def mock_eats_moderation_count(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/tasks/count')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200, json={'counts': [2, 3]})


@pytest.fixture
def mock_eats_moderation_count_400(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/tasks/count')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )


@pytest.fixture
def mock_eats_moderation_remove(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task/remove')
    def _mock_authorizer(request):
        return mockserver.make_response(status=204, json={})


@pytest.fixture
def mock_eats_moderation_remove_400(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task/remove')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )


@pytest.fixture
def mock_eats_moderation_remove_404(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task/remove')
    def _mock_authorizer(request):
        return mockserver.make_response(status=404, json={})


@pytest.fixture
def mock_eats_moderation_get(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task/status')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=200,
            json={
                'items': [
                    {
                        'task_id': 'task1111',
                        'tag': 'tag2222',
                        'status': 'process',
                        'payload': '{"qqq":"www"}',
                        'moderator_context': '{"moderator_id": "Ivanov  "}',
                        'context': (
                            '{"place_id": "1", "partner_id": "2",'
                            ' "city": "Saint-Petersburg"}'
                        ),
                        'queue': 'restapp_moderation_hero',
                        'reasons': [],
                    },
                ],
            },
        )


@pytest.fixture
def mock_eats_moderation_get_400(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task/status')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )


@pytest.fixture
def mock_eats_moderation_get_404(mockserver, request):
    @mockserver.json_handler('eats-moderation/moderation/v1/task/status')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'error'},
        )


@pytest.fixture()
def get_pickup_status_by_place_id(get_cursor):
    def do_get_pickup_status_by_place(place_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_restapp_places.pickup_status '
            'WHERE place_id = %s',
            [place_id],
        )
        return cursor.fetchone()

    return do_get_pickup_status_by_place


@pytest.fixture()
def get_pickup_statuses(get_cursor):
    def do_get_pickup_statuses():
        cursor = get_cursor()
        cursor.execute('SELECT * FROM eats_restapp_places.pickup_status')
        return cursor.fetchall()

    return do_get_pickup_statuses


@pytest.fixture
def mock_eats_core_pickup_enable(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/place-pickup/enable')
    def _mock_sessions(request):
        assert request.json == {'place_ids': [111, 222, 333]}
        return mockserver.make_response(status=204, json={})


@pytest.fixture
def mock_eats_core_pickup_enable_f(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/place-pickup/enable')
    def _mock_sessions(request):
        assert request.json == {'place_ids': [111, 222, 333]}
        return mockserver.make_response(status=400, json={})


@pytest.fixture
def mock_eats_core_pickup_disable(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/place-pickup/disable')
    def _mock_sessions(request):
        assert request.json == {'place_ids': [111, 222, 333]}
        return mockserver.make_response(status=204, json={})


@pytest.fixture
def mock_eats_core_pickup_disable_f(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/place-pickup/disable')
    def _mock_sessions(request):
        assert request.json == {'place_ids': [111, 222, 333]}
        return mockserver.make_response(status=400, json={})


@pytest.fixture
def mock_eats_place_subscriptions(mockserver, request):
    @mockserver.json_handler(
        'eats-place-subscriptions/internal/'
        'eats-place-subscriptions/v1/place/'
        'get-subscriptions',
    )
    def _mock_place_subscriptions(request):
        subscriptions = {
            'subscriptions': [
                {
                    'place_id': 1,
                    'tariff_info': {'type': 'free', 'features': []},
                    'valid_until': '27.07.2022',
                    'valid_until_iso': '2022-07-27T03:00:00+03:00',
                    'activated_at': '01.01.2022',
                    'activated_at_iso': '2022-01-01T00:00:00+00:00',
                    'is_trial': True,
                    'need_alerting_about_finishing_trial': False,
                },
                {
                    'place_id': 2,
                    'tariff_info': {'type': 'business', 'features': []},
                    'valid_until': '26.07.2022',
                    'valid_until_iso': '2022-07-26T03:00:00+03:00',
                    'activated_at': '01.01.2022',
                    'activated_at_iso': '2022-01-01T00:00:00+00:00',
                    'is_trial': False,
                    'need_alerting_about_finishing_trial': True,
                },
                {
                    'place_id': 3,
                    'tariff_info': {'type': 'business_plus', 'features': []},
                    'valid_until': '27.06.2022',
                    'valid_until_iso': '2022-06-27T03:00:00+03:00',
                    'activated_at': '01.01.2022',
                    'activated_at_iso': '2022-01-01T00:00:00+00:00',
                    'is_trial': True,
                    'need_alerting_about_finishing_trial': False,
                },
                {
                    'place_id': 4,
                    'tariff_info': {'type': 'free', 'features': []},
                    'valid_until': '26.06.2022',
                    'valid_until_iso': '2022-06-26T03:00:00+03:00',
                    'activated_at': '01.01.2022',
                    'activated_at_iso': '2022-01-01T00:00:00+00:00',
                    'is_trial': False,
                    'need_alerting_about_finishing_trial': True,
                },
                {
                    'place_id': 5,
                    'tariff_info': {'type': 'business', 'features': []},
                    'valid_until': '27.05.2022',
                    'valid_until_iso': '2022-05-27T03:00:00+03:00',
                    'activated_at': '01.01.2022',
                    'activated_at_iso': '2022-01-01T00:00:00+00:00',
                    'is_trial': True,
                    'need_alerting_about_finishing_trial': False,
                },
                {
                    'place_id': 6,
                    'tariff_info': {'type': 'business_plus', 'features': []},
                    'valid_until': '26.05.2022',
                    'valid_until_iso': '2022-05-26T03:00:00+03:00',
                    'activated_at': '01.01.2022',
                    'activated_at_iso': '2022-01-01T00:00:00+00:00',
                    'is_trial': False,
                    'need_alerting_about_finishing_trial': True,
                },
                {
                    'place_id': 7,
                    'tariff_info': {'type': 'free', 'features': []},
                    'valid_until': '27.04.2022',
                    'valid_until_iso': '2022-04-27T03:00:00+03:00',
                    'activated_at': '01.01.2022',
                    'activated_at_iso': '2022-01-01T00:00:00+00:00',
                    'is_trial': True,
                    'need_alerting_about_finishing_trial': False,
                },
            ],
        }
        return mockserver.make_response(status=200, json=subscriptions)


def pytest_configure(config):
    config.addinivalue_line('markers', 'eats_core_error: eats core error')
    config.addinivalue_line('markers', 'route: route')


@pytest.fixture
def mock_eats_core_billing_info(mockserver, request):
    @mockserver.json_handler('/eats-core-restapp/v1/places/billing-info')
    def _mock_core(request):
        assert request.args['place_id'] == '42'
        return mockserver.make_response(
            status=200,
            json={
                'payload': [
                    {
                        'tanker_key': 'eats_restapp_places_billing_info_inn',
                        'value': '9705114405',
                    },
                    {
                        'tanker_key': (
                            'eats_restapp_places_billing_info_account'
                        ),
                        'value': '40702810638000093677',
                    },
                    {
                        'tanker_key': (
                            'eats_restapp_places_billing_info_address_postcode'
                        ),
                        'value': '115035',
                    },
                    {
                        'tanker_key': (
                            'eats_restapp_places_billing_info_address_full'
                        ),
                        'value': (
                            'Москва, ул Садовническая, д 82, стр 2, пом 3'
                        ),
                    },
                ],
            },
        )


@pytest.fixture
def mock_eats_core_billing_info_400(mockserver, request):
    @mockserver.json_handler('/eats-core-restapp/v1/places/billing-info')
    def _mock_core(request):
        assert request.args['place_id'] == '42'
        return mockserver.make_response(status=400, json={'errors': 'error'})


@pytest.fixture
def mock_eats_plus_first_date(mockserver, request):
    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/first_plus_activation_date',
    )
    def _mock_plus(request):
        return mockserver.make_response(
            status=200,
            json={
                'places': [
                    {
                        'place_id': 42,
                        'active': True,
                        'first_plus_activation_date': (
                            '2022-05-01T03:00:00+03:00'
                        ),
                    },
                ],
            },
        )


@pytest.fixture
def mock_eats_plus_first_date_400(mockserver, request):
    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/first_plus_activation_date',
    )
    def _mock_plus(request):
        return mockserver.make_response(status=400)
