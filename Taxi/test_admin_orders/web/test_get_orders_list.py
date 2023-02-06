# pylint: disable=C0302

import copy
import json
import os

import bson
import pytest

TRANSLATIONS_TARIFF = {
    'name.econom': {'ru': 'Эконом', 'en': 'Econom'},
    'name.express': {'ru': 'Доставка', 'en': 'Delivery'},
    'name.business': {'ru': 'Комфорт'},
    'name.comfort': {'ru': 'Комфорт', 'en': 'Comfort'},
    'name.vip': {'ru': 'Бизнес'},
    'name.comfortplus': {'ru': 'Комфорт+'},
    'name.minivan': {'ru': 'Минивэн'},
    'name.pool': {'ru': 'Попутка'},
    'name.business2': {'ru': 'Комфорт2'},
    'name.uberx': {'ru': 'UberX'},
    'name.uberselect': {'ru': 'UberSelect'},
    'name.uberblack': {'ru': 'UberBlack'},
    'name.uberkids': {'ru': 'UberKids'},
}
TRANSLATIONS_GEOAREAS = {
    'moscow': {'ru': 'Москва', 'en': 'Moscow'},
    'ekb': {'ru': 'Екатеринбург', 'en': 'Ekaterinburg'},
    'spb': {'ru': 'Санкт-Петербург', 'en': 'Saint Petersburg'},
}
CONFIGS = dict(
    TVM_RULES=[
        {'dst': 'archive-api', 'src': 'admin-orders'},
        {'dst': 'tariffs', 'src': 'admin-orders'},
    ],
    LOCALES_SUPPORTED=['ru', 'en'],
)
TRANSLATIONS = dict(tariff=TRANSLATIONS_TARIFF)
TARGET_INFO_PREFIX = '/replication/state/yt_target_info/'

RESPONSE_CACHE = {}

RESPONSES_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_get_orders_list', 'responses',
)

for root, _, filenames in os.walk(RESPONSES_DIR):
    for filename in filenames:
        full_filename = os.path.join(root, filename)
        if filename.endswith('.bson.json'):
            with open(full_filename) as f:
                RESPONSE_CACHE[filename[:-5]] = bson.json_util.loads(f.read())
        elif filename.endswith('.json'):
            with open(full_filename) as f:
                RESPONSE_CACHE[filename] = json.load(f)


