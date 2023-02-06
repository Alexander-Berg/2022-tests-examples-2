# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import collections
import copy
import datetime
import json
import operator
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

import psycopg2.extras
import pytest
import pytz

from eats_eta_plugins import *  # noqa: F403 F401

from . import utils
from .eta_testcases import *  # noqa: F403 F401


def pytest_configure(config):
    config.addinivalue_line('markers', 'redis_testcase')
    config.addinivalue_line('markers', 'update_mode')


@pytest.fixture(name='now_utc')
def _now_utc(mocked_time):
    return mocked_time.now().replace(tzinfo=pytz.utc)


Order = Dict[str, Any]
Composite = Optional[Union[dict, tuple]]


def _make_currency(currency: Composite) -> Optional[tuple]:
    if isinstance(currency, dict):
        currency = currency['sign'], currency['code']
    return currency


def _make_interval(
        interval: Optional[Union[int, datetime.timedelta]],
) -> Optional[datetime.timedelta]:
    if isinstance(interval, int):
        interval = datetime.timedelta(seconds=interval)
    return interval


def _make_timepoint(
        timepoint: Optional[Union[str, datetime.datetime]],
) -> Optional[datetime.datetime]:
    if isinstance(timepoint, str):
        timepoint = utils.parse_datetime(timepoint)
    return timepoint


@pytest.fixture(name='make_order')
def _make_order(now_utc):
    def make_order(**kwargs) -> Order:
        order = {
            'id': 1,
            'order_nr': 'order_nr-1',
            'eater_id': 'eater_id-1',
            'eater_personal_phone_id': 'eater_personal_phone_id-1',
            'eater_passport_uid': None,
            'device_id': None,
            'place_id': 1,
            'order_status': 'created',
            'picking_status': None,
            'picking_flow_type': None,
            'picking_duration': None,
            'order_type': 'native',
            'delivery_type': 'native',
            'shipping_type': 'delivery',
            'delivery_coordinates': None,
            'delivery_zone_courier_type': None,
            'cooking_time': None,
            'delivery_time': None,
            'total_time': None,
            'ml_provider': None,
            'claim_id': None,
            'claim_created_at': None,
            'pickup_arrived_at': None,
            'delivery_arrived_at': None,
            'claim_status': None,
            'place_point_id': None,
            'customer_point_id': None,
            'place_visit_order': None,
            'customer_visit_order': None,
            'place_visited_at': None,
            'customer_visited_at': None,
            'place_visit_status': None,
            'customer_visit_status': None,
            'place_cargo_waiting_time': None,
            'customer_cargo_waiting_time': None,
            'place_point_eta_updated_at': None,
            'customer_point_eta_updated_at': None,
            'courier_position': None,
            'courier_speed': None,
            'courier_direction': None,
            'courier_transport_type': None,
            'courier_position_updated_at': None,
            'created_at': now_utc,
            'status_changed_at': None,
            'delivery_started_at': None,
            'picking_starts_at': None,
            'retail_order_created_at': None,
            'picking_duration_updated_at': None,
            'picking_start_updated_at': None,
            'corp_client_type': None,
            'batch_info': None,
            'batch_info_updated_at': None,
            'picking_slot_started_at': None,
            'picking_slot_finished_at': None,
            'delivery_date': None,
            'delivery_slot_started_at': None,
            'delivery_slot_finished_at': None,
            'promised_at': '2022-03-03T19:30:00+03:00',
            'park_id': None,
            'driver_id': None,
            'segment_pickuped_time': None,
            'chained_orders': None,
        }
        for key in kwargs:
            assert key in order
        order.update(kwargs)
        for key in (
                'picking_duration',
                'cooking_time',
                'delivery_time',
                'total_time',
                'place_cargo_waiting_time',
                'customer_cargo_waiting_time',
        ):
            order[key] = _make_interval(order[key])
        for key in (
                'place_visited_at',
                'customer_visited_at',
                'place_point_eta_updated_at',
                'customer_point_eta_updated_at',
                'courier_position_updated_at',
                'created_at',
                'status_changed_at',
                'delivery_started_at',
                'picking_starts_at',
                'retail_order_created_at',
                'picking_duration_updated_at',
                'picking_start_updated_at',
                'batch_info_updated_at',
                'picking_slot_started_at',
                'picking_slot_finished_at',
                'delivery_date',
                'delivery_slot_started_at',
                'delivery_slot_finished_at',
                'promised_at',
        ):
            order[key] = _make_timepoint(order[key])
        if order['status_changed_at'] is None:
            order['status_changed_at'] = order['created_at']
        return order

    return make_order


