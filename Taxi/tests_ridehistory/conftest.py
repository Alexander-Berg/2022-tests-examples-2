# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=import-error
# pylint: disable=too-many-lines
import datetime as dt

import pytest
import pytz
from ridehistory_plugins import *  # noqa: F403 F401

from tests_plugins import json_util

from tests_ridehistory import common


@pytest.fixture
def mock_yt_queries(mockserver, load_json):
    def _impl(queries_fname, *, override_tariff=None):
        load_json_object_hook = None
        if override_tariff is not None:
            load_json_object_hook = common.kv_updater_hook(
                {'order.tariff_class': override_tariff},
            )

        if queries_fname is None:
            queries = {}
        else:
            raw_queries = load_json(f'{queries_fname}.json')
            queries = {}
            for query_template, format_kwargs, result_fname in raw_queries:
                if format_kwargs is None:
                    queries[query_template] = result_fname
                else:
                    for query in common.prepare_queries(
                            query_template, format_kwargs,
                    ):
                        queries[query] = result_fname

        @mockserver.json_handler('/archive-api/v1/yt/select_rows')
        def _mock_archive_api(request):
            query_string = request.json['query']['query_string']
            fname = queries.get(query_string)
            assert fname is not None, query_string
            return {
                'source': 'source',
                'items': load_json(
                    f'{fname}.json', object_hook=load_json_object_hook,
                ),
            }

        return _mock_archive_api

    return _impl


@pytest.fixture
def mock_yt_queries_empty(mockserver):
    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    def _mock_archive_api(request):
        return {'source': 'source', 'items': []}


