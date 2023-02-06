import json

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from order_events_producer_plugins import *  # noqa: IS001 F403 F401
import pytest


@pytest.fixture
def taxi_order_core_mock(mockserver, load_json):
    class Mocks:
        _expect_times_called = 0
        data = load_json('order_core.json')

        @staticmethod
        @mockserver.json_handler('/order-core/v1/tc/order-info')
        def _order_info(request):
            if Mocks._expect_times_called <= 0:
                return mockserver.make_response(
                    json.dumps(
                        {'code': '500', 'message': 'Unexpected mock call'},
                    ),
                    500,
                )
            Mocks._expect_times_called -= 1
            return mockserver.make_response(response=json.dumps(Mocks.data))

        @staticmethod
        def expect_times_called(times):
            Mocks._expect_times_called = times

        @staticmethod
        def verify():
            return Mocks._expect_times_called == 0

    return Mocks()


@pytest.fixture
def taxi_rider_metrics_storage_ctx():
    class RiderMetricsStorageContext:
        def __init__(self):
            self.times_called = 0
            self._expect_times_called = 0
            self.calls = []
            self.last_called_name = 'none'
            self.last_called_tags = 'none'
            self.last_called_user_id = 'none'
            self.last_extra_data = 'none'
            self.fail_count = 0

        def expect_times_called(self, times):
            self._expect_times_called = times

        def set_fail_count(self, count):
            self.fail_count = count

        def verify(self):
            return self._expect_times_called == self.times_called

    return RiderMetricsStorageContext()


@pytest.fixture
def taxi_rider_metrics_storage_mock(
        # pylint: disable=redefined-outer-name
        mockserver,
        taxi_rider_metrics_storage_ctx,
):
    @mockserver.json_handler('/rider-metrics-storage/v1/event/new')
    def _event_new(request):
        # pylint: disable=redefined-outer-name
        taxi_rider_metrics_storage_ctx.calls.append(request.json)
        taxi_rider_metrics_storage_ctx.times_called += 1
        taxi_rider_metrics_storage_ctx.last_called_name = request.json[
            'descriptor'
        ]['name']
        taxi_rider_metrics_storage_ctx.last_called_user_id = request.json[
            'user_id'
        ]
        if 'tags' in request.json['descriptor']:
            taxi_rider_metrics_storage_ctx.last_called_tags = request.json[
                'descriptor'
            ]['tags']
        if 'extra_data' in request.json:
            taxi_rider_metrics_storage_ctx.last_extra_data = request.json[
                'extra_data'
            ]
        if taxi_rider_metrics_storage_ctx.fail_count > 0:
            taxi_rider_metrics_storage_ctx.fail_count -= 1
            return mockserver.make_response('{}', 429)
        return mockserver.make_response('{}', 200)

    @mockserver.json_handler('/rider-metrics-storage/v1/event/new/bulk')
    def _event_new_bulk(request):
        taxi_rider_metrics_storage_ctx.calls.append(request.json)
        taxi_rider_metrics_storage_ctx.times_called += 1
        if taxi_rider_metrics_storage_ctx.fail_count > 0:
            taxi_rider_metrics_storage_ctx.fail_count -= 1
            return mockserver.make_response('{}', 429)
        events = request.json['events']
        response_events = [
            {'idempotency_token': event['idempotency_token']}
            for event in events
        ]
        return mockserver.make_response(
            json.dumps({'events': response_events}), 200,
        )

    return taxi_rider_metrics_storage_ctx