@pytest.fixture(name='db_orders_fields')
def _db_orders_fields(make_order) -> Set[str]:
    return set(make_order().keys())


@pytest.fixture(name='db_get_cursor')
def _db_get_cursor(pgsql):
    def create_cursor():
        cursor = pgsql['eats_eta'].dict_cursor()
        psycopg2.extras.register_composite('eats_eta.currency', cursor)
        return cursor

    return create_cursor


@pytest.fixture(name='check_redis_value')
def _check_redis_value(redis_store):
    def do_check_redis_value(
            order_nr,
            key,
            value,
            # pylint: disable=dangerous-default-value
            redis_keys_ttl=utils.REDIS_KEYS_TTL,
            ttl_delta=10,
            estimation_source=None,
    ):
        redis_key = utils.make_redis_key(key, order_nr)
        redis_value = redis_store.get(redis_key)
        if redis_value is None:
            assert value is None
        else:
            redis_value = redis_value.decode()
            if isinstance(value, datetime.datetime):
                redis_value = utils.parse_datetime(redis_value)
            if isinstance(value, datetime.timedelta):
                redis_value = datetime.timedelta(seconds=int(redis_value))
            if isinstance(value, int):
                redis_value = int(redis_value)
            assert value == redis_value
            if redis_keys_ttl is not None:
                ttl = redis_keys_ttl.get(key, redis_keys_ttl['__default__'])
                assert abs(ttl - redis_store.ttl(redis_key)) <= ttl_delta
            if estimation_source is not None:
                redis_estimation_source_key = (
                    utils.make_redis_estimation_source_key(key, order_nr)
                )
                redis_estimation_source = redis_store.get(
                    redis_estimation_source_key,
                )
                assert redis_estimation_source == estimation_source

    return do_check_redis_value


@pytest.fixture(name='check_metrics')
def _check_metrics(taxi_eats_eta_monitor):
    # pylint: disable=redefined-outer-name
    async def do_check_metrics(
            requests=0,
            get_eta_from_redis=0,
            get_eta_from_postgres=0,
            update_cargo_info=0,
            update_retail_info=0,
            update_ml_prediction=0,
            get_order_not_found_from_redis=0,
            get_order_not_found_from_postgres=0,
    ):
        metrics = await taxi_eats_eta_monitor.get_metric('handlers-stats')
        assert metrics == {
            'requests': requests,
            'get-eta-from-redis': get_eta_from_redis,
            'get-eta-from-postgres': get_eta_from_postgres,
            'update-cargo-info': update_cargo_info,
            'update-retail-info': update_retail_info,
            'update-ml-prediction': update_ml_prediction,
            'get-order-not-found-from-redis': get_order_not_found_from_redis,
            'get-order-not-found-from-postgres': (
                get_order_not_found_from_postgres
            ),
        }

    return do_check_metrics


@pytest.fixture()
def db_insert_order(db_get_cursor, db_orders_fields):
    def insert_order(order: Order) -> int:
        for key in order:
            assert key in db_orders_fields
        order = order.copy()
        if isinstance(order['batch_info'], dict):
            order['batch_info'] = json.dumps(order['batch_info'])
        cursor = db_get_cursor()
        query = (
            'INSERT INTO eats_eta.orders ({}) VALUES ({})'
            ' RETURNING id'.format(
                ', '.join(order.keys()),
                ', '.join('%s' for _ in range(len(order))),
            )
        )
        cursor.execute(query, list(order.values()))

        return cursor.fetchone()[0]

    return insert_order