@pytest.fixture
def mock_zones_v2_empty(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones_v2(request):
        common.check_headers(request.headers)
        return {'zones': [], 'notification_params': {}}


@pytest.fixture
def mock_yamaps_default(mockserver, load_json, yamaps):
    translations = load_json('localizeaddress_config.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        rtranslations = translations[request.args['lang']]
        yamaps_vars = None
        if 'uri' in request.args:
            yamaps_vars = rtranslations['uri'][request.args['uri']]
        elif 'll' in request.args and 'text' in request.args:
            if request.args['text'] == request.args['ll']:
                yamaps_vars = {
                    'full_text': 'Should be ignored',
                    'point': request.args['ll'],
                }
            else:
                yamaps_vars = rtranslations['text'][request.args['text']]
        else:
            assert None, 'Bad request'
        assert yamaps_vars
        return [
            load_json(
                'yamaps_response_default.json',
                object_hook=json_util.VarHook(yamaps_vars),
            ),
        ]


LIST_ORDER_CORE_QUERY_PROJECTION = [
    'performer.driver_id',
    'performer.presetcar',
    'performer.candidate_index',
    'candidates.tariff_class',
    'candidates.tariff_currency',
    'candidates.transport.type',
    'candidates.car_color',
    'candidates.car_color_code',
    'candidates.car_model',
    'candidates.car_number',
    'candidates.db_id',
    'order.cost',
    'order.nz',
    'order.status',
    'order.taxi_status',
    'order.application',
    'order.coupon.was_used',
    'order.coupon.value',
    'order.current_prices.user_ride_display_price',
    'order.current_prices.cashback_price',
    'order.current_prices.discount_cashback',
    'order.request.cargo_ref_id',
    'order.request.due',
    'order.request.source.fullname',
    'order.request.source.short_text',
    'order.request.source.uris',
    'order.request.source.type',
    'order.request.source.geopoint',
    'order.request.destinations.fullname',
    'order.request.destinations.short_text',
    'order.request.destinations.uris',
    'order.request.destinations.type',
    'order.request.destinations.geopoint',
    'order.user_locale',
    'order.user_uid',
    'order.user_phone_id',
    'order.status_updated',
    'payment_tech.type',
    'order_info.statistics.status_updates',
]

ITEM_ORDER_CORE_QUERY_PROJECTION = LIST_ORDER_CORE_QUERY_PROJECTION + [
    'candidates.alias_id',
    'payment_tech.main_card_payment_id',
    'order.performer.carrier',
    'order.performer.tin',
    'order.request.sp',
    'order.cargo_billing.park_traits.has_cargo_service',
]


@pytest.fixture
def mock_order_core_query(mockserver, load_json):
    def _impl(
            order_ids,
            responses_fname,
            is_item_view,
            patch_orders=None,
            *,
            override_tariff=None,
    ):
        load_json_object_hook = None
        if override_tariff is not None:
            load_json_object_hook = common.kv_updater_hook(
                {'tariff_class': override_tariff},
            )

        responses = {
            order['_id']: order
            for order in load_json(
                f'{responses_fname}.json', object_hook=load_json_object_hook,
            )
        }

        if patch_orders:
            for order_id, patch in patch_orders.items():
                for path, value in patch.items():
                    order = responses[order_id]
                    keys = path.split('.')
                    for key in keys[:-1]:
                        order = order[key]
                    order[keys[-1]] = value

        @mockserver.json_handler('/order-core/v1/tc/order-fields')
        def _mock_order_proc(request):
            order_id = request.json['order_id']

            if is_item_view:
                query_projection = ITEM_ORDER_CORE_QUERY_PROJECTION
            else:
                query_projection = LIST_ORDER_CORE_QUERY_PROJECTION

            assert set(request.json['fields']) == set(query_projection)
            if order_id in order_ids:
                return {
                    'fields': responses[order_id],
                    'order_id': order_id,
                    'replica': 'master',
                    'version': '777',
                }

            return mockserver.make_response(
                json={'code': 'not found', 'message': 'not found'}, status=404,
            )

        return _mock_order_proc

    return _impl


@pytest.fixture
def mock_order_core_heartbeat(mockserver):
    def _impl(orders):
        @mockserver.handler('/order-core/v1/tc/order-fields')
        def _mock_order_proc(request):
            order_id = request.json['order_id']

            assert request.json['fields'] == ['_id']
            assert order_id in orders

            status = orders[order_id]

            if status == 200:
                response = mockserver.make_response(
                    json={
                        'fields': {'_id': order_id},
                        'order_id': order_id,
                        'replica': 'master',
                        'version': '777',
                    },
                    status=200,
                )
            elif status == 404:
                response = mockserver.make_response(
                    json={'code': 'not found', 'message': 'not found'},
                    status=404,
                )
            else:
                response = mockserver.make_response(
                    json={'code': 'error', 'message': 'error'}, status=500,
                )

            return response

        return _mock_order_proc

    return _impl


@pytest.fixture
def mock_transactions_query(mockserver, load_json):
    def _impl(order_ids, responses_fname):
        responses = {
            order['_id']: order
            for order in load_json(f'{responses_fname}.json')
        }

        @mockserver.json_handler('/transactions/v2/invoice/retrieve')
        def _mock_v2_invoice_retrieve(request):
            order_id = request.json['id']

            assert order_id in order_ids

            doc = responses[order_id]

            invoice_tech = doc.get('invoice_payment_tech')
            if invoice_tech:
                sum_to_pay = invoice_tech['items_by_payment_type']
                payment_types = [
                    payment['type'] for payment in invoice_tech['payments']
                ]
            else:
                payment_type = doc['payment_tech'].get('type')
                payment_types = [payment_type]
                sum_to_pay = [
                    {
                        'payment_type': payment_type,
                        'items': [
                            {'item_id': item_id, 'amount': str(amount)}
                            for item_id, amount in doc['payment_tech'][
                                'sum_to_pay'
                            ].items()
                        ],
                    },
                ]

            return {
                'id': order_id,
                'invoice_due': doc['request']['due'],
                'created': doc['request']['due'],
                'currency': doc['performer']['tariff']['currency'],
                'status': 'cleared',
                'operation_info': {},
                'sum_to_pay': sum_to_pay,
                'held': doc.get('held', []),
                'cleared': doc.get('cleared', []),
                'debt': [],
                'transactions': [],
                'yandex_uid': doc['order']['user_uid'],
                'payment_types': payment_types,
                'cashback': doc.get('cashback'),
            }

        return _mock_v2_invoice_retrieve

    return _impl


@pytest.fixture
def mock_taxi_tariffs_query(mockserver, load_json):
    def _impl(allowed_zones, legal_entities_enabled=None, error=False):
        zone_infos = load_json('taxi_tariffs_config.json')

        @mockserver.json_handler(
            '/taxi-tariffs/v1/tariff_settings/bulk_retrieve',
        )
        def _mock_taxi_tariffs(request):
            if error:
                return mockserver.make_response(status=500)

            zones = []

            for zone_name in request.args['zone_names'].split(','):
                assert zone_name in allowed_zones
                assert zone_name in zone_infos

                zone_info = zone_infos[zone_name]

                categories = []
                for category_data in zone_info['categories']:
                    category = {
                        'service_levels': [],
                        'is_default': False,
                        'can_be_default': False,
                        'client_constraints': [],
                        'only_for_soon_orders': False,
                        'persistent_requirements': [],
                        'client_requirements': [],
                    }
                    if legal_entities_enabled is not None:
                        category[
                            'legal_entities_enabled'
                        ] = legal_entities_enabled

                    category.update(category_data)
                    categories.append(category)

                zones.append(
                    {
                        'zone': zone_name,
                        'tariff_settings': {
                            'timezone': zone_info['timezone'],
                            'categories': categories,
                            'country': zone_info['country'],
                        },
                    },
                )

            return {'zones': zones}

        return _mock_taxi_tariffs

    return _impl


@pytest.fixture
def get_table_ids(pgsql):
    db = pgsql['ridehistory']

    def _impl(table):
        cursor = db.cursor()
        cursor.execute(f'SELECT order_id FROM ridehistory.{table}')
        return {row[0] for row in cursor}

    return _impl


@pytest.fixture
def get_hidden_data(pgsql):
    db = pgsql['ridehistory']

    def _impl():
        data = {}

        cursor = db.cursor()
        cursor.execute(
            'SELECT order_id, is_hidden FROM ridehistory.user_index',
        )
        data['user_index'] = {row[0]: row[1] for row in cursor}

        cursor = db.cursor()
        cursor.execute(
            'SELECT order_id, phone_id, user_uid, payment_tech_type, '
            'payment_method_id, order_created_at, created_at '
            'FROM ridehistory.hidden_orders',
        )
        data['hidden_orders'] = {
            row[0]: dict(
                zip(
                    [
                        'order_id',
                        'phone_id',
                        'user_uid',
                        'payment_tech_type',
                        'payment_method_id',
                        'order_created_at',
                        'created_at',
                    ],
                    row,
                ),
            )
            for row in cursor
        }

        return data

    return _impl


@pytest.fixture
def get_user_index_rows(pgsql):
    def _impl():
        db = pgsql['ridehistory']

        cursor = db.cursor()
        cursor.execute(
            'SELECT order_id, phone_id, user_uid, order_created_at, '
            'seen_unarchived_at, is_hidden, payment_tech_type, '
            'payment_method_id FROM ridehistory.user_index',
        )

        entries = []

        for entry in map(list, cursor):
            for i, item in enumerate(entry):
                if isinstance(item, dt.datetime):
                    entry[i] = item.astimezone(pytz.UTC)

            entries.append(entry)

        return entries

    return _impl


DRIVER_PROFILES_PROJECTION = [
    'data.full_name.first_name',
    'data.full_name.middle_name',
    'data.full_name.last_name',
    'data.phone_pd_ids',
]


def _get_keys(doc):
    if not isinstance(doc, dict) or not doc:
        return None

    result = []

    for key, value in doc.items():
        suffixes = _get_keys(value)

        if suffixes is None:
            result.append(key)
        else:
            result.extend([f'{key}.{suffix}' for suffix in suffixes])

    return result


@pytest.fixture
def mock_driver_profiles(mockserver, load_json):
    def _impl(fname):
        drivers = {
            item['park_driver_profile_id']: item for item in load_json(fname)
        }
        for driver in drivers.values():
            assert {
                k for k in _get_keys(driver) if k.startswith('data')
            }.issubset(set(DRIVER_PROFILES_PROJECTION))

        @mockserver.json_handler(
            '/driver-profiles/v1/driver/profiles/retrieve',
        )
        def _handle(request):
            assert request.query['consumer'] == 'ridehistory'
            assert request.json['projection'] == DRIVER_PROFILES_PROJECTION

            return {
                'profiles': [
                    drivers[driver_id]
                    for driver_id in request.json['id_in_set']
                    if driver_id in drivers
                ],
            }

        return _handle

    return _impl


@pytest.fixture(autouse=True)
def mock_driver_profiles_error(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _handle(request):
        return mockserver.make_response(status=500)


LIST_PARKS_REPLICA_QUERY_PROJECTION = ['data.phone_pd_id']
ITEM_PARKS_REPLICA_QUERY_PROJECTION = LIST_PARKS_REPLICA_QUERY_PROJECTION + [
    'data.name',
    'data.legal_address',
    'data.long_name',
    'data.ogrn',
    'data.legal_log',
]


@pytest.fixture
def mock_parks_replica(mockserver, load_json):
    def _impl(fname, is_item_view, error=False):
        parks = {item['park_id']: item for item in load_json(fname)}

        @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
        def _handle(request):
            assert request.query['consumer'] == 'ridehistory'

            if error:
                return mockserver.make_response(status=500)

            if is_item_view:
                assert (
                    request.json['projection']
                    == ITEM_PARKS_REPLICA_QUERY_PROJECTION
                )
            else:
                assert (
                    request.json['projection']
                    == LIST_PARKS_REPLICA_QUERY_PROJECTION
                )

            return {
                'parks': [
                    parks[park_id]
                    for park_id in request.json['id_in_set']
                    if park_id in parks
                ],
            }

        return _handle

    return _impl


@pytest.fixture(autouse=True)
def mock_parks_replica_error(mockserver):
    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_personal_phones(mockserver, load_json):
    def _impl(fname):
        phones = load_json(fname)

        @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
        def _handle(request):
            return {
                'items': [
                    {'id': item['id'], 'value': phones[item['id']]}
                    for item in request.json['items']
                ],
            }

        return _handle

    return _impl


@pytest.fixture(autouse=True)
def mock_personal_phones_error(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_personal_tins(mockserver):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def _handle(request):
        return {'id': request.json['id'], 'value': '550012341234'}


@pytest.fixture(autouse=True)
def mock_personal_tins_error(mockserver):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_selfemployed(mockserver):
    @mockserver.json_handler('/selfemployed-fns-replica/v1/profiles/retrieve')
    def _handle(request):
        return {
            'profiles': [
                {
                    'park_contractor_profile_id': 'inn_pd_id',
                    'data': {
                        'is_own_park': False,
                        'do_send_receipts': True,
                        'inn_pd_id': 'inn_pd_id',
                    },
                },
            ],
        }


@pytest.fixture(autouse=True)
def mock_selfemployed_error(mockserver):
    @mockserver.json_handler('/selfemployed-fns-replica/v1/profiles/retrieve')
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_cardstorage(mockserver, load_json):
    def _impl(yandex_uid, card_id, response_fname, error=False):
        @mockserver.json_handler('/cardstorage/v1/card')
        def _mock_cardstorage(request):
            if error:
                return mockserver.make_response(status=500)

            assert request.json['yandex_uid'] == yandex_uid
            assert request.json['card_id'] == card_id

            return load_json(response_fname)

        return _mock_cardstorage

    return _impl


@pytest.fixture(autouse=True)
def mock_cardstorage_error(mockserver):
    @mockserver.json_handler('/cardstorage/v1/card')
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_shared_payments(mockserver, load_json):
    def _impl(account_id, locale, response_json, error=False):
        @mockserver.json_handler(
            '/taxi-shared-payments/internal/coop_account/history_info',
        )
        def _mock_shared_payments(request):
            if error:
                return mockserver.make_response(status=500)

            assert request.headers['X-Request-Language'] == locale
            assert request.query['account_id'] == account_id

            return response_json

        return _mock_shared_payments

    return _impl


@pytest.fixture(autouse=True)
def mock_shared_payments_error(mockserver):
    @mockserver.json_handler(
        '/taxi-shared-payments/internal/coop_account/history_info',
    )
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_unique_drivers(mockserver, load_json):
    def _impl(expected_park_driver_profile_id, response_json, error=False):
        @mockserver.json_handler(
            '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
        )
        def _handle(request):
            if error:
                return mockserver.make_response(status=500)

            assert request.query['consumer'] == 'ridehistory'
            assert request.json == {
                'profile_id_in_set': [expected_park_driver_profile_id],
            }

            return response_json

        return _handle

    return _impl


@pytest.fixture(autouse=True)
def mock_unique_drivers_error(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_driver_ratings(mockserver, load_json):
    def _impl(expected_unique_driver_id, driver_ratings_resp, error=False):
        @mockserver.json_handler('/driver-ratings/v2/driver/rating')
        def _handle(request):
            if error:
                return mockserver.make_response(status=500)

            assert request.headers['X-Ya-Service-Name'] == 'ridehistory'
            assert (
                request.query['unique_driver_id'] == expected_unique_driver_id
            )

            return {
                'unique_driver_id': request.query['unique_driver_id'],
                'rating': driver_ratings_resp,
            }

        return _handle

    return _impl


@pytest.fixture(autouse=True)
def mock_driver_ratings_error(mockserver):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture(autouse=True)
def mock_admin_images(mockserver, load_json):
    @mockserver.json_handler('/admin-images/internal/list')
    def _mock_internal_list(request):
        return load_json('admin_images_list.json')


@pytest.fixture(autouse=True)
def mock_admin_images_custom(mockserver, load_json):
    def _impl(fname):
        @mockserver.json_handler('/admin-images/internal/list')
        def _mock_internal_list(request):
            return load_json(fname)

    return _impl


@pytest.fixture(autouse=True)
def mock_persey_payments_error(mockserver):
    @mockserver.json_handler(
        '/persey-payments/internal/v1/charity/ride_donations', prefix=True,
    )
    def _handle(request):
        return mockserver.make_response(
            status=500, json={'code': 'code', 'message': 'message'},
        )


@pytest.fixture
def mock_persey_payments(mockserver, load_json):
    def _impl(expected_order_ids, response_json):
        @mockserver.json_handler(
            '/persey-payments/internal/v1/charity/ride_donations', prefix=True,
        )
        def _handle(request):
            assert set(request.query['order_ids'].split(',')) == set(
                expected_order_ids,
            )

            return load_json(response_json)

        return _handle

    return _impl


@pytest.fixture
def check_pg_queries(testpoint, load_json):
    def _impl(expected_queries_fname):
        expected_queries = load_json(expected_queries_fname)

        @testpoint('orders_query')
        def orders_tp(data):
            assert data['query'] == expected_queries['orders']

        @testpoint('hidden_orders_query')
        def hidden_orders_tp(data):
            assert data['query'] == expected_queries['hidden_orders']

        return {'orders': orders_tp, 'hidden_orders': hidden_orders_tp}

    return _impl


@pytest.fixture
def check_pg_tp_times_called(testpoint):
    def _impl(tps):
        assert tps['orders'].times_called == 1
        assert tps['hidden_orders'].times_called == 1

    return _impl


@pytest.fixture
def check_response(load_json):
    def _impl(response, exp_resp, need_item_view):
        if isinstance(exp_resp, str):
            exp_resp = load_json(exp_resp)

        assert set(response.json().keys()) == set(exp_resp.keys())

        for key, data in response.json().items():
            if key == 'orders':
                response_orders = (
                    list(map(common.item_view_to_list_view, data))
                    if need_item_view
                    else data
                )
                assert response_orders == exp_resp['orders']
            else:
                assert data == exp_resp[key]

    return _impl


@pytest.fixture(autouse=True)
def mock_driver_trackstory_error(mockserver):
    @mockserver.json_handler('/driver-trackstory/get_track')
    def _handle(request):
        return mockserver.make_response(
            status=500, json={'code': 'code', 'message': 'message'},
        )


@pytest.fixture
def mock_driver_trackstory(mockserver, load_json):
    def _impl(expected_req_fname, response_fname):
        @mockserver.json_handler('/driver-trackstory/get_track')
        def _handle(request):
            assert request.json == load_json(expected_req_fname)

            return load_json(response_fname)

        return _handle

    return _impl


@pytest.fixture
def mock_territories(mockserver):
    def _impl(carrier_enabled, error=False):
        @mockserver.json_handler('/territories/v1/countries/list')
        def _handle(request):
            if error:
                return {'countries': []}

            return {
                'countries': [
                    {
                        '_id': country,
                        'carrier_enabled': carrier_enabled,
                        'code2': 'RU',
                        'phone_code': '1',
                        'phone_min_length': 5,
                        'phone_max_length': 5,
                        'national_access_code': '123',
                        'region_id': 1,
                    }
                    for country in ['kgz', 'mda', 'rus']
                ],
            }

        return _handle

    return _impl


@pytest.fixture(autouse=True)
def mock_territories_empty(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _handle(request):
        return {'countries': []}


@pytest.fixture(autouse=True)
def mock_yb_trust_payments_empty(mockserver):
    @mockserver.json_handler('/yb-trust-payments/order', prefix=True)
    def _handle(request):
        return []


@pytest.fixture
def mock_yb_trust_payments(mockserver, load_json):
    def _impl(expected_order_id, resp_fname, error=False):
        @mockserver.json_handler('/yb-trust-payments/order', prefix=True)
        def _handle(request):
            order_id = request.path.split('/')[3]
            assert order_id == expected_order_id

            if error:
                return mockserver.make_response(
                    status=500, json={'code': 'code', 'message': 'message'},
                )

            return load_json(resp_fname)

        return _handle

    return _impl


@pytest.fixture
def mock_receipt_fetching(mockserver, load_json):
    def _impl(expected_order_id, resp_fname, error=False):
        @mockserver.json_handler('/taxi-receipt-fetching/receipts')
        def _handle(request):
            assert request.json['order_ids'] == [expected_order_id]

            if error:
                return mockserver.make_response(
                    status=500, json={'code': 'code', 'message': 'message'},
                )

            return load_json(resp_fname)

        return _handle

    return _impl


@pytest.fixture(autouse=True)
def mock_udriver_photos_error(mockserver):
    @mockserver.json_handler(
        '/udriver-photos/driver-photos/v1/photo', prefix=True,
    )
    def _handle(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_udriver_photos(mockserver):
    def _impl(exp_park_driver_profile_ids):
        @mockserver.json_handler(
            '/udriver-photos/driver-photos/v1/photo', prefix=True,
        )
        def _handle(request):
            assert request.query.get('unique_driver_id') is None
            assert (
                request.query['park_id'],
                request.query['driver_profile_id'],
            ) in exp_park_driver_profile_ids
            assert request.query['moderated_only'] == 'true'

            return {
                'actual_photo': {
                    'portrait_url': 'portrait_url',
                    'avatar_url': 'avatar_url',
                },
            }

        return _handle

    return _impl


@pytest.fixture
def mock_eulas_freightage(mockserver):
    def _impl(return_contract=True, **kwargs):
        @mockserver.json_handler('/eulas/internal/eulas/v1/freightage')
        def _handle(request):
            assert request.json['order_id'] == kwargs['order_id']
            assert request.json['format_currency'] == kwargs['format_currency']
            assert request.json['search_archive'] is True
            if not return_contract:
                return {}
            return {
                'contract': {
                    'title': 'test_title',
                    'contract_data': [
                        {
                            'item_type': 'string',
                            'name': 'test_name',
                            'value': 'test_value',
                        },
                    ],
                },
            }

        return _handle

    return _impl


@pytest.fixture()
def eulas_freightage_error_mock(mockserver):
    @mockserver.json_handler(
        '/eulas/internal/eulas/v1/freightage', prefix=True,
    )
    def _handle(request):
        return mockserver.make_response(status=500)

    return _handle