@pytest.fixture
def taxi_admin_orders_mocks(mockserver, order_archive_mock):
    class _Mock:
        @mockserver.json_handler('/audit/v1/robot/logs/')
        @staticmethod
        def log_audit(request):
            return {'id': 'audit_log_id'}

        @mockserver.handler('/taxi-tariffs/v1/tariff_zones')
        @staticmethod
        def _get_tariff_zones(request):
            locale = request.query['locale']
            zones = RESPONSE_CACHE[f'tariffs_v1_tariff_zones_{locale}.json']
            return mockserver.make_response(json=zones)

        @mockserver.handler(TARGET_INFO_PREFIX, prefix=True)
        @staticmethod
        def _get_target_info(request):
            target_name = request.path_qs[len(TARGET_INFO_PREFIX) :]
            if target_name == 'order_proc_admin':
                folder = 'struct'
                table_name = 'order_proc_admin'
            elif target_name.startswith('order_proc_'):
                folder = 'indexes/order_proc'
                if target_name.endswith('_index'):
                    table_name = target_name[
                        len('order_proc_') : -len('_index')
                    ]
                else:
                    table_name = target_name[len('order_proc_') :]
            else:
                folder = 'as_is'
                table_name = target_name
            return mockserver.make_response(
                json={
                    'table_path': f'replica/mongo/{folder}/{table_name}',
                    'full_table_path': 'full_table_path',
                    'target_names': ['does', 'not', 'matter'],
                    'clients_delays': 0,  # does not matter
                },
            )

        order_archive_mock.set_order_proc(
            RESPONSE_CACHE['order_archive-order_proc-retrieve.json'],
        )

        @mockserver.json_handler('/territories/v1/countries/list')
        @staticmethod
        def _get_countries_list(request):
            return RESPONSE_CACHE['territories_v1_countries_list.json']

        @mockserver.json_handler('/personal/v1/phones/find')
        @staticmethod
        def _personal_phones(request):
            phone = request.json['value']
            phone_to_personal = RESPONSE_CACHE['personal_phones.json']
            if phone in phone_to_personal:
                return {'id': phone_to_personal[phone], 'value': phone}
            return mockserver.make_response(
                status=404,
                json={'code': '404', 'message': 'No document with such id'},
            )

        @mockserver.json_handler('/personal/v1/emails/find')
        @staticmethod
        def _personal_emails(request):
            email = request.json['value']
            email_to_personal = RESPONSE_CACHE['personal_emails.json']
            if email in email_to_personal:
                return {'id': email_to_personal[email], 'value': email}
            return mockserver.make_response(
                status=404,
                json={'code': '404', 'message': 'No document with such id'},
            )

        @mockserver.json_handler(
            '/user-api/user_phones/by_personal/retrieve_bulk',
        )
        @staticmethod
        def _get_phone_docs(request):
            phone_data = request.json['items'][0]
            personal_phone_id = phone_data['personal_phone_id']
            phone_type = phone_data.get('type')
            res = RESPONSE_CACHE[
                f'user-api_retrieve_bulk_{personal_phone_id}.json'
            ]
            return {
                'items': [
                    phone_doc
                    for phone_doc in res['items']
                    if phone_type is None or phone_doc['type'] == phone_type
                ],
            }

        @mockserver.json_handler('/user-api/user_emails/get')
        @staticmethod
        def _user_api_emails(request):
            personal_email_id = request.json['personal_email_ids'][0]
            personal_to_emails = RESPONSE_CACHE['user-api_emails.json']
            return {'items': personal_to_emails.get(personal_email_id, [])}

        @mockserver.handler('/parks-replica/v1/parks/retrieve')
        @staticmethod
        def _get_parks_info(request):
            all_parks = RESPONSE_CACHE['parks-replica_v1_parks_retrieve.json']
            return mockserver.make_response(json=all_parks)

        @mockserver.handler('/maas/internal/v1/mark-maas-orders')
        @staticmethod
        def _mark_maas_orders(request):
            maas_orders = RESPONSE_CACHE['maas_mark_maas_orders.json']
            return mockserver.make_response(json=maas_orders)

        @mockserver.handler(
            '/order-core/internal/processing/v1/order-proc/get-order',
        )
        @staticmethod
        def _order_core_get_order(request):
            order_id = request.json['order_id']
            body = RESPONSE_CACHE.get(f'order_core_get_{order_id}.bson')
            if body is None:
                return mockserver.make_response(
                    status=404,
                    json={'code': 'no_such_order', 'message': 'no_such_order'},
                )

            return mockserver.make_response(
                status=200,
                content_type='application/bson',
                response=bson.BSON.encode(body),
            )

    return _Mock()