@pytest.fixture()
def db_select_orders(db_get_cursor, db_orders_fields):
    def select_orders(**where) -> List[Order]:
        for key in where:
            assert key in db_orders_fields

        cursor = db_get_cursor()
        if not where:
            query = 'SELECT {} FROM eats_eta.orders'.format(
                ', '.join(db_orders_fields),
            )
            cursor.execute(query)
        else:
            query = 'SELECT {} FROM eats_eta.orders WHERE {}'.format(
                ', '.join(db_orders_fields),
                ', '.join('{} = %s'.format(k) for k in where),
            )
            cursor.execute(query, list(where.values()))

        return sorted(
            list(map(dict, cursor.fetchall())), key=lambda order: order['id'],
        )

    return select_orders


Place = Dict[str, Any]


@pytest.fixture(name='make_place')
def _make_place(now_utc):
    def make_place(**kwargs) -> Place:
        place = {
            'id': 1,
            'slug': 'place_slug-1',
            'enabled': True,
            'type': 'native',
            'business': 'shop',
            'brand_id': 1,
            'brand_slug': 'brand_slug-1',
            'city': 'big city',
            'address': 'a street',
            'country_id': 1,
            'country_currency': {'sign': '₽', 'code': 'RUB'},
            'region_id': 1,
            'location': '(56.78,12.34)',
            'is_fast_food': False,
            'shop_picking_type': None,
            'preparation': datetime.timedelta(seconds=1000),
            'average_preparation': datetime.timedelta(seconds=1000),
            'extra_preparation': datetime.timedelta(seconds=1000),
            'load_level': None,
            'load_level_updated_at': None,
            'revision_id': 0,
            'updated_at': now_utc,
            'price_category_value': 2.0,
            'rating_users': 5.0,
        }
        for key in kwargs:
            assert key in place
        place.update(kwargs)
        place['country_currency'] = _make_currency(place['country_currency'])
        for key in 'preparation', 'average_preparation', 'extra_preparation':
            place[key] = _make_interval(place[key])
        for key in 'load_level_updated_at', 'updated_at':
            place[key] = _make_timepoint(place[key])
        return place

    return make_place


@pytest.fixture(name='db_places_fields')
def _db_places_fields(make_place) -> Set[str]:
    return set(make_place().keys())


@pytest.fixture()
def db_insert_place(db_get_cursor, db_places_fields):
    def insert_place(place: Place) -> int:
        for key in place:
            assert key in db_places_fields

        cursor = db_get_cursor()
        query = (
            'INSERT INTO eats_eta.places ({}) VALUES ({})'
            ' RETURNING id'.format(
                ', '.join(place.keys()),
                ', '.join('%s' for _ in range(len(place))),
            )
        )
        cursor.execute(query, list(place.values()))

        return cursor.fetchone()[0]

    return insert_place


@pytest.fixture()
def db_select_places(db_get_cursor, db_places_fields):
    def select_places(**where) -> List[Place]:
        for key in where:
            assert key in db_places_fields

        cursor = db_get_cursor()
        if not where:
            query = 'SELECT {} FROM eats_eta.places'.format(
                ', '.join(db_places_fields),
            )
            cursor.execute(query)
        else:
            query = 'SELECT {} FROM eats_eta.places WHERE {}'.format(
                ', '.join(db_places_fields),
                ', '.join('{} = %s'.format(k) for k in where),
            )
            cursor.execute(query, list(where.values()))

        return sorted(
            list(map(dict, cursor.fetchall())), key=lambda place: place['id'],
        )

    return select_places


@pytest.fixture()
def claim_statuses_list(db_get_cursor):
    cursor = db_get_cursor()
    cursor.execute('SELECT enum_range(NULL::eats_eta.claim_status)::text[]')
    return cursor.fetchone()[0]


