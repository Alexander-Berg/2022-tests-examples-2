# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import collections
import datetime
import json

import dateutil.parser
import pytest
import pytz

from eats_picker_dispatch_plugins import *  # noqa: F403 F401

from . import utils


@pytest.fixture(name='now_utc')
def _now_utc(mocked_time):
    def make_now_utc():
        return mocked_time.now().replace(tzinfo=pytz.utc)

    return make_now_utc


@pytest.fixture(name='get_dispatch_cancel_reasons')
def _get_dispatch_cancel_reasons(taxi_eats_picker_dispatch_monitor):
    async def do_get_dispatch_cancel_reasons(place_id):
        place_id = str(place_id or 'unknown')
        metric = await taxi_eats_picker_dispatch_monitor.get_metric(
            'dispatch-failed',
        )
        if place_id in metric:
            del metric[place_id]['$meta']
            return metric[place_id]
        return {}

    return do_get_dispatch_cancel_reasons


@pytest.fixture(name='places_toggled_metric_diff')
async def _places_toggled_metric_diff(
        taxi_eats_picker_dispatch, taxi_eats_picker_dispatch_monitor,
):
    await taxi_eats_picker_dispatch.tests_control(reset_metrics=True)

    async def do_calc_diff():
        metric = await taxi_eats_picker_dispatch_monitor.get_metric(
            'place-toggle',
        )
        del metric['$meta']
        diff = {}
        for place_id, place_metric in metric.items():
            diff[place_id] = {
                key: value for key, value in place_metric.items() if value
            }
        return diff

    return do_calc_diff


