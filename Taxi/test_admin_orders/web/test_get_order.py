# pylint: disable=C0302

import json
import os

import aiohttp.web
import bson.json_util
import pytest

from testsuite.utils import callinfo

from test_admin_orders.web import helpers

TRANSLATIONS_ORDER = {
    'change.name.user_ready': {'ru': 'Уже выхожу'},
    'change.name.dont_call': {'ru': 'Не звонить'},
    'discount.method.subvention-fix': {
        'ru': 'Полная скидка с лимитом и ограничениями',
    },
    'discount.reason.for_all': {'ru': 'Для всех'},
    'subvention.decline_reason.surge': {
        'ru': 'Из-за сурджа (повышающего коэффициента)',
    },
}
TRANSLATIONS_TARIFF = {
    'currency.rub': {'ru': 'руб.', 'en': 'rub'},
    'currency_sign.rub': {'ru': '₽', 'en': '₽'},
    'name.econom': {'ru': 'Эконом', 'en': 'Econom'},
    'name.express': {'ru': 'Доставка', 'en': 'Delivery'},
    'name.business': {'ru': 'Комфорт'},
    'name.comfort': {'ru': 'Комфорт', 'en': 'Comfort'},
}
TRANSLATIONS_TARIFF_VEZET = {
    'currency.rub': {'ru': 'руб.', 'en': 'rub'},
    'currency_sign.rub': {'ru': '₽', 'en': '₽'},
    'name.econom': {'ru': 'Везет эконом', 'en': 'Vezet econom'},
    'name.express': {'ru': 'Везет доставка', 'en': 'Vezet delivery'},
    'name.business': {'ru': 'Везет комфорт'},
    'name.comfort': {'ru': 'Везет комфорт', 'en': 'Vezet comfort'},
}
TRANSLATIONS_TARIFF_EDITOR = {
    'order_info.address_details.apartment': {'ru': 'кв.'},
    'order_info.address_details.floor': {'ru': 'этаж'},
    'order_info.address_details.porch': {'ru': 'подъезд'},
    'candidates.reposition_mode.home': {'ru': 'Домой'},
    'candidates.reposition_mode.poi_coms': {'ru': 'По Делам с комиссией'},
}
EDITABLE_REQUIREMENTS_BY_ZONE = {
    '__default__': {},
    'ekb': {
        'luggage_count': {
            'default_value': 0,
            'max_value': 100,
            'min_value': 0,
        },
        'third_passenger': {
            'default_value': 0,
            'max_value': 100,
            'min_value': 0,
        },
    },
}
CONFIGS = dict(
    TVM_RULES=[{'dst': 'archive-api', 'src': 'admin-orders'}],
    LOCALES_SUPPORTED=['ru', 'en'],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    EDITABLE_REQUIREMENTS_BY_ZONE=EDITABLE_REQUIREMENTS_BY_ZONE,
    ENABLE_DRIVER_CHANGE_COST=True,
    USE_PAYMENT_EVENTS=True,
    CHATTERBOX_ANTIFRAUD_RULES_FOR_META=['flag_enabled', 'flag_disabled'],
    ADMIN_ORDERS_ORDERS_FULL_THRESHOLD_DATE='2018-01-01T00:00:00',
)
CONFIGS_WITH_PASSENGER_FEEDBACK = dict(
    ADMIN_ORDERS_ENABLE_NEW_PASSENGER_FEEDBACK_SOURCE=True, **(CONFIGS or {}),
)

TRANSLATIONS = dict(
    order=TRANSLATIONS_ORDER,
    tariff=TRANSLATIONS_TARIFF,
    tariff_vezet=TRANSLATIONS_TARIFF_VEZET,
    tariff_editor=TRANSLATIONS_TARIFF_EDITOR,
)

RESPONSE_CACHE = {}