@pytest.fixture
def mock_yt_simple(mockserver):
    """Mock select_rows with simple filtering"""

    def _extract_field_params(query_string, query_params, field):
        where = query_string.split('WHERE')[1]
        and_clauses = where.split(' AND ')
        field_clause = [chunk for chunk in and_clauses if field in chunk][0]
        params_count = field_clause.count('%p')
        return query_params[2 : 2 + params_count]

    def _get_phone_ids(query_string, query_params):
        phone_ids = _extract_field_params(
            query_string, query_params, 'phone_id',
        )
        if 'index.contact_type = %p' in query_string:
            contact_type = query_params[2 + len(phone_ids)]
        else:
            contact_type = None
        return contact_type, phone_ids

    def _get_user_uids(query_string, query_params):
        return _extract_field_params(query_string, query_params, 'user_uid')

    def _get_items_by_contact_phones(item_rows, query_string, query_params):
        contact_type, phone_ids = _get_phone_ids(query_string, query_params)
        rows = []
        for row in item_rows['items']:
            contact_phones = set()
            source_phone_id = row.get('source_contact_phone_id')
            if source_phone_id and contact_type in {'source', None}:
                contact_phones.add(source_phone_id)
            destination_phones = row.get('destinations_contact_phone_ids', [])
            if destination_phones and contact_type in {'destination', None}:
                contact_phones.update(destination_phones)
            extra_user_phone_id = row.get('extra_user_phone_id')
            if extra_user_phone_id and contact_type in {'extra_user', None}:
                contact_phones.add(extra_user_phone_id)
            if contact_phones.intersection(phone_ids):
                if extra_user_phone_id:
                    row = copy.deepcopy(row)
                    # normally this field is absent in archive-api response
                    # it's a test hack here
                    del row['extra_user_phone_id']
                rows.append(row)
        return {'items': rows}

    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    # pylint: disable=W0612
    def _select_rows(request):
        request_data = json.loads(request.get_data())
        query_string = request_data['query']['query_string']
        query_params = request_data['query']['query_params']
        index_path = query_params[0]
        index_name = index_path.rsplit('/')[-1]
        response_fname = f'archive-api_v1_yt_select_rows_{index_name}.json'
        all_rows = RESPONSE_CACHE[response_fname]
        if index_name == 'phone_id_created_contact_type':
            return _get_items_by_contact_phones(
                all_rows, query_string, query_params,
            )
        if 'WHERE index.order_id = %p' in query_string:
            order_id = query_params[2]
            rows = []
            for row in all_rows['items']:
                if row['id'] == order_id:
                    rows.append(row)
            return {'items': rows}
        if 'WHERE index.city_id = %p' in query_string:
            city_id = query_params[2]
            rows = []
            for row in all_rows['items']:
                if row['city_id'] == city_id:
                    rows.append(row)
            return {'items': rows}
        if ' WHERE index.phone_id IN (' in query_string:
            _, phone_ids = _get_phone_ids(query_string, query_params)
            rows = []
            for row in all_rows['items']:
                if row['phone_id'] in phone_ids:
                    rows.append(row)
            return {'items': rows}
        if ' WHERE index.created <= -%p' in query_string:
            created = query_params[2]
            rows = []
            for row in all_rows['items']:
                if row['created'] >= created:
                    rows.append(row)
            return {'items': rows}
        if ' WHERE index.user_uid IN (' in query_string:
            user_uids = _get_user_uids(query_string, query_params)
            rows = []
            for row in all_rows['items']:
                if row['user_uid'] in user_uids:
                    rows.append(row)
            return {'items': rows}
        return all_rows


@pytest.fixture
def mock_yt_many_cities(mockserver):
    """Mock select_rows with filtering by group of cities"""

    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    # pylint: disable=W0612
    def _select_rows(request):
        assert 'X-YaRequestId' in request.headers
        all_rows = RESPONSE_CACHE['archive-api_v1_yt_select_rows.json']
        request_data = json.loads(request.get_data())
        query_string = request_data['query']['query_string']
        query_params = request_data['query']['query_params']
        if ' WHERE index.created <= -%p' in query_string:
            created = query_params[2]
            rows = []
            for row in all_rows['items']:
                if row['created'] >= created:
                    rows.append(row)
            all_rows = {'items': rows}
        if 'AND index.city_id IN (' in query_string:
            # city_ids are %p placeholders except those for created & limit
            city_ids_count = query_string.count('%p') - 2
            # first 2 params are tables, third is index.created, then cities go
            city_ids = query_params[3 : 3 + city_ids_count]
            rows = []
            for row in all_rows['items']:
                if row['city_id'] in city_ids:
                    rows.append(row)
            return {'items': rows}
        if 'AND NOT (index.city_id IN (' in query_string:
            city_ids_count = query_string.count('%p') - 2
            city_ids = query_params[3 : 3 + city_ids_count]
            rows = []
            for row in all_rows['items']:
                if row['city_id'] not in city_ids:
                    rows.append(row)
            return {'items': rows}
        return all_rows


async def _check_log_audit(log_audit_handler, field, value):
    assert log_audit_handler.times_called == 1
    patched_call_args = await log_audit_handler.wait_call()
    patched_call_request = patched_call_args['request']
    assert patched_call_request.method == 'POST'
    audit_arguments = patched_call_request.json['arguments']
    assert audit_arguments[field] == value
    assert patched_call_request.json['action'] == 'search_orders_pd'
    assert patched_call_request.json['login'] == 'phoneseeker'