@pytest.fixture(name='environment')
def _environment(load, mockserver, now_utc):
    class Environment:
        def __init__(self):
            self.place_count_ = 0
            self.order_stub_ = json.loads(load('picker_order_stub.json'))
            self.order_count_ = 0
            self.orders_ = dict()
            self.place_orders_ = collections.defaultdict(list)
            self.picker_order_ = dict()
            self.picker_available_until_ = dict()
            self.place_pickers_ = collections.defaultdict(list)
            self.pickers_places_ = collections.defaultdict(list)

            self._build_mocks()

        def create_places(self, count):
            result = range(self.place_count_, self.place_count_ + count)
            self.place_count_ += count
            return result

        def create_orders(self, place_id, count, **kwargs):
            result = []
            for i in range(self.order_count_, self.order_count_ + count):
                eats_id = f'201221-00000{i}'
                order = dict(
                    self.order_stub_,
                    id=str(i),
                    eats_id=eats_id,
                    place_id=place_id,
                    status='new',
                    flow_type='picking_packing',
                )
                order.update(**kwargs)

                self.orders_[eats_id] = order
                self.place_orders_[place_id].append(order)
                result.append(order)
            self.order_count_ += count
            return result

        def remove_order(self, eats_id):
            del self.orders_[eats_id]
            self.order_count_ -= 1

        def create_pickers(self, place_id, count, available_until=None):
            if available_until is None:
                available_until = now_utc() + datetime.timedelta(hours=8)
            picker_count = len(self.picker_order_)
            result = [
                str(i) for i in range(picker_count, picker_count + count)
            ]
            for picker_id in result:
                self.place_pickers_[place_id].append(picker_id)
                self.pickers_places_[picker_id].append(place_id)
                self.picker_order_[picker_id] = None
                self.picker_available_until_[picker_id] = available_until
            return result

        def create_pickers_empty(self, place_id):
            self.place_pickers_[place_id] = []

        def create_pickers_in_log_group(
                self, place_ids, count, available_until=None,
        ):
            if available_until is None:
                available_until = now_utc() + datetime.timedelta(hours=8)
            picker_count = len(self.picker_order_)
            result = [
                str(i) for i in range(picker_count, picker_count + count)
            ]
            for place_id in place_ids:
                for picker_id in result:
                    self.place_pickers_[place_id].append(picker_id)
                    self.pickers_places_[picker_id].append(place_id)
                    self.picker_order_[picker_id] = None
                    self.picker_available_until_[picker_id] = available_until
            return result

        def remove_pickers(self, place_id):
            del self.place_pickers_[place_id]

        def assign_picker_order(self, picker_id, order):
            assert order is self.orders_.get(order['eats_id'])
            order['status'] = 'assigned'
            order['status_updated_at'] = utils.to_string(now_utc())
            self.picker_order_[picker_id] = {
                k: order[k]
                for k in [
                    'eats_id',
                    'status',
                    'status_updated_at',
                    'estimated_picking_time',
                    'place_id',
                ]
            }

        def start_picking_order(self, picker_id, order):
            assert order is self.orders_.get(order['eats_id'])
            order['status'] = 'picking'
            order['status_updated_at'] = utils.to_string(now_utc())
            self.picker_order_[picker_id] = {
                k: order[k]
                for k in [
                    'eats_id',
                    'status',
                    'status_updated_at',
                    'estimated_picking_time',
                    'place_id',
                ]
            }

        def get_delivery_duration_response(self, _):
            return {
                'name': 'delivery_duration',
                'duration': 1800,
                'remaining_duration': 1800,
                'calculated_at': utils.to_string(now_utc()),
                'status': 'not_started',
            }

        def get_picking_duration_response(self, order_nr):
            order = self.orders_[order_nr]
            total_picking_duration = order['estimated_picking_time']
            # эмулируется старая логика, чтобы не переписывать другие тесты
            if order['status'] == 'picking':
                pickedup_at = dateutil.parser.parse(
                    order['status_updated_at'],
                ) + (datetime.timedelta(seconds=total_picking_duration))
                if pickedup_at < now_utc():
                    remaining_picking_duration = total_picking_duration
                else:
                    remaining_picking_duration = (
                        pickedup_at - now_utc()
                    ).total_seconds()
                estimation_status = 'in_progress'
            else:
                remaining_picking_duration = total_picking_duration
                estimation_status = 'not_started'
            return {
                'name': 'picking_duration',
                'duration': total_picking_duration,
                'remaining_duration': remaining_picking_duration,
                'calculated_at': utils.to_string(now_utc()),
                'status': estimation_status,
            }

        def _build_mocks(self):
            @mockserver.json_handler(
                '/eats-picker-orders/api/v1/orders/select-for-dispatch',
            )
            def _picker_orders_select_orders_for_dispatch(request):
                filter_map = request.json

                def filter_order(order):
                    status = filter_map.get('state', [])
                    if status and order['status'] not in status:
                        return False
                    flow_type = filter_map.get('flow_type', [])
                    if flow_type and order['flow_type'] not in flow_type:
                        return False
                    return True

                response = {
                    'orders': [
                        o for o in self.orders_.values() if filter_order(o)
                    ],
                }
                return response

            # pylint: disable=invalid-name
            self.mock_picker_orders_select_orders_for_dispatch = (
                _picker_orders_select_orders_for_dispatch
            )

            @mockserver.json_handler(
                '/eats-picker-supply/api/v1/select-store-pickers/',
            )
            def _picker_supply_select_store_pickers(request):
                assert request.method == 'POST'

                def build_picker_json(picker_id):
                    result = {
                        'picker_id': picker_id,
                        'picker_available_until': utils.to_string(
                            self.picker_available_until_[picker_id],
                        ),
                    }
                    order = self.picker_order_.get(picker_id)
                    if order:
                        result['order'] = order
                    return result

                return {
                    'stores': [
                        {
                            'place_id': place_id,
                            'pickers': (
                                [
                                    build_picker_json(picker_id)
                                    for picker_id in self.place_pickers_[
                                        place_id
                                    ]
                                ]
                                if place_id in self.place_pickers_
                                else None
                            ),
                        }
                        for place_id in (
                            request.json.get(
                                'stores', self.place_pickers_.keys(),
                            )
                        )
                    ],
                }

            # pylint: disable=invalid-name
            self.mock_picker_supply_select_store_pickers = (
                _picker_supply_select_store_pickers
            )

            @mockserver.json_handler(
                '/eats-picker-supply/api/v1/select-pickers-stores',
            )
            def _picker_supply_select_pickers_stores(request):
                assert request.method == 'POST'
                pickers_ids = request.json['picker_ids']
                return {
                    'pickers_stores': [
                        {
                            'picker_id': picker_id,
                            'place_ids': self.pickers_places_[picker_id],
                        }
                        for picker_id in pickers_ids
                    ],
                }

            # pylint: disable=invalid-name
            self.mock_picker_supply_select_pickers_stores = (
                _picker_supply_select_pickers_stores
            )

            @mockserver.json_handler('/eats-picker-orders/api/v1/order')
            def _get_picker_order(request):
                assert request.method == 'GET'
                eats_id = request.query['eats_id']
                if eats_id in self.orders_:
                    return {'payload': self.orders_[eats_id], 'meta': {}}
                return mockserver.make_response(status=404)

            self.mock_get_picker_order = _get_picker_order

            @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
            def _picker_orders_status(request):
                assert request.method == 'POST'
                eats_id = request.query['eats_id']
                self.orders_[eats_id]['status'] = request.json['status']
                return mockserver.make_response()

            @mockserver.json_handler(
                '/eats-picker-orders/api/v1/orders/status-time',
            )
            def _picker_orders_status_time(request):
                assert request.method == 'POST'
                timestamps = []
                for eats_id in request.json['eats_ids']:
                    order = self.orders_.get(eats_id)
                    if order and utils.enum_status(
                            request.json['state'],
                    ) <= utils.enum_status(order['status']):
                        timestamps.append(
                            {
                                'eats_id': order['eats_id'],
                                'status_change_timestamp': order[
                                    'status_updated_at'
                                ],
                            },
                        )
                return mockserver.make_response(
                    status=200, json={'timestamps': timestamps},
                )

            # pylint: disable=invalid-name
            self.mock_picker_orders_status_time = _picker_orders_status_time

            # pylint: disable=invalid-name
            self.mock_picker_orders_status = _picker_orders_status

            @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
            def _core_notify_status_change_handler(request):
                assert request.method == 'POST'
                return {'isSuccess': True}

            # pylint: disable=invalid-name
            self.mock_core_notify_status_change_handler = (
                _core_notify_status_change_handler
            )

            @mockserver.json_handler('/eats-eta/v1/eta/orders/estimate')
            def _eats_eta_orders_estimate(request):
                assert request.method == 'POST'
                assert request.query['consumer'] == 'eats-picker-dispatch'
                assert not request.json['check_status']
                assert all(
                    estimation in ['picking_duration', 'delivery_duration']
                    for estimation in request.json['estimations']
                )
                response_orders = []
                not_found_orders = []
                for order_nr in request.json['orders']:
                    if order_nr not in self.orders_:
                        not_found_orders.append(order_nr)
                        continue
                    response_estimations = []
                    for estimation in request.json['estimations']:
                        if estimation == 'delivery_duration':
                            response_estimations.append(
                                self.get_delivery_duration_response(order_nr),
                            )
                        else:
                            response_estimations.append(
                                self.get_picking_duration_response(order_nr),
                            )
                    response_orders.append(
                        {
                            'order_nr': order_nr,
                            'estimations': response_estimations,
                        },
                    )
                return {
                    'orders': response_orders,
                    'not_found_orders': not_found_orders,
                }

            self.mock_eats_eta_orders_estimate = _eats_eta_orders_estimate

    return Environment()