@pytest.fixture()
def get_cargo_journal_cursor(db_get_cursor):
    def do_get_cargo_journal_cursor(corp_client):
        cursor = db_get_cursor()
        cursor.execute(
            'SELECT cursor FROM eats_eta.cargo_journal_cursor '
            'WHERE corp_client = %s',
            [corp_client],
        )
        return cursor.fetchone()[0]

    return do_get_cargo_journal_cursor


@pytest.fixture()
def get_segments_journal_cursor(db_get_cursor):
    def do_get_segments_journal_cursor():
        cursor = db_get_cursor()
        cursor.execute('SELECT cursor FROM eats_eta.segments_journal_cursor')
        return cursor.fetchone()[0]

    return do_get_segments_journal_cursor


@pytest.fixture()
def create_cargo_journal_cursor(db_get_cursor):
    def do_create_cargo_journal_cursor(corp_client, journal_cursor):
        cursor = db_get_cursor()
        cursor.execute(
            'INSERT INTO eats_eta.cargo_journal_cursor (corp_client, cursor)'
            'VALUES (%s, %s) '
            'RETURNING id',
            [corp_client, journal_cursor],
        )
        return cursor.fetchone()[0]

    return do_create_cargo_journal_cursor


@pytest.fixture()
def cargo(mockserver, load_json):
    class Cargo:
        def __init__(self):
            self._claims = {}
            self._order_claims = collections.defaultdict(list)
            self._build_mocks()
            self.points_eta = load_json('points_eta.json')
            self._batch_info = {}

        def add_batch_info(self, claim_id: str, **kwargs):
            self._batch_info[claim_id] = kwargs

        def add_claim(
                self,
                claim_id: str,
                order_nr: str,
                created_ts: str = None,
                status: str = None,
                order_type: str = 'native',
                brand_id: int = 1,
                country_id: int = 1,
                corp_client=None,
                performer_info: dict = None,
        ):
            claim = {
                'id': claim_id,
                'order_nr': order_nr,
                'created_ts': created_ts,
                'status': status,
                'authorization': utils.make_cargo_authorization_header(
                    order_type=order_type,
                    brand_id=brand_id,
                    country_id=country_id,
                ),
                'performer_info': performer_info,
            }
            self._claims[claim_id] = claim
            self._order_claims[order_nr].append(claim)

        def _build_mocks(self):
            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v2/claims/info',
            )
            def _cargo_claims_info(request):
                assert request.method == 'POST'
                authorization = request.headers['Authorization']
                claim_id = request.query['claim_id']
                if claim_id not in self._claims:
                    return mockserver.make_response(
                        status=404,
                        json={
                            'code': 'not_found',
                            'message': 'claim not found',
                        },
                    )

                claim = self._claims[claim_id]
                claim_stub = load_json('claim.json')
                assert authorization == claim['authorization']
                claim_response = dict(claim_stub)
                claim_response['id'] = claim['id']

                if claim['created_ts']:
                    claim_response['created_ts'] = utils.to_string(
                        claim['created_ts'],
                    )
                if claim['status']:
                    claim_response['status'] = claim['status']
                for point in claim_response['route_points']:
                    point['external_order_id'] = claim['order_nr']
                if claim.get('performer_info'):
                    claim_response['performer_info'].update(
                        **claim['performer_info'],
                    )
                return claim_response

            self.mock_cargo_claims_info = _cargo_claims_info

            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
            )
            def _cargo_points_eta(request):
                assert request.method == 'POST'
                claim_id = request.query['claim_id']
                if claim_id not in self._claims:
                    return mockserver.make_response(
                        status=404,
                        json={
                            'code': 'not_found',
                            'message': 'claim with id={} not found'.format(
                                claim_id,
                            ),
                        },
                    )

                points_eta_response = copy.deepcopy(self.points_eta)
                for point in points_eta_response['route_points']:
                    point['external_order_id'] = self._claims[claim_id][
                        'order_nr'
                    ]
                return mockserver.make_response(
                    status=200, json=points_eta_response,
                )

            self.mock_cargo_points_eta = _cargo_points_eta

            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
            )
            def _cargo_performer_position(request):
                assert request.method == 'GET'
                claim_id = request.query['claim_id']
                if claim_id not in self._claims:
                    return mockserver.make_response(
                        status=404,
                        json={
                            'code': 'not_found',
                            'message': 'claim with id={} not found'.format(
                                claim_id,
                            ),
                        },
                    )

                return mockserver.make_response(
                    status=200, json=load_json('performer_position.json'),
                )

            self.mock_cargo_performer_position = _cargo_performer_position

            @mockserver.json_handler('/b2b-taxi/internal/external-performer')
            def _cargo_external_performer(request):
                assert request.method == 'GET'
                authorization = request.headers['Authorization']
                claim_id = request.query['sharing_key']
                claim = self._claims.get(claim_id, {})
                if authorization != claim.get('authorization', None):
                    return mockserver.make_response(status=404)
                return {'batch_info': self._batch_info.get(claim_id, None)}

            self.mock_external_performer = _cargo_external_performer

    return Cargo()