TEST_PARAMS_OK = [
    # empty request (searches in mongo only)
    ({}, 'ru', 200, 'admin_orders_v1_orders_from_mongo'),
    ({}, 'en', 200, 'admin_orders_v1_orders_from_mongo_en'),
    # almost empty request (searches in yt, too)
    (
        {
            'created_to': '2020-02-10T00:00:00',
            'created_from': '2020-02-01T00:00:00',
        },
        'ru',
        200,
        'admin_orders_v1_orders',
    ),
    (
        {
            'created_to': '2020-02-10T00:00:00',
            'created_from': '2020-02-01T00:00:00',
        },
        'en',
        200,
        'admin_orders_v1_orders_en',
    ),
    # exclude orders before "from" and after "to" for order_proc
    (
        {
            'user_uid': '707467832',
            'created_from': '2020-02-06T13:40:00',
            'created_to': '2020-02-06T13:41:00',
        },
        'ru',
        200,
        'admin_orders_v1_orders_empty',
    ),
    # search by order_id
    (
        {'order_id': '8be2235988d1658d953d874023e38b45'},
        'ru',
        200,
        'admin_orders_v1_orders_8be2235988d1658d953d874023e38b45',
    ),
    # search by alias_id
    (
        {'order_id': '8be2235988d1658d953d874023e38b45_alias_id'},
        'ru',
        200,
        'admin_orders_v1_orders_8be2235988d1658d953d874023e38b45',
    ),
    # search by UID
    (
        {'user_uid': '4052247306'},
        'ru',
        200,
        'admin_orders_v1_orders_user_uid_4052247306',
    ),
]


