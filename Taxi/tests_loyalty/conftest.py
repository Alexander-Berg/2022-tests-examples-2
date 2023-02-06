# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from loyalty_plugins import *  # noqa: F403 F401
# pylint: disable=wrong-import-order
import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(
            pytest.mark.geoareas(filename='db_geoareas.json', db_format=True),
        )
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


@pytest.fixture(name='driver_metrics_storage', autouse=True)
def _driver_metrics_storage(mockserver):
    class DriverMetricsStorageContext:
        def __init__(self):
            self.wallet_balance_values = {}
            self.priorities_values = {}
            self.events_processed_response = {}
            self.events_processed_response_code = 200

        def set_wallet_balance_value(
                self, unique_driver_id, ts_from, ts_to, value,
        ):
            self.wallet_balance_values[
                'value:' + unique_driver_id + ts_from + ts_to
            ] = value

        def set_events_processed_response(self, response, code):
            self.events_processed_response = response
            self.events_processed_response_code = code

        def set_priority_value(
                self, tariff_zone, unique_driver_id, tags, priority,
        ):
            self.priorities_values[
                tariff_zone + unique_driver_id + ''.join(tags)
            ] = priority

    context = DriverMetricsStorageContext()
    context.set_wallet_balance_value(
        'test_unique_driver_id',
        '2019-04-01T06:10:00+0500',
        '2019-04-01T06:10:00+0500',
        98,
    )

    def mock_wallet_balance(context, request):
        udids = request.json.get('udids', ['empty'])
        unique_driver_id = udids[0]
        ts_from = request.json['ts_from']
        ts_to = request.json['ts_to']
        key = 'value:' + unique_driver_id + ts_from + ts_to
        if key not in context.wallet_balance_values:
            return []
        return [
            {
                'udid': unique_driver_id,
                'value': context.wallet_balance_values[key],
                'last_ts': ts_from,
            },
        ]

    def mock_events_processed(context, request):
        response_code = context.events_processed_response_code
        if response_code != 200:
            return mockserver.make_response('Error', response_code)
        return context.events_processed_response

    def mock_priority_fetch_bulk(context, request):
        chunks = request.json['chunks']
        result = {'priority_values': []}
        for chunk in chunks:
            tariff_zone = chunk['tariff_zone']
            drivers = chunk['drivers']
            for driver in drivers:
                unique_driver_id = driver['unique_driver_id']
                tags = driver['tags']
                try:
                    priority = context.priorities_values[
                        tariff_zone + unique_driver_id + ''.join(tags)
                    ]
                    result['priority_values'].append(
                        {
                            'unique_driver_id': unique_driver_id,
                            'value': priority,
                        },
                    )
                except KeyError:
                    result['priority_values'].append(
                        {'unique_driver_id': unique_driver_id},
                    )
        return result

    @mockserver.json_handler('/driver-metrics-storage/v1/wallet/balance')
    def _mock_wallet_balance(request):
        return mock_wallet_balance(context, request)

    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    def _mock_events_processed(request):
        return mock_events_processed(context, request)

    @mockserver.json_handler('/driver-metrics-storage/v1/priority/fetch-bulk')
    def _mock_priority_fetch_bulk(request):
        return mock_priority_fetch_bulk(context, request)

    return context


@pytest.fixture(name='driver_orders', autouse=True)
def _driver_orders(mockserver):
    class DriverOrdersContext:
        def __init__(self):
            self.bulk_retrieve_response_code = 200
            self.bulk_retrieve_orders = {}

        def set_bulk_retrieve_response_code(self, code):
            self.bulk_retrieve_response_code = code

        def add_bulk_retrieve_order(self, order_id, order):
            self.bulk_retrieve_orders[order_id] = order

    context = DriverOrdersContext()

    def mock_bulk_retrieve(context, request):
        response_code = context.bulk_retrieve_response_code
        if response_code != 200:
            return mockserver.make_response('Error', response_code)
        orders = []
        order_ids = set()
        for order_id in request.json['query']['park']['order']['ids']:
            order = {'id': order_id}
            if order_id in context.bulk_retrieve_orders:
                order['order'] = context.bulk_retrieve_orders[order_id]
            orders.append(order)
            order_ids.add(order_id)
        assert len(orders) == len(order_ids)
        return {'orders': orders}

    @mockserver.json_handler('/driver-orders/v1/parks/orders/bulk_retrieve')
    def _mock_bulk_retrieve(request):
        return mock_bulk_retrieve(context, request)

    return context


@pytest.fixture(name='mock_driver_ratings', autouse=True)
def _driver_ratings(mockserver):
    service = '/driver-ratings'
    v1_retrieve = '/v1/driver/ratings/retrieve'

    class DriverRatingsContext:
        def __init__(self):
            self.consumer = 'loyalty'
            self.ratings = {}

        def set_rating(self, udid, rating):
            self.ratings[udid] = rating

    context = DriverRatingsContext()

    @mockserver.json_handler(service + v1_retrieve)
    def _mock_v1_retrieve(request):
        assert context.consumer == request.args.get('consumer')
        assert request.json.get('id_in_set')
        udid = request.json['id_in_set'][0]
        if udid not in context.ratings:
            return mockserver.make_response('not_found', 404)
        return {
            'ratings': [
                {
                    'unique_driver_id': udid,
                    'data': {'rating': context.ratings[udid]},
                },
            ],
        }

    return context


@pytest.fixture(name='unique_drivers', autouse=True)
def _unique_drivers(mockserver):
    class UniqueDriversContext:
        def __init__(self):
            self.unique_driver_ids = {}

        def set_unique_driver(self, db_id, uuid, unique_driver_id):
            self.unique_driver_ids[
                'UniqueDriver:' + db_id + '_' + uuid
            ] = unique_driver_id

    context = UniqueDriversContext()
    context.set_unique_driver('test_db', 'test_uuid', 'test_unique_driver_id')

    def mock_retrieve_by_profiles(context, request):
        token = request.headers.get('X-Ya-Service-Ticket')
        if token is None:
            return mockserver.make_response('{"message": "unauthorized"}', 401)
        profile_id_in_set = request.json.get('profile_id_in_set')
        response_uniques = []
        for profile_id in profile_id_in_set:
            record = {'park_driver_profile_id': profile_id}
            key = 'UniqueDriver:' + profile_id
            if key in context.unique_driver_ids:
                record['data'] = {
                    'unique_driver_id': context.unique_driver_ids[key],
                }
            response_uniques.append(record)
        return {'uniques': response_uniques}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_retrieve_by_profiles(request):
        return mock_retrieve_by_profiles(context, request)

    return context


@pytest.fixture(name='tags', autouse=True)
def _tags(mockserver):
    class Tags:
        def __init__(self):
            self.provider_id = 'loyalty'
            self.remove_tags = ['bronze', 'silver', 'gold', 'platinum']
            self.append_tag = None

        def set_append_tag(self, append_tag):
            self.append_tag = append_tag

    context = Tags()

    def _get_tags(json):
        return [tag['name'] for tag in json[0].get('tags')]

    @mockserver.json_handler('/tags/v2/upload')
    def _mock_tags_v2_upload(request):
        assert request.json.get('provider_id') == context.provider_id
        assert _get_tags(request.json.get('append')) == [context.append_tag]
        loyalty_statuses = context.remove_tags
        loyalty_statuses.remove(context.append_tag)
        assert sorted(_get_tags(request.json.get('remove'))) == sorted(
            loyalty_statuses,
        )
        return {'status': 'ok'}

    return context