@pytest.fixture()
def catalog(mockserver, now_utc, load_json):
    class Catalog:
        def __init__(self):
            self._revision_places = collections.defaultdict(list)
            self._build_mocks()

        def add_place(self, place_id: int, revision_id: int):
            place = {
                'id': place_id,
                'revision_id': revision_id,
                'updated_at': now_utc,
            }
            self._revision_places[revision_id].append(place)

        def _build_mocks(self):
            @mockserver.json_handler(
                '/eats-catalog-storage/internal/'
                'eats-catalog-storage/v1/places/updates',
            )
            def _places_updates(request):
                assert request.method == 'POST'
                last_known_revision = request.json['last_known_revision']
                limit = request.json['limit']

                places = []
                for revision, revision_places in sorted(
                        filter(
                            lambda item: item[0] >= last_known_revision,
                            self._revision_places.items(),
                        ),
                        key=operator.itemgetter(0),
                ):
                    last_known_revision = revision

                    for place in revision_places:
                        if limit == 0:
                            break
                        place.update(load_json('place_info.json'))
                        places.append(place)
                        limit -= 1
                    if limit == 0:
                        break

                return mockserver.make_response(
                    status=200,
                    json={
                        'last_known_revision': last_known_revision,
                        'places': places,
                    },
                )

            self.mock_places_updates = _places_updates

    return Catalog()


@pytest.fixture()
def surge_resolver(mockserver, load_json):
    class SurgeResolver:
        def __init__(self):
            self._places = {}
            self._build_mocks()

        def add_place(self, place_id: int):
            place = {'id': place_id}
            self._places[place_id] = place

        def _build_mocks(self):
            @mockserver.json_handler('/eats-surge-resolver/api/v1/surge-level')
            def _surge_level(request):
                assert request.method == 'POST'

                surge = {'id': 1, 'jsonrpc': '2.0', 'result': []}

                place_surge = load_json('surge.json')
                for place_id in request.json['params']['placeIds']:
                    place_surge['placeId'] = place_id
                    surge['result'].append(place_surge)

                return mockserver.make_response(status=200, json=surge)

            self.mock_surge_level = _surge_level

    return SurgeResolver()