@pytest.mark.parametrize(
    ['request_dict', 'locale', 'expected_status', 'expected_filename'],
    TEST_PARAMS_OK,
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_orders_list(
        taxi_admin_orders_web,
        request_dict,
        locale,
        expected_status,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': locale, 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['request_dict', 'locale', 'expected_status', 'expected_filename'],
    TEST_PARAMS_OK,
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_orders_list_with_warnings(
        taxi_admin_orders_web,
        request_dict,
        locale,
        expected_status,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/?with_warnings=true',
        json=request_dict,
        headers={'Accept-Language': locale, 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == {
        'items': RESPONSE_CACHE[f'{expected_filename}.json'],
        'warnings': [],
    }


@pytest.mark.parametrize(
    ['request_dict', 'locale', 'expected_status', 'expected_filename'],
    [
        # search by city_id
        (
            {'city': 'Санкт-Петербург'},
            'ru',
            200,
            'admin_orders_v1_orders_city_spb_ru',
        ),
        # search by lowercase city_id with whitespaces around
        (
            {'city': ' санкт-петербург '},
            'ru',
            200,
            'admin_orders_v1_orders_city_spb_ru',
        ),
        # search by city translation
        (
            {'city': 'Ekaterinburg'},
            'ru',
            200,
            'admin_orders_v1_orders_city_ekb_en',
        ),
        # search by unexistent city
        (
            {'city': 'Unexistenburg'},
            'ru',
            200,
            'admin_orders_v1_orders_city_not_found',
        ),
        # search by city name not present in zone translations
        ({'city': 'Астана'}, 'ru', 200, 'admin_orders_v1_orders_city_astana'),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_search_by_city(
        taxi_admin_orders_web,
        request_dict,
        locale,
        expected_status,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': locale, 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['request_dict', 'expected_status', 'expected_filename'],
    [
        ({'last_orders': 5}, 200, 'admin_orders_v1_orders_from_mongo'),
        ({'last_days': 2}, 200, 'admin_orders_v1_orders_last_2_days'),
    ],
)
@pytest.mark.now('2020-02-07T00:00:00')  # for testing last_days
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_view_orders_limited(
        taxi_admin_orders_web,
        request_dict,
        expected_status,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    expected_content = RESPONSE_CACHE[f'{expected_filename}.json']
    if request_dict.get('last_orders') is not None:
        expected_content = expected_content[: request_dict['last_orders']]
    assert content == expected_content


@pytest.mark.parametrize(
    ['request_dict', 'expected_status', 'expected_filename'],
    [
        # search in russian cities
        ({'countries_filter': ['rus']}, 200, 'admin_orders_v1_orders'),
        # # search in non-russian cities
        (
            {'countries_filter': ['isr']},
            200,
            'admin_orders_v1_orders_country_isr',
        ),
        # search with no countries allowed
        ({'countries_filter': []}, 200, 'admin_orders_v1_orders_empty'),
        # restricted by country with no cities in zones
        ({'countries_filter': ['arm']}, 200, 'admin_orders_v1_orders_empty'),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_many_cities')
async def test_countries_filter(
        taxi_admin_orders_web,
        request_dict,
        expected_status,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['request_dict', 'expected_filename'],
    [
        (
            {'phone': '+79099670585'},
            'admin_orders_v1_orders_phone_79099670585',
        ),
        (
            {'phone': '+79099670585', 'phone_type': 'yandex'},
            'admin_orders_v1_orders_phone_79099670585_yandex',
        ),
        (
            {'phone': '+79099670585', 'phone_type': 'uber'},
            'admin_orders_v1_orders_phone_79099670585_uber',
        ),
        # search by uncleaned phones
        ({'phone': '89099670585'}, 'admin_orders_v1_orders_phone_79099670585'),
        ({'phone': '79099670585'}, 'admin_orders_v1_orders_phone_79099670585'),
        # no orders for phone
        ({'phone': '+70000930068'}, 'admin_orders_v1_orders_empty'),
        # find_orders with contact phone
        ({'phone': '79998887766'}, 'admin_orders_v1_orders_phone_79998887766'),
        ({'phone': '79990007766'}, 'admin_orders_v1_orders_phone_79990007766'),
        # find_orders with contact phone and contact type
        (
            {'phone': '79990007766', 'contact_type': 'source'},
            'admin_orders_v1_orders_phone_79990007766_src',
        ),
        (
            {'phone': '79990007766', 'contact_type': 'destination'},
            'admin_orders_v1_orders_phone_79990007766_dst',
        ),
        (
            {'phone': '79990007766', 'contact_type': 'passenger'},
            'admin_orders_v1_orders_phone_79990007766_pass',
        ),
        (
            {'phone': '79990007766', 'contact_type': 'extra_user'},
            'admin_orders_v1_orders_phone_79990007766_extra',
        ),
        # find_orders with application
        (
            {'phone': '79990007766', 'application': 'alice'},
            'admin_orders_v1_orders_phone_79990007766_app_alice',
        ),
        (
            {'phone': '79990007766', 'application': 'web'},
            'admin_orders_v1_orders_phone_79990007766_app_web',
        ),
        # no orders with this application
        (
            {'phone': '79990007766', 'application': 'iphone'},
            'admin_orders_v1_orders_empty',
        ),
        # find with payment_type
        (
            {'phone': '79990007766', 'payment_type': 'cash'},
            'admin_orders_v1_orders_phone_79990007766_payment_cash',
        ),
        (
            {'phone': '79990007766', 'payment_type': 'card'},
            'admin_orders_v1_orders_phone_79990007766_payment_card',
        ),
        # no orders with this payment type
        (
            {'phone': '79990007766', 'payment_type': 'corp'},
            'admin_orders_v1_orders_empty',
        ),
        # no orders with this payment type
        (
            {'phone': '79990007766', 'payment_type': 'corp'},
            'admin_orders_v1_orders_empty',
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('mock_yt_simple')
async def test_phone_search(
        taxi_admin_orders_web,
        taxi_admin_orders_mocks,  # pylint: disable=redefined-outer-name
        request_dict,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'phoneseeker'},
    )
    content = await response.json()
    expected_content = RESPONSE_CACHE[f'{expected_filename}.json']
    assert content == expected_content
    await _check_log_audit(
        taxi_admin_orders_mocks.log_audit, 'phone', request_dict['phone'],
    )


@pytest.mark.parametrize(
    ['request_dict', 'expected_filename'],
    [  # every test has 2 result orders: from mongo and YT
        pytest.param(
            {'email': 'user111@yandex.ru'},
            'admin_orders_v1_orders_email_for_two_phones',
            id='email_with_orders_for_two_phones',
        ),
        pytest.param(
            {'email': 'user222@yandex.ru'},
            'admin_orders_v1_orders_email_for_two_uids',
            id='email_with_orders_for_two_uids',
        ),
        pytest.param(
            {'email': 'user333@yandex.ru'},
            'admin_orders_v1_orders_email_for_phones_or_uids',
            id='email_with_orders_for_phones_or_uids',
        ),
        ({'email': 'no_exists@yandex.ru'}, 'admin_orders_v1_orders_empty'),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('mock_yt_simple')
async def test_email_search(
        taxi_admin_orders_web,
        taxi_admin_orders_mocks,  # pylint: disable=redefined-outer-name
        request_dict,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'phoneseeker'},
    )
    content = await response.json()
    expected_content = RESPONSE_CACHE[f'{expected_filename}.json']
    assert content == expected_content
    await _check_log_audit(
        taxi_admin_orders_mocks.log_audit, 'email', request_dict['email'],
    )


@pytest.mark.parametrize(
    [
        'with_warnings',
        'request_dict',
        'locale',
        'expected_status',
        'expected_filename',
    ],
    [
        # search by application without phone (must be code 400)
        # see test_phone_search for code 200
        (
            False,
            {'application': 'web'},
            'ru',
            400,
            'admin_orders_v1_orders_error_app_without_phone',
        ),
        # search by application not in config (must be code 400)
        (
            False,
            {'application': 'fraud_iphone', 'phone': '89099670585'},
            'ru',
            400,
            'admin_orders_v1_orders_error_app_not_in_list',
        ),
        # search by payment_type not in config (must be code 400)
        (
            False,
            {'payment_type': 'nature', 'phone': '89099670585'},
            'ru',
            400,
            'admin_orders_v1_orders_error_payment_not_in_list',
        ),
        (
            True,
            {'phone': '+70000930068'},
            'ru',
            200,
            'admin_orders_v1_orders_warnings_no_phone_found',
        ),
        (
            True,
            {'email': 'no_exists@example.ru'},
            'ru',
            200,
            'admin_orders_v1_orders_warnings_no_email_found',
        ),
        (
            True,
            {'phone': '+79099670585', 'email': 'user@yandex.ru'},
            'ru',
            400,
            'admin_orders_v1_orders_error_email_and_phone_together',
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_phone_search_errors(
        taxi_admin_orders_web,
        mockserver,
        with_warnings,
        request_dict,
        locale,
        expected_status,
        expected_filename,
):
    @mockserver.json_handler('/personal/v1/emails/find')
    def _personal_emails(request):
        return {'id': 'id', 'value': 'value'}

    response = await taxi_admin_orders_web.post(
        f'/v1/orders/?with_warnings={str(with_warnings).lower()}',
        json=request_dict,
        headers={'Accept-Language': locale, 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['request_dict', 'expected_status', 'expected_filename'],
    [
        (
            {'created_to': '2020-05-01T00:00:00'},
            400,
            'admin_orders_v1_orders_error_created_to',
        ),
        (
            {'request_due_to': '2020-05-01T00:00:00'},
            400,
            'admin_orders_v1_orders_error_request_due_to',
        ),
        (
            {'request_due_from': '2020-06-01T00:00:00', 'phone': 'some_phone'},
            400,
            'admin_orders_v1_orders_error_request_due_and_phone',
        ),
    ],
)
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_search_by_time_restrictions(
        taxi_admin_orders_web,
        request_dict,
        expected_status,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    expected_content = RESPONSE_CACHE[f'{expected_filename}.json']
    assert content == expected_content


@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_search_by_driver_license_pd_id(
        taxi_admin_orders_web, mockserver,
):
    @mockserver.json_handler('personal/v1/driver_licenses/retrieve')
    # pylint: disable=W0612
    def mock_personal(request):
        pd_id = request.json['id']
        return {'id': pd_id, 'value': pd_id[:-3]}

    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    # pylint: disable=W0612
    def mock_yt(request):
        request_data = json.loads(request.get_data())
        query_string = request_data['query']['query_string']
        assert 'WHERE index.driver_license = %p' in query_string
        return {'items': []}

    await taxi_admin_orders_web.post(
        '/v1/orders/',
        json={'license_pd_id': 'some_license_id'},
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )

    assert mock_personal.times_called == 1
    assert mock_yt.times_called == 1


@pytest.mark.parametrize(
    ['request_dict', 'expected_status', 'expected_filename'],
    [
        # this search only in yt because no indexes
        (
            {'driver_license': 'some_driver_license', 'order_short_id': '1'},
            200,
            'admin_orders_v1_orders_opteum_from_yt_only.json',
        ),
        (
            {
                'status': 'cancelled',
                'driver_license': 'some_driver_license',
                'order_short_id': '4',
            },
            200,
            'admin_orders_v1_orders_opteum_from_orders.json',
        ),
        # this search only in order_proc and yt
        (
            {
                'driver_license': 'candidate_driver_license',
                'order_short_id': '4',
                'use_candidates': True,
            },
            200,
            'admin_orders_v1_orders_opteum_from_order_proc.json',
        ),
        # unable to search without driver license
        (
            {'order_short_id': '4'},
            400,
            'admin_orders_v1_orders_opteum_filter_error.json',
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_search_by_driver_license_and_opteum_id(
        taxi_admin_orders_web,
        mockserver,
        request_dict,
        expected_filename,
        expected_status,
):
    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    # pylint: disable=W0612
    def mock_yt(request):
        request_data = json.loads(request.get_data())
        query_string = request_data['query']['query_string']
        query_params = request_data['query']['query_params']
        assert 'driver_license = %p' in query_string
        assert request_dict['driver_license'] in query_params
        assert 'order_short_id = %p' not in query_string
        assert request_dict['order_short_id'] not in query_params
        return RESPONSE_CACHE['archive-api_v1_yt_select_rows_opteum.json']

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _mock_driver_license(request):
        return {'id': request.json['value'], 'value': request.json['value']}

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def _mock_driver_profiles(request):
        return RESPONSE_CACHE['driver_profiles_response.json']

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return RESPONSE_CACHE['fleet_parks_response.json']

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    # pylint: disable=W0612
    def mock_driver_orders(request):
        request_data = json.loads(request.get_data())
        request_orders = request_data['query']['park']['order']['ids']
        mocked_orders = RESPONSE_CACHE['driver_orders_response.json']['orders']
        matched_orders = []
        for order in mocked_orders:
            if order['id'] in request_orders:
                matched_orders.append(order)
        return {'orders': matched_orders}

    response = await taxi_admin_orders_web.post(
        '/v1/orders/',
        json=request_dict,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert expected_status == response.status
    response_body = await response.json()
    if expected_status == 200:
        assert mock_yt.times_called == 1
    expected_body = RESPONSE_CACHE[expected_filename]
    assert response_body == expected_body


@pytest.mark.filldb(order_proc='anonymized')
@pytest.mark.parametrize(
    [
        'request_dict',
        'select_rows_filename',
        'expected_status',
        'expected_filename',
    ],
    [
        (
            {'user_uid': '4034567800', 'deanonymize': True},
            None,
            200,
            'admin_orders_v1_orders_deanonymized_1.json',
        ),
        (
            {'user_uid': '4034567800', 'deanonymize': False},
            None,
            200,
            'admin_orders_v1_orders_deanonymized_1.json',
        ),
        (
            {
                'order_id': '023db41534f74832b3125d76932a9002',
                'deanonymize': True,
            },
            None,
            200,
            'admin_orders_v1_orders_deanonymized_2.json',
        ),
        (
            {
                'user_id': '944463deff564bb2a0b3b5cea753a0cc',
                'deanonymize': True,
            },
            'archive-api_v1_yt_select_rows_anonymized_orders.json',
            200,
            'admin_orders_v1_orders_deanonymized_3.json',
        ),
        (
            {
                'user_id': '944463deff564bb2a0b3b5cea753a0cc',
                'deanonymize': False,
            },
            'archive-api_v1_yt_select_rows_anonymized_orders.json',
            200,
            'admin_orders_v1_orders_deanonymized_4.json',
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_search_deanonymize(
        taxi_admin_orders_web,
        mockserver,
        request_dict,
        select_rows_filename,
        expected_filename,
        expected_status,
):
    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    def _select_rows(request):
        if select_rows_filename is not None:
            return RESPONSE_CACHE[select_rows_filename]
        return {'items': []}

    response = await taxi_admin_orders_web.post(
        '/v1/orders/?with_warnings=true',
        json=request_dict,
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == RESPONSE_CACHE[expected_filename]