RESPONSES_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_get_order', 'responses',
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
def taxi_admin_orders_mocks(mockserver, load_json, order_archive_mock):
    """Put your mocks here"""

    def _set_order_proc():
        for resp_filename, response in RESPONSE_CACHE.items():
            if resp_filename.startswith('order_archive-order_proc-retrieve'):
                order_archive_mock.set_order_proc(response['doc'])

    _set_order_proc()

    @mockserver.handler('/archive-api/archive/', prefix=True)
    def _get_archive_order(request):
        return aiohttp.web.Response(status=404)

    @mockserver.json_handler('/replication/map_data')
    def _map_data(request):
        response = RESPONSE_CACHE['replication_map_data.json']
        for row in request.json.get('items'):
            # check if request was made to passenger-feedback service
            if row.get('target_name') == 'feedbacks_full':
                feedback_data = json.loads(row.get('data')).get('data', {})
                # check passenger-feedback response content then load fixture
                assert sorted(feedback_data) == sorted(
                    RESPONSE_CACHE['feedback_retrieve_struct_data.json'],
                )
                return mockserver.make_response(
                    json=RESPONSE_CACHE['replication_feedback_map_data.json'],
                )
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/user_api-api/user_phones/get')
    def _user_phones_get(request):
        response = RESPONSE_CACHE['user-api_user_phones_get.json']
        return mockserver.make_response(json=response)

    @mockserver.json_handler('/fleet-parks/v1/parks/contacts/retrieve')
    def _contacts_retrieve(request):
        park_id = request.query['park_id']
        resp_fname = f'fleet-parks_v1_parks_contacts_retrieve_{park_id}.json'
        if resp_fname not in RESPONSE_CACHE:
            return aiohttp.web.Response(
                status=404,
                body='{"code": "not_found", "message": "Park not found"}',
            )
        return mockserver.make_response(json=RESPONSE_CACHE[resp_fname])

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        responses = RESPONSE_CACHE['fleet-parks_v1_parks_list.json']
        request_data = json.loads(request.get_data())
        park_ids = set(request_data['query']['park']['ids'])
        responses = [
            park for park in responses['parks'] if park['id'] in park_ids
        ]
        return mockserver.make_response(json={'parks': responses})

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        response_filename = 'driver-profiles_v1_driver_profiles_retrieve.json'
        responses = RESPONSE_CACHE[response_filename]
        request_data = json.loads(request.get_data())
        driver_ids = set(request_data['id_in_set'])
        responses = [
            profile
            for profile in responses['profiles']
            if profile['park_driver_profile_id'] in driver_ids
        ]
        return mockserver.make_response(json={'profiles': responses})

    @mockserver.handler('/parks-replica/v1/parks/retrieve')
    def _get_parks_info(request):
        response_dict = RESPONSE_CACHE['parks-replica_v1_parks_retrieve.json']
        return mockserver.make_response(json=response_dict)

    @mockserver.handler('/parks-replica/v1/parks/billing_client_id/retrieve')
    def _get_billing_client_id(request):
        clid = request.query['park_id']
        fname = f'parks-replica_billing_client_id_retrieve_{clid}.json'
        return mockserver.make_response(json=RESPONSE_CACHE[fname])

    @mockserver.json_handler('/billing-replication/person/')
    def _get_billing_person(request):
        client_id = request.query['client_id']
        fname = f'billing-replication_person_{client_id}.json'
        return mockserver.make_response(json=RESPONSE_CACHE[fname])

    @mockserver.handler('/taxi-tariffs/v1/tariff_zones')
    def _get_tariff_zones(request):
        locale = request.query['locale']
        zones = RESPONSE_CACHE[f'tariffs_v1_tariff_zones_{locale}.json']
        return mockserver.make_response(json=zones)

    @mockserver.json_handler('/coupons/admin/promocodes/list/')
    def _promocodes_list(request):
        if 'series_id' in request.query:
            suffix = request.query['series_id']
        elif 'for_support' in request.query:
            suffix = 'support'
        else:
            suffix = ''
        response_filename = f'coupons_admin_promocodes_list_{suffix}.json'
        series_items = RESPONSE_CACHE[response_filename]
        return mockserver.make_response(json=series_items)

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_unique_driver_ids(request):
        fname = 'unique-drivers_v1_driver_uniques_retrieve_by_profiles.json'
        return mockserver.make_response(json=RESPONSE_CACHE[fname])

    @mockserver.json_handler('/driver-ratings/v2/driver/rating/batch-retrieve')
    def _retrieve_driver_ratings_new(request):
        fname = 'driver-ratings_v2_driver_ratings_retrieve.json'
        return mockserver.make_response(json=RESPONSE_CACHE[fname])

    @mockserver.json_handler('/driver-ratings/v1/driver/ratings/retrieve')
    def _retrieve_driver_ratings(request):
        fname = 'driver-ratings_v1_driver_ratings_retrieve.json'
        return mockserver.make_response(json=RESPONSE_CACHE[fname])

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profiles')
    def _retrieve_driver_tags(request):
        fname = 'driver-tags_v1_drivers_match_profiles.json'
        return mockserver.make_response(json=RESPONSE_CACHE[fname])

    @mockserver.json_handler('/driver-work-rules/service/v1/changes/list')
    def _retrieve_driver_changes(request):
        request_data = json.loads(request.get_data())
        park_id = request_data['query']['park_id']
        obj_id = request_data['query']['object_id']
        fname = (
            'driver-work-rules_service_v1_changes_list_'
            f'{park_id}_{obj_id}.json'
        )
        return mockserver.make_response(json=RESPONSE_CACHE[fname])

    @mockserver.json_handler(
        '/persey-payments/internal/v1/charity/ride_donations', prefix=True,
    )
    def _get_ride_donations(request):
        return {'orders': [{'order_id': '777'}]}

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _parks_orders_list(request):
        doc = load_json('responses/driver_orders_found.json')
        doc_orders = doc.get('orders')

        orders_ids = set(
            request.json.get('query', {})
            .get('park', {})
            .get('order', {})
            .get('ids', []),
        )
        found = []
        for order in doc_orders:
            if order.get('id') in orders_ids:
                found.append(order)
        return {'orders': found}

    @mockserver.handler('/antifraud_refund-api/taxi/support')
    def _antifraud_refund(http_request):
        request_json = json.loads(http_request.get_data())
        response_cache = RESPONSE_CACHE['antifraud_refund.json']
        if request_json == response_cache['request']:
            return mockserver.make_response(json=response_cache['response'])
        empty_response = RESPONSE_CACHE['antifraud_refund_empty_response.json']
        return mockserver.make_response(json=empty_response)

    @mockserver.json_handler(
        '/passenger-feedback/passenger-feedback/v1/retrieve',
    )
    def _feedback_retrieve(http_request):
        return mockserver.make_response(
            json=RESPONSE_CACHE['feedback_retrieve.json'],
        )

    @mockserver.handler('/maas/internal/v1/get-maas-order-info')
    @staticmethod
    def _get_maas_order_info(request):
        order_id = json.loads(request.get_data())['order_id']
        if order_id == '0fc10c193bbb32fa97ea5fc7cca95455':
            maas_orders = RESPONSE_CACHE['maas_get_order_info.json']
            return mockserver.make_response(json=maas_orders)
        if order_id == '71a910a1bb274456bfe4946bd2bb8333':
            return mockserver.make_response(status=500)
        maas_orders = RESPONSE_CACHE['maas_get_order_info_empty.json']
        return mockserver.make_response(json=maas_orders, status=404)

    @mockserver.handler('/invoices-archive/v1/orders/get-order')
    def _invoices_archive_get_order(request):
        return mockserver.make_response(
            json={'code': 'no_such_order', 'message': 'no_such_order'},
            status=404,
        )

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-order',
    )
    def _order_core_get_order(request):
        body = RESPONSE_CACHE[
            'order_core_get_0fc10c193bbb32fa97ea5fc7cca95455.bson'
        ]
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(body),
        )

    class Mock:
        def __init__(self):
            self.invoices_archive_get_order: callinfo.AsyncCallQueue = (
                _invoices_archive_get_order
            )
            self.order_core_get_order: callinfo.AsyncCallQueue = (
                _order_core_get_order
            )

    return Mock()