@pytest.fixture()
def pickers(mockserver, load_json):
    class Pickers:
        def __init__(self):
            self._orders = {}
            self._build_mocks()
            self.cart = load_json('cart.json')
            self.estimate = load_json('estimate.json')
            self.place_load = load_json('place_load.json')

        def add_order(
                self, order_nr: str, status: str, flow_type: str, **kwargs,
        ):
            order = {
                'eats_id': order_nr,
                'status': status,
                'flow_type': flow_type,
            }
            order.update(**kwargs)
            self._orders[order_nr] = order

        def _build_mocks(self):
            @mockserver.json_handler('/eats-picker-orders/api/v1/order')
            def _picker_orders_get_order(request):
                assert request.method == 'GET'

                eats_id = request.query['eats_id']
                if eats_id not in self._orders:
                    return mockserver.make_response(
                        status=404, json={'code': 'not found', 'message': ''},
                    )

                order = self._orders[eats_id]
                picker_order = load_json('picker_order.json')
                picker_order.update(**order)
                return mockserver.make_response(
                    status=200, json={'payload': picker_order, 'meta': {}},
                )

            self.mock_picker_orders_get_order = _picker_orders_get_order

            @mockserver.json_handler(
                '/eats-picker-dispatch/api/v1/place/'
                'calculate-load-without-order',
            )
            def _dispatch_preceding_load(request):
                assert request.method == 'POST'

                eats_id = request.json['eats_id']
                if eats_id not in self._orders:
                    return mockserver.make_response(
                        status=404, json={'code': 'not found', 'message': ''},
                    )

                return mockserver.make_response(
                    status=200, json=self.place_load,
                )

            self.mock_dispatch_preceding_load = _dispatch_preceding_load

            @mockserver.json_handler(
                '/eats-picker-orders/api/v1/orders/status-time',
            )
            def _picker_orders_status_time(request):
                assert request.method == 'POST'

                status_time = load_json('status_time.json')
                timestamps = []
                for eats_id in request.json['eats_ids']:
                    if eats_id in self._orders:
                        timestamps.append(
                            {
                                'eats_id': eats_id,
                                'status_change_timestamp': status_time[
                                    'status_change_timestamp'
                                ],
                            },
                        )
                return mockserver.make_response(
                    status=200, json={'timestamps': timestamps},
                )

            self.mock_picker_orders_status_time = _picker_orders_status_time

            @mockserver.json_handler('/eats-picker-orders/api/v1/order/cart')
            def _picker_orders_cart(request):
                assert request.method == 'GET'

                eats_id = request.query['eats_id']
                if eats_id not in self._orders:
                    return mockserver.make_response(
                        status=404, json={'code': 'not found', 'message': ''},
                    )

                return mockserver.make_response(status=200, json=self.cart)

            self.mock_picker_orders_cart = _picker_orders_cart

            @mockserver.json_handler(
                '/eats-picking-time-estimator/api/v1/order/estimate',
            )
            def _picker_time_estimate(request):
                assert request.method == 'POST'

                eats_id = request.json['eats_id']
                if eats_id not in self._orders:
                    return mockserver.make_response(
                        status=400, json={'code': 'not found', 'message': ''},
                    )

                return mockserver.make_response(status=200, json=self.estimate)

            self.mock_picker_time_estimate = _picker_time_estimate

    return Pickers()


@pytest.fixture()
def orders_retrieve(mockserver, now_utc):
    class OrdersRetrieve:
        def __init__(self):
            self._user_orders = collections.defaultdict(dict)
            self._build_mocks()

        def add_order(self, order_nr, yandex_uid, status, **kwargs):
            order = dict(
                order_id=order_nr,
                service='eats',
                title='Магнит',
                created_at=now_utc,
                status=status,
                calculation={
                    'addends': [],
                    'final_cost': '',
                    'discount': '',
                    'refund': '',
                    'currency_code': '',
                    'final_cost_decimal': '',
                },
                legal_entities=[],
                destinations=(
                    {
                        'short_text': 'ул. Пушкина, д. Колотушкина',
                        'point': [30.33811, 59.93507],
                    },
                ),
                meta_info=None,
                **kwargs,
            )
            order['created_at'] = utils.to_string(order['created_at'])
            self._user_orders[yandex_uid][order_nr] = order

        def _build_mocks(self):
            @mockserver.json_handler(
                '/eats-core-orders-retrieve/orders/retrieve',
            )
            def _eats_core_orders_retrieve(request):
                assert request.method == 'POST'
                assert request.json['services'] == ['eats']
                assert not request.json['user_identity']['bound_yandex_uids']
                assert request.json['user_identity']['include_eater_orders']
                assert request.json['range']['results'] == 1
                user_orders = self._user_orders[
                    request.json['user_identity']['yandex_uid']
                ]
                order_id = request.json['range']['order_id']
                response = {'orders': []}
                if order_id in user_orders:
                    response['orders'].append(user_orders[order_id])
                return response

            self.mock = _eats_core_orders_retrieve

    return OrdersRetrieve()