@pytest.fixture(name='places_environment')
def _places_environment(load_json, mockserver, now_utc):
    class Environment:
        def __init__(self):
            self.next_revision_id_ = 1
            self.next_place_id_ = 100000
            self.delivery_zones_count_ = 0
            self.catalog_place_stub_ = load_json(
                'eats_catalog_storage_place.json',
            )
            self.core_place_stub_ = load_json('eats_core_place.json')
            self.catalog_places = {}
            self.catalog_places_sorted = []
            self.core_places = {}
            self.places_updates = []
            self.delivery_zones = collections.defaultdict(list)
            self.disabled_places = []
            self.enabled_places = []

            self._build_mocks()

        def create_places(self, count, catalog_kwargs=None, core_kwargs=None):
            result = []
            for i in range(count):
                place_id = self.next_place_id_ + i
                catalog_place = self.catalog_place_stub_.copy()
                catalog_place['id'] = place_id
                catalog_place['revision_id'] = self.next_revision_id_ + i
                catalog_place['updated_at'] = now_utc()
                if catalog_kwargs:
                    catalog_place.update(catalog_kwargs)
                catalog_place['updated_at'] = utils.to_string(
                    catalog_place['updated_at'],
                )
                self.catalog_places[catalog_place['id']] = catalog_place
                self.catalog_places_sorted.append(catalog_place)
                if catalog_place.get('working_intervals') is not None:
                    for working_interval in catalog_place['working_intervals']:
                        working_interval['from'] = utils.to_string(
                            working_interval['from'],
                        )
                        working_interval['to'] = utils.to_string(
                            working_interval['to'],
                        )
                core_place = self.core_place_stub_.copy()
                core_place['id'] = place_id
                if core_kwargs:
                    core_place.update(**core_kwargs)
                self.core_places[core_place['id']] = core_place
                result.append(place_id)

            self.catalog_places_sorted.sort(key=lambda p: p['revision_id'])
            self.next_place_id_ += count
            self.next_revision_id_ += count
            return result

        def create_delivery_zones(self, place_id, count, **kwargs):
            result = []
            for i in range(
                    self.delivery_zones_count_,
                    self.delivery_zones_count_ + count,
            ):
                delivery_zone = {
                    'id': i,
                    'revision_id': 1,
                    'updated_at': now_utc(),
                    'enabled': True,
                    'place_id': place_id,
                    'working_intervals': [],
                }
                delivery_zone.update(kwargs)
                delivery_zone['updated_at'] = utils.to_string(
                    delivery_zone['updated_at'],
                )
                if delivery_zone['working_intervals'] is not None:
                    for working_interval in delivery_zone['working_intervals']:
                        working_interval['from'] = utils.to_string(
                            working_interval['from'],
                        )
                        working_interval['to'] = utils.to_string(
                            working_interval['to'],
                        )
                result.append(delivery_zone)
            self.delivery_zones[place_id] += result
            self.delivery_zones_count_ += count
            return result

        def _build_mocks(self):
            def make_catalog_place(place, projection):
                return {
                    key: place[key]
                    for key in {'id', 'revision_id', 'updated_at'}
                    | set(projection) & place.keys()
                }

            @mockserver.json_handler(
                '/eats-catalog-storage/internal/eats-catalog-storage'
                '/v1/places/updates',
            )
            def _eats_catalog_storage_places_updates(request):
                place_idx = len(self.catalog_places_sorted)
                for i in range(len(self.catalog_places_sorted)):
                    if (
                            self.catalog_places_sorted[i]['revision_id']
                            >= request.json['last_known_revision']
                    ):
                        place_idx = i
                        break
                places = [
                    make_catalog_place(place, request.json['projection'])
                    for place in self.catalog_places_sorted[
                        place_idx : place_idx + request.json['limit']
                    ]
                ]
                if places:
                    last_known_revision = places[-1]['revision_id']
                elif self.catalog_places_sorted:
                    last_known_revision = self.catalog_places_sorted[-1][
                        'revision_id'
                    ]
                else:
                    last_known_revision = 0
                return {
                    'places': places,
                    'last_known_revision': last_known_revision,
                }

            self.mock_places_updates = _eats_catalog_storage_places_updates

            @mockserver.json_handler(
                '/eats-catalog-storage/internal/eats-catalog-storage'
                '/v1/places/retrieve-by-ids',
            )
            def _eats_catalog_storage_retrieve_places(request):
                not_found_place_ids = []
                places = []
                for place_id in request.json['place_ids']:
                    if place_id in self.catalog_places:
                        places.append(
                            make_catalog_place(
                                self.catalog_places[place_id],
                                request.json['projection'],
                            ),
                        )
                    else:
                        not_found_place_ids.append(place_id)
                return {
                    'places': places,
                    'not_found_place_ids': not_found_place_ids,
                }

            self.mock_retrieve_places = _eats_catalog_storage_retrieve_places

            @mockserver.json_handler(
                '/eats-catalog-storage/internal/eats-catalog-storage'
                '/v1/delivery_zones/retrieve-by-place-ids',
            )
            def _eats_catalog_storage_retrieve_delivery_zones(request):
                assert set(request.json['projection']) == {
                    'enabled',
                    'place_id',
                    'working_intervals',
                }
                not_found_place_ids = []
                delivery_zones = []
                for place_id in request.json['place_ids']:
                    if place_id in self.delivery_zones:
                        delivery_zones.append(
                            {
                                'place_id': place_id,
                                'delivery_zones': self.delivery_zones[
                                    place_id
                                ],
                            },
                        )
                    else:
                        not_found_place_ids.append(place_id)
                return {
                    'delivery_zones': delivery_zones,
                    'not_found_place_ids': not_found_place_ids,
                }

            self.mock_retrieve_delivery_zones = (
                _eats_catalog_storage_retrieve_delivery_zones
            )

            @mockserver.json_handler('/eats-core/v1/places/info')
            def _eats_core_places_info(request):
                core_places = []
                for place_id in request.json['place_ids']:
                    if (
                            place_id in self.core_places
                            and self.core_places[place_id]['available']
                            is not None
                    ):
                        core_places.append(self.core_places[place_id])
                return (
                    {'payload': core_places}
                    if core_places
                    else mockserver.make_response(status=404)
                )

            self.mock_core_places_info = _eats_core_places_info

            @mockserver.json_handler('/eats-core/v1/places/disable')
            def _eats_core_places_disable(request):
                assert request.json['disable_details'] == {
                    'code': 100,
                    'comment': (
                        'Picker Dispatch: place_disable_offset_time exceeded'
                    ),
                }
                place_ids = request.json['place_ids']
                for place_id in place_ids:
                    self.disable_place(
                        place_id, request.json['disable_details']['code'],
                    )
                return {
                    'payload': {'disabled_places': place_ids, 'errors': []},
                }

            self.mock_places_disable = _eats_core_places_disable

            @mockserver.json_handler('/eats-core/v1/places/enable')
            def _eats_core_places_enable(request):
                place_ids = request.json['place_ids']
                for place_id in place_ids:
                    self.enable_place(place_id)
                return {'payload': {'enabled_places': place_ids, 'errors': []}}

            self.mock_places_enable = _eats_core_places_enable

        def disable_place(self, place_id, reason):
            self.catalog_places[place_id]['enabled'] = False
            core_place = self.core_places[place_id]
            core_place['available'] = False
            core_place['disable_details'] = {'reason': reason}

        def enable_place(self, place_id):
            self.catalog_places[place_id]['enabled'] = True
            core_place = self.core_places[place_id]
            core_place['available'] = True
            if 'disable_details' in core_place:
                del core_place['disable_details']

    return Environment()