class OrderEvent:
    def __init__(self, **kwargs):
        self._attributes = {
            'timestamp': 1571253356.872,
            'alias': '39cea0e974a738abbe4cd087eaa85d7e',
            'order_id': 'b2f366eb37ba19a88a14a35345c8af5a',
            'event_index': 1,
            'created': 1571253353.757,
            'updated': 1571253356.545,
            'status_updated': 1571253356.368,
            'status': 'cancelled',
            'source_geopoint': [30.14590537507627, 59.5819290068952],
            'payment_type': 'cash',
            'nz': 'moscow',
            'user_id': '03def2593a934fd6489bbbeb35efcce8',
            'user_phone_id': '04def2593a934fd6489bbbeb',
            'user_locale': 'ru',
            'user_agent': (
                'yandex-taxi/3.120.1.104493 '
                'Android/8.0.0 (samsung; SM-G935F)'
            ),
            'user_tags': ['user_tag'],
            'tags': [],
            'db_id': None,
            'driver_id': None,
            'driver_uuid': None,
            'request_classes': ['econom'],
            'destinations_geopoint': [[30.102516, 59.556206]],
            'event_key': 'handle_cancel_by_user',
            'event_reason': None,
            'topic': None,
            'personal_phone_id': None,
            'phone_type': None,
            'performer_tariff_class': None,
            'idempotency_token': None,
        }
        for key, value in kwargs.items():
            self._attributes[key] = value

    def as_tskv(self):
        def as_tskv_value(value):
            if isinstance(value, str):
                return value
            return json.dumps(value)

        return 'tskv\ttskv_format=order-events\t' + '\t'.join(
            [
                '{}={}'.format(k, as_tskv_value(v))
                for k, v in self._attributes.items()
                if v is not None
            ],
        )

    def as_json(self):
        json_attributes = {}
        for key, value in self._attributes.items():
            if value is not None:
                json_attributes[key] = value
        return json.dumps(json_attributes)

    def cast(self, restype):
        if restype == 'json':
            return self.as_json()
        if restype == 'tskv':
            return self.as_tskv()
        raise Exception('Unknown cast type: \'{}\''.format(restype))


class OrderEventsGen:
    def __init__(self, *order_events):
        self.order_events = order_events

    def cast(self, cast_into=None):
        assert cast_into is not None
        return (
            '\n'.join(
                [
                    order_event.cast(cast_into)
                    for order_event in self.order_events
                ],
            )
            + '\n'
        )


@pytest.fixture
def order_events_gen():
    return OrderEventsGen


@pytest.fixture
def make_order_event():
    return OrderEvent


@pytest.fixture(name='metrics_snapshot', autouse=True)
def _metrics_snapshot(taxi_order_events_producer_monitor):
    class Metrics:
        def __init__(self):
            self._snapshot_metrics = None

        async def take_snapshot(self):
            self._snapshot_metrics = (
                await taxi_order_events_producer_monitor.get_metrics()
            )

        async def get_metrics_diff(self):
            assert self._snapshot_metrics, (
                'You should call metrics_snapshot.take_snapshot() in '
                'your test before get_metrics_diff call'
            )

            metrics = await taxi_order_events_producer_monitor.get_metrics()

            class MetricsDiff:
                def __init__(self, old_metrics, new_metrics):
                    self._old_metrics = old_metrics
                    self._new_metrics = new_metrics

                def new_value(self):
                    assert not isinstance(
                        self._new_metrics, dict,
                    ), 'You should call new_value only on value node'
                    return self._new_metrics

                def old_value(self):
                    assert not isinstance(
                        self._old_metrics, dict,
                    ), 'You should call old_value only on value node'
                    return self._old_metrics

                def __getitem__(self, arg):
                    assert arg in self._new_metrics
                    return MetricsDiff(
                        self._old_metrics.get(arg, {})
                        if self._old_metrics is not None
                        else {},
                        self._new_metrics[arg],
                    )

                def get_diff(self):
                    if isinstance(self._new_metrics, dict):
                        res = {}
                        for key, value in self._new_metrics.items():
                            if key.startswith('$'):
                                continue
                            res[key] = MetricsDiff(
                                self._old_metrics.get(key, {}), value,
                            ).get_diff()
                        return res
                    return self._new_metrics - (self._old_metrics or 0)

            return MetricsDiff(self._snapshot_metrics, metrics)

    return Metrics()


@pytest.fixture(name='tags_upload_comparer', autouse=True)
def _tags_upload_comparer():
    class TagsComparer:
        def __init__(self, expected_tags):
            self._expected_tags = expected_tags
            self._expected_tags.sort(key=lambda x: (x['name'], x['entity']))

        def __eq__(self, incoming_tags):
            incoming_tags.sort(key=lambda x: (x['name'], x['entity']))
            assert self._expected_tags == incoming_tags
            return self._expected_tags == incoming_tags

    return TagsComparer