@pytest.fixture()
def revisions(mockserver, now_utc):
    class RevisionsMock:
        def __init__(self):
            self.order_revisions = {}
            self._build_mocks()

        def set_default(self, order_id: str, place_id: str):
            revision_ids = ['aaa', 'ddd']
            self.add_order_customer_service(
                order_id=order_id,
                place_id=place_id,
                revision_id=revision_ids[0],
                customer_service_id='retail-product',
                customer_service_name='Расходы на исполнение '
                'поручений по заказу',
                cost_for_customer='780.00',
                type_='retail',
                composition_products=[
                    self.make_composition_product(
                        id_='item_000-0',
                        name='Макароны',
                        cost_for_customer='50.00',
                        origin_id='item-0',
                    ),
                    self.make_composition_product(
                        id_='item_111-1',
                        name='Дырка от бублика',
                        cost_for_customer='150.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_111-2',
                        name='Дырка от бублика',
                        cost_for_customer='150.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_222-1',
                        name='Виноград',
                        cost_for_customer='100.00',
                        weight=500,
                        origin_id='item-2',
                    ),
                ],
            )
            self.add_order_customer_service(
                order_id=order_id,
                place_id=place_id,
                revision_id=revision_ids[1],
                customer_service_id='retail-product',
                customer_service_name='Расходы на исполнение '
                'поручений по заказу',
                cost_for_customer='617.00',
                refunded_amount='260.00',
                type_='retail',
                composition_products=[
                    self.make_composition_product(
                        id_='item_000-0',
                        name='Макароны',
                        cost_for_customer='50.00',
                        origin_id='item-0',
                    ),
                    self.make_composition_product(
                        id_='item_111-1',
                        name='Дырка от бублика',
                        cost_for_customer='60.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_111-2',
                        name='Дырка от бублика',
                        cost_for_customer='0.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_555-1',
                        name='Сливы',
                        cost_for_customer='120.00',
                        weight=500,
                        origin_id='item-5',
                    ),
                    self.make_composition_product(
                        id_='item_555-2',
                        name='Сливы',
                        cost_for_customer='120.00',
                        weight=500,
                        origin_id='item-5',
                    ),
                ],
                refunds=[
                    {
                        'refund_revision_id': revision_ids[1],
                        'refund_products': [
                            {'id': 'item_111-1', 'refunded_amount': '100.00'},
                            {'id': 'item_111-2', 'refunded_amount': '160.00'},
                        ],
                    },
                ],
            )
            self.add_order_customer_service(
                order_id=order_id,
                place_id=place_id,
                revision_id=revision_ids[1],
                customer_service_id='assembly',
                customer_service_name='Стоимость сборки',
                cost_for_customer='60.00',
                type_='assembly',
            )
            self.add_order_customer_service(
                order_id=order_id,
                place_id=place_id,
                revision_id=revision_ids[1],
                customer_service_id='delivery',
                customer_service_name='Стоимость доставки',
                cost_for_customer='50.00',
                type_='delivery',
            )
            self.add_order_customer_service(
                order_id=order_id,
                place_id=place_id,
                revision_id=revision_ids[1],
                customer_service_id='tips',
                customer_service_name='Чаевые курьеру',
                cost_for_customer='40.00',
                type_='tips',
            )
            self.add_order_customer_service(
                order_id=order_id,
                place_id=place_id,
                revision_id=revision_ids[1],
                customer_service_id='restaurant_tips',
                customer_service_name='Чаевые ресторану',
                cost_for_customer='60.00',
                type_='restaurant_tips',
            )

        @staticmethod
        def make_composition_product(
                id_: str,
                name: str,
                cost_for_customer: str,
                type_: str = 'product',
                parent_id: Optional[str] = None,
                origin_id: Optional[str] = None,
                weight: Optional[float] = None,
                measure_unit: Optional[str] = 'GRM',
        ):
            composition_product: dict = dict(
                id=id_,
                name=name,
                cost_for_customer=cost_for_customer,
                type=type_,
                parent_id=parent_id,
                origin_id=origin_id,
            )
            if weight is not None and measure_unit is not None:
                composition_product['weight'] = {
                    'value': weight,
                    'measure_unit': measure_unit,
                }
            return composition_product

        def add_order_customer_service(
                self,
                order_id: str,
                place_id: str,
                revision_id: str,
                customer_service_id: str,
                customer_service_name: str,
                cost_for_customer: str,
                type_: str,
                composition_products: Optional[list] = None,
                currency: str = 'RUB',
                refunds: Optional[list] = None,
                refunded_amount: Optional[str] = None,
        ):
            order_revisions = self.order_revisions.setdefault(order_id, {})
            revision = order_revisions.setdefault(revision_id, [])
            customer_service = dict(
                id=customer_service_id,
                name=customer_service_name,
                cost_for_customer=cost_for_customer,
                currency=currency,
                type=type_,
                trust_product_id='eda_133158084',
                place_id=place_id,
                details={
                    'composition_products': composition_products,
                    'discriminator_type': 'composition_products_details',
                    # элементы refunds - словари с полями id и refunded_amount
                    'refunds': refunds,
                },
            )
            if refunded_amount is not None:
                customer_service['refunded_amount'] = refunded_amount
            revision.append(customer_service)

        def _build_mocks(self):
            @mockserver.json_handler(
                '/eats-core-order-revision/internal-api/v1'
                '/order-revision/list',
            )
            def _eats_core_order_revision_list(request):
                assert request.method == 'GET'
                order_id = request.query['order_id']
                if order_id not in self.order_revisions:
                    return mockserver.make_response(status=404)
                order_revisions = self.order_revisions[order_id]
                return {
                    'order_id': order_id,
                    'revisions': [
                        {'revision_id': revision_id}
                        for revision_id in order_revisions.keys()
                    ],
                }

            self.mock_order_revision_list = _eats_core_order_revision_list

            @mockserver.json_handler(
                '/eats-core-order-revision/internal-api/v1'
                '/order-revision/customer-services/details',
            )
            def _eats_core_order_revision_details(request):
                assert request.method == 'POST'
                order_id = request.json['order_id']
                revision_id = request.json['revision_id']
                if revision_id not in self.order_revisions.get(order_id, {}):
                    return mockserver.make_response(status=404)
                return {
                    'revision_id': revision_id,
                    'customer_services': self.order_revisions[order_id][
                        revision_id
                    ],
                    'created_at': (now_utc.isoformat()),
                }

            self.mock_order_revision_details = (
                _eats_core_order_revision_details
            )

    return RevisionsMock()