@pytest.fixture(name='eats-picker-racks-mock', autouse=True)
def _mock_eats_picker_racks(mockserver):
    @mockserver.json_handler(
        '/eats-picker-racks/api/v1/fridge_and_freezer_info',
    )
    def _eats_picker_racks(_):
        return {'places_info': []}


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_picker_dispatch'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_place(get_cursor, now_utc):
    def do_create_place(
            place_id=1,
            revision_id=1,
            slug='place-slug',
            brand_id=1,
            country_id=1,
            region_id=1,
            time_zone='Europe/Moscow',
            city='Москва',
            working_intervals=None,
            enabled=True,
            updated_at=None,
            synchronized_at=None,
            auto_disabled_at=None,
            last_time_had_pickers=None,
    ):
        if working_intervals is None:
            working_intervals = [
                (now_utc(), now_utc() + datetime.timedelta(days=1)),
            ]
        if updated_at is None:
            updated_at = now_utc()
        if synchronized_at is None:
            synchronized_at = now_utc()
        working_intervals = [
            tuple(
                dateutil.parser.parse(item)
                if isinstance(item, str)
                else item
                if item.tzinfo is not None
                else item.replace(tzinfo=pytz.UTC)
                for item in working_interval
            )
            for working_interval in working_intervals
        ]
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_dispatch.places '
            '(id, revision_id, slug, brand_id, country_id, region_id, '
            'time_zone, city, enabled, updated_at, synchronized_at, '
            'auto_disabled_at, last_time_had_pickers, working_intervals) '
            'SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            'array_agg((f, t)::eats_picker_dispatch.working_interval) '
            'FROM UNNEST(%s) AS i (f timestamptz, t timestamptz)',
            [
                place_id,
                revision_id,
                slug,
                brand_id,
                country_id,
                region_id,
                time_zone,
                city,
                enabled,
                updated_at,
                synchronized_at,
                auto_disabled_at,
                last_time_had_pickers,
                working_intervals,
            ],
        )

    return do_create_place


@pytest.fixture()
def get_places(get_cursor):
    def do_get_places(place_ids=None):
        cursor = get_cursor()
        cursor.execute(
            'SELECT '
            'id, revision_id, slug, brand_id, country_id, region_id, '
            'time_zone, city, '
            'array('
            '  SELECT array[working_interval.interval_from,'
            '               working_interval.interval_to] '
            '  FROM UNNEST(working_intervals) working_interval'
            ') working_intervals, enabled, updated_at, '
            'synchronized_at, auto_disabled_at, last_time_had_pickers '
            'FROM eats_picker_dispatch.places '
            f'{"WHERE id = ANY(%s) " if place_ids else ""}'
            'ORDER BY id',
            [place_ids],
        )
        return cursor.fetchall()

    return do_get_places