@pytest.fixture
def mock_yt_simple(mockserver):
    """Mock lookup_rows with simple filtering"""

    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def _lookup_rows(request):
        request_data = json.loads(request.get_data())
        lookup_rule = request_data['replication_rule']['name']

        if lookup_rule == 'order_reports_sent':
            response_filename = 'archive-api_v1_yt_lookup_rows_reports.json'
        else:
            response_filename = 'archive-api_v1_yt_lookup_rows.json'

        all_rows = RESPONSE_CACHE[response_filename]
        order_id = request_data['query'][0]['id']
        rows = []
        for row in all_rows['items']:
            if row['id'] == order_id:
                rows.append(row)
        return {'items': rows}


@pytest.mark.parametrize(
    [
        'order_id',
        'locale',
        'countries_filter',
        'expected_status',
        'expected_filename',
    ],
    [
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            'ru',
            None,
            200,
            'admin_orders_v1_order_get_0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            'ru',
            'rus,blr',
            200,
            'admin_orders_v1_order_get_0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            'ru',
            'kaz,kgz',
            403,
            'admin_orders_v1_order_get_error',
        ),
        (
            'not_found_id',
            'ru',
            None,
            404,
            'admin_orders_v1_order_get_not_found',
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order(
        taxi_admin_orders_web,
        order_id,
        locale,
        countries_filter,
        expected_status,
        expected_filename,
):
    if countries_filter is None:
        url = f'/v1/order/get/{order_id}/'
    else:
        url = f'/v1/order/get/{order_id}/?countries_filter={countries_filter}'
    response = await taxi_admin_orders_web.post(
        url,
        headers={'Accept-Language': locale, 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['application_map_translation_config', 'expected_response'],
    [
        (
            {'android': {'tariff': 'unexisting_keyset'}},
            'admin_orders_v1_order_get_0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            {'android': {'tariff': 'tariff_vezet'}},
            'admin_orders_v1_order_get_0fc10c193bbb32fa97ea5fc7cca95455_vezet',
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order_map_translations(
        taxi_admin_orders_web,
        taxi_config,
        application_map_translation_config,
        expected_response,
):
    taxi_config.set_values(
        {'APPLICATION_MAP_TRANSLATIONS': application_map_translation_config},
    )

    order_id = '0fc10c193bbb32fa97ea5fc7cca95455'
    url = f'/v1/order/get/{order_id}/'

    response = await taxi_admin_orders_web.post(
        url, headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_response}.json']


@pytest.mark.parametrize(
    [
        'order_id',
        'locale',
        'countries_filter',
        'expected_status',
        'expected_filename',
    ],
    [
        (
            '71a910a1bb274456bfe4946bd2bb8333',
            'ru',
            None,
            200,
            'admin_orders_v1_order_get_71a910a1bb274456bfe4946bd2bb8333',
        ),
    ],
)
@pytest.mark.config(**CONFIGS_WITH_PASSENGER_FEEDBACK)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order_with_passenger_feedback(
        taxi_admin_orders_web,
        order_id,
        locale,
        countries_filter,
        expected_status,
        expected_filename,
        load_json,
        order_archive_mock,
        mockserver,
):
    @mockserver.handler('/archive-api/archive/', prefix=True)
    def _get_archive_order(request):
        doc = load_json(
            'responses/archive-api_archive_order_'
            '0fc10c193bbb32fa97ea5fc7cca95455.bson.json',
        )
        response = bson.BSON.encode(doc)
        return aiohttp.web.Response(
            body=response, headers={'Content-Type': 'application/bson'},
        )

    url = f'/v1/order/get/{order_id}/'
    response = await taxi_admin_orders_web.post(
        url,
        headers={'Accept-Language': locale, 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['order_id', 'locale', 'expected_status', 'expected_filename'],
    [
        (
            '0fc10c193bbb32fa97ea5fc7cca95455',
            'ru',
            200,
            'admin_orders_v1_order_get_0fc10c193bbb32fa97ea5fc7cca95455',
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.filldb(order_reports_sent='empty')
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order_ride_report_yt(
        taxi_admin_orders_web,
        order_id,
        locale,
        expected_status,
        expected_filename,
):
    response = await taxi_admin_orders_web.post(
        f'/v1/order/get/{order_id}/',
        headers={'Accept-Language': locale, 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content['user_info']['ride_report_sent'] is False
    # to compare with expected filename make it True
    # (otherwise we'd have to add a whole bunch of mocks for other order_id)
    content['user_info']['ride_report_sent'] = True
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['expected_taxi_staff'],
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                ADMIN_ORDERS_CONSIDER_TAXI_OUTSTAFF=False,
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(ADMIN_ORDERS_CONSIDER_TAXI_OUTSTAFF=True),
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order_taxi_outstaff(
        taxi_admin_orders_web, expected_taxi_staff,
):
    response = await taxi_admin_orders_web.post(
        f'/v1/order/get/0fc10c193bbb32fa97ea5fc7cca95455/',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()
    expected_content = RESPONSE_CACHE[
        'admin_orders_v1_order_get_0fc10c193bbb32fa97ea5fc7cca95455.json'
    ]
    expected_content['user_info']['taxi_staff'] = expected_taxi_staff
    assert content == expected_content


@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
@pytest.mark.parametrize(
    [
        'pp_resp_fname',
        'pp_fail',
        'expected_charity',
        'expected_pp_times_called',
    ],
    [
        ('responses/pp_resp_donation.json', False, 2.0, 1),
        ('responses/pp_resp_donation_pending.json', False, None, 1),
        ('responses/pp_resp_no_donation.json', False, None, 1),
        (None, True, None, 3),
    ],
)
async def test_charity(
        taxi_admin_orders_web,
        mockserver,
        load_json,
        pp_resp_fname,
        pp_fail,
        expected_charity,
        expected_pp_times_called,
):
    @mockserver.json_handler(
        '/persey-payments/internal/v1/charity/ride_donations', prefix=True,
    )
    def _get_ride_donations(request):
        if pp_fail:
            return mockserver.make_response(
                status=500, json={'code': 'code', 'message': 'message'},
            )

        return load_json(pp_resp_fname)

    response = await taxi_admin_orders_web.post(
        '/v1/order/get/0fc10c193bbb32fa97ea5fc7cca95455/',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )

    assert response.status == 200
    content = await response.json()
    assert content['payments_info'].get('charity') == expected_charity
    assert _get_ride_donations.times_called == expected_pp_times_called


@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_agent_order(taxi_admin_orders_web):
    response = await taxi_admin_orders_web.post(
        f'/v1/order/get/0fc10c193bbb32fa97ea5fc7cca95455/',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()
    assert (
        content['order_info']['agent']['agent_order_id']
        == '9aaa2f7671ca41e1a9a395a23fe7c199'
    )
    assert content['order_info']['agent']['agent_user_type'] == 'individual'


@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_calc_alternative_type(taxi_admin_orders_web):
    response = await taxi_admin_orders_web.post(
        f'/v1/order/get/0fc10c193bbb32fa97ea5fc7cca95455/',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()
    assert content['payments_info']['calc_alternative_type'] == 'combo_outer'


@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order_non_existent_insurer_id(
        taxi_admin_orders_web, mockserver,
):
    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def _lookup_rows(request):
        request_data = json.loads(request.get_data())

        response_filename = 'archive-api_v1_yt_lookup_rows.json'

        all_rows = RESPONSE_CACHE[response_filename]
        order_id = request_data['query'][0]['id']
        rows = []
        for row in all_rows['items']:
            if row['id'] == order_id:
                # main point of test
                row['insurer_id'] = 'non_existent_insurer_id'
                rows.append(row)
        return {'items': rows}

    response = await taxi_admin_orders_web.post(
        '/v1/order/get/0fc10c193bbb32fa97ea5fc7cca95455/',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()

    expected_content = RESPONSE_CACHE[
        f'admin_orders_v1_order_get_0fc10c193bbb32fa97ea5fc7cca95455.json'
    ]
    expected_content['user_info']['taxi_staff'] = False
    expected_content['order_info'].pop('insurance_export_date')
    expected_content['order_info'].pop('insurer')
    assert content == expected_content


@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
@pytest.mark.parametrize(
    'current_prices_patch, pricing_data_patch,'
    'expected_sp, expected_surge, expected_driver_surge,'
    'custom_round, order_proc',
    [
        (
            None,
            None,
            1.0,
            None,
            None,
            None,
            '0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            {},
            {'driver_meta': {}, 'user_meta': {}},
            1.0,
            {},
            {},
            None,
            '0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            {},
            {
                'driver_meta': {'setcar.show_surge': 1.2},
                'user_meta': {
                    'setcar.show_surge': 1.3,
                    'surge_delta': 30.0,
                    'synthetic_surge': 1.3,
                },
            },
            1.3,
            {
                'multiplier': 1.3,
                'display_str': '×1.3',
                'without_surge_price': 834.87,
                'surge_overpayment': 30.0,
            },
            {'multiplier': 1.2, 'display_str': '×1.2'},
            None,
            '0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            {},
            {
                'user_meta': {
                    'setcar.show_surcharge': 30.0,
                    'surge_delta': 30.0,
                    'synthetic_surge': 1.1,
                },
            },
            1.1,
            {
                'surcharge': 30.0,
                'display_str': '+30 ₽',
                'without_surge_price': 834.87,
                'surge_overpayment': 30.0,
            },
            {},
            None,
            '0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            {
                'user_final_cost': {'total': 222.0, 'without_surge': 190.0},
                'user_final_cost_meta': {
                    'setcar.show_surcharge': 30.0,
                    'synthetic_surge': 1.1,
                },
            },
            {'user_meta': {}},
            1.1,
            {
                'surcharge': 30.0,
                'display_str': '+30 ₽',
                'without_surge_price': 190.0,
                'surge_overpayment': 32.0,
            },
            {},
            None,
            '0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            {
                'user_final_cost': {
                    'total': 222.0,
                    'without_surge': 190.123456,
                },
                'user_final_cost_meta': {
                    'setcar.show_surcharge': 31.12345,
                    'synthetic_surge': 1.1,
                },
            },
            {'user_meta': {}},
            1.1,
            {
                'surcharge': 31.12345,
                'display_str': '+31.12345 ₽',
                'without_surge_price': 190.123456,
                'surge_overpayment': 31.87654,
            },
            {},
            5,
            '0fc10c193bbb32fa97ea5fc7cca95455',
        ),
        (
            None,
            None,
            1.53511259382819,
            {
                'display_str': '×1.5',
                'without_surge_price': 1.5,
                'multiplier': 1.5,
                'surge_overpayment': 0.8,
            },
            {'display_str': '×1.5', 'multiplier': 1.5},
            2,
            'dfce8351eab91322a92735d5a684d2da',
        ),
    ],
    ids=[
        'order_without_pricing_data',
        'no_surge_metadata',
        'show_surge',
        'show_surcharge',
        'without_surge_price_from_final_cost',
        'surge_with_round',
        'from_real_order',
    ],
)
async def test_get_order_using_pricing_data(
        taxi_admin_orders_web,
        order_archive_mock,
        load_json,
        current_prices_patch,
        pricing_data_patch,
        expected_sp,
        expected_surge,
        expected_driver_surge,
        custom_round,
        order_proc,
):
    order_proc_patch = {}
    if current_prices_patch:
        order_proc_patch['current_prices'] = load_json(
            'current_prices_object.json',
            object_hook=helpers.VarHook(current_prices_patch),
        )
    if pricing_data_patch:
        order_proc_patch['pricing_data'] = load_json(
            'pricing_data_object.json',
            object_hook=helpers.VarHook(pricing_data_patch),
        )
        if custom_round is not None:
            order_proc_patch['pricing_data']['currency'][
                'fraction_digits'
            ] = custom_round

    order_archive_mock.set_order_proc(
        load_json(
            'order_archive-order_proc-retrieve.json',
            object_hook=helpers.VarHook(order_proc_patch),
        ),
    )

    response = await taxi_admin_orders_web.post(
        '/v1/order/get/' + order_proc + '/',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()

    payments_info = content['payments_info']
    assert payments_info['sp'] == expected_sp

    if expected_surge is None:
        assert 'surge' not in payments_info
    else:
        assert payments_info['surge'] == expected_surge

    decoupling = content.get('decoupling', {})
    if expected_driver_surge is None:
        assert 'driver_surge' not in decoupling
    else:
        assert decoupling['driver_surge'] == expected_driver_surge


@pytest.mark.parametrize(
    ['order_id', 'expected_filename'],
    [
        (
            '4d5de9e9500c4ed2a3a96128f0427115',
            'admin_orders_v1_order_get_4d5de9e9500c4ed2a3a96128f0427115',
        ),
    ],
)
@pytest.mark.config(**CONFIGS_WITH_PASSENGER_FEEDBACK)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order_archive_api(
        taxi_admin_orders_web,
        order_id,
        expected_filename,
        load_json,
        order_archive_mock,
        mockserver,
):
    @mockserver.handler('/archive-api/archive/', prefix=True)
    def _get_archive_order(request):
        doc = load_json(f'responses/order_{order_id}.bson.json')
        response = bson.BSON.encode(doc)
        return aiohttp.web.Response(
            body=response, headers={'Content-Type': 'application/bson'},
        )

    url = f'/v1/order/get/{order_id}/'
    response = await taxi_admin_orders_web.post(
        url, headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == RESPONSE_CACHE[f'{expected_filename}.json']


@pytest.mark.parametrize(
    ['expected'],
    [
        pytest.param(
            {},
            marks=pytest.mark.config(
                LONG_TRIP_CRITERIA={
                    '__default__': {
                        '__default__': {
                            'apply': 'either',
                            'distance': 25000,
                            'duration': 2400,
                        },
                    },
                },
            ),
        ),
        pytest.param(
            {'distance': 600, 'duration': 2400},
            marks=pytest.mark.config(
                LONG_TRIP_CRITERIA={
                    '__default__': {
                        '__default__': {
                            'apply': 'either',
                            'distance': 600,
                            'duration': 2400,
                        },
                    },
                },
            ),
        ),
        pytest.param(
            {},
            marks=pytest.mark.config(
                LONG_TRIP_CRITERIA={
                    '__default__': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 600,
                            'duration': 2400,
                        },
                    },
                },
            ),
        ),
        pytest.param(
            {'distance': 600, 'duration': 120},
            marks=pytest.mark.config(
                LONG_TRIP_CRITERIA={
                    '__default__': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 600,
                            'duration': 120,
                        },
                    },
                },
            ),
        ),
        pytest.param(
            {'distance': 600, 'duration': 120},
            marks=pytest.mark.config(
                LONG_TRIP_CRITERIA={
                    '__default__': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 600,
                            'duration': 120,
                        },
                    },
                    'msk': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 550,
                            'duration': 110,
                        },
                    },
                },
            ),
        ),
        pytest.param(
            {'distance': 550, 'duration': 110},
            marks=pytest.mark.config(
                LONG_TRIP_CRITERIA={
                    '__default__': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 600,
                            'duration': 120,
                        },
                    },
                    'ekb': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 550,
                            'duration': 110,
                        },
                    },
                },
            ),
        ),
        pytest.param(
            {'distance': 400, 'duration': 90},
            marks=pytest.mark.config(
                LONG_TRIP_CRITERIA={
                    '__default__': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 600,
                            'duration': 120,
                        },
                    },
                    'ekb': {
                        '__default__': {
                            'apply': 'both',
                            'distance': 550,
                            'duration': 110,
                        },
                        'econom': {
                            'apply': 'both',
                            'distance': 400,
                            'duration': 90,
                        },
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.usefixtures('taxi_admin_orders_mocks', 'mock_yt_simple')
async def test_get_order_long_trip(taxi_admin_orders_web, expected):
    response = await taxi_admin_orders_web.post(
        '/v1/order/get/0fc10c193bbb32fa97ea5fc7cca95455/',
        headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )

    assert response.status == 200
    content = await response.json()

    if not expected:
        assert 'long_trip' not in content['order_info']
    else:
        assert 'long_trip' in content['order_info']
        assert expected == content['order_info'].get('long_trip')


# pylint: disable=redefined-outer-name
@pytest.mark.parametrize('deanonymize', [True, False])
@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
async def test_get_order_anonymized(
        taxi_admin_orders_web,
        mockserver,
        mock_yt_simple,
        taxi_admin_orders_mocks,
        deanonymize,
):

    order_id = '0fc10c193bbb32fa97ea5fc7cca95455'

    @mockserver.json_handler('/replication/map_data')
    def _map_data(request):
        doc = RESPONSE_CACHE['replication_map_data_with_takeout.json']
        return doc

    url = f'/v1/order/get/{order_id}/?deanonymize={deanonymize}'
    headers = {'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'}
    response = await taxi_admin_orders_web.post(url, headers=headers)
    assert response.status == 200
    assert _map_data.has_calls
    if deanonymize:
        assert taxi_admin_orders_mocks.invoices_archive_get_order.has_calls
        assert taxi_admin_orders_mocks.order_core_get_order.has_calls

    assert response.status == 200
    content = await response.json()
    assert content.get('takeout', {}) == {
        'status': 'anonymized',
        'deleted': '2020-03-23T20:15:28.658000+03:00',
    }


@pytest.mark.config(**CONFIGS)
@pytest.mark.translations(**TRANSLATIONS)
async def test_get_order_with_family(
        taxi_admin_orders_web,
        mockserver,
        mock_yt_simple,
        taxi_admin_orders_mocks,
):
    order_id = '0fc10c193bbb32fa97ea5fc7cca95455'

    @mockserver.json_handler('/replication/map_data')
    def _map_data(request):
        doc = RESPONSE_CACHE['replication_map_data_with_family.json']
        return doc

    url = f'/v1/order/get/{order_id}/'
    response = await taxi_admin_orders_web.post(
        url, headers={'Accept-Language': 'ru', 'X-Yandex-Login': 'simpleman'},
    )
    assert response.status == 200
    content = await response.json()
    assert 'family' in content.get('payments_info')