@pytest.fixture()
def checkout(mockserver, now_utc):
    class CheckoutMock:
        def __init__(self):
            self.orders_revisions = {}
            self._build_mocks()

        def add_order_revision(
                self,
                order_nr: str,
                delivery_date: Optional[datetime.datetime],
        ):
            self.orders_revisions[order_nr] = {
                'number': 1,
                'costs': {'type': 'unfetched_object'},
                'items': {'type': 'unfetched_object'},
                'created_at': utils.to_string(now_utc),
                'delivery_date': utils.to_string(delivery_date),
            }

        def _build_mocks(self):
            @mockserver.json_handler('/eats-checkout/orders/fetch-revisions')
            def _eats_checkout_orders_revisions(request):
                assert request.method == 'POST'
                order_nrs = request.json['order_nrs']

                return {
                    'items': [
                        {
                            'order_nr': order_nr,
                            'revision': self.orders_revisions[order_nr],
                            'changes': {'type': 'unfetched_object'},
                            'currency_code': 'RUB',
                            'payment_method': 'prepayment_cashless',
                        }
                        for order_nr in order_nrs
                        if order_nr in self.orders_revisions.keys()
                    ],
                }

            self.mock_orders_revisions = _eats_checkout_orders_revisions

    return CheckoutMock()
