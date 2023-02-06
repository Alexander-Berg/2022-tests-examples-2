import bson
from geobus_tools import geobus  # pylint: disable=import-error
import pytest

from tests_plugins import utils


TIMELEFTS_CHANNEL = 'channel:drw:timelefts'
DRIVERS_COUNT = 11


@pytest.mark.now('2022-04-29T05:11:01+03:00')
@pytest.mark.config(
    SAFETY_EVENTS_WATCHER_DETECT_DEVIATIONS_SETTINGS={
        'enabled': True,
        'lru_cache_size': 100,
        'number_of_deviations_to_detect': 10,
        'close_to_destination_distance_left_meters': 500,
        'close_to_destination_straight_line_meters': 500,
        'minimum_distance_left_increase_meters': 50,
        'order_classes_to_process': ['business'],
        'countries_to_process': ['Россия'],
        'enable_chatterbox': True,
        'tracker_queue': 'TAXIUNSAFEROAD',
        'tracker_org_id': '0',
        'tickets_creation_interval_msk_time': {
            'begin_hour': 20,
            'end_hour': 8,
        },
        'tickets_creation_interval_order_timezone_time': {
            'begin_hour': 20,
            'end_hour': 8,
        },
        'user_is_female_probability_threshold': 0.5,
        'enable_female_drivers_detection': True,
        'disable_call_center_orders': True,
    },
)
async def test_detect_deviations_task(
        taxi_safety_events_watcher, mockserver, redis_store, testpoint, now,
):
    timestamp = int(utils.timestamp(now))

    @testpoint('detect_deviations-started_work')
    def start_work(arg):
        return arg

    @testpoint('detect_deviations-got_geobus_message')
    def got_message(arg):
        return arg

    @testpoint('detect_deviations-deviation_detected')
    def detect_deviation(arg):
        return arg

    @testpoint('detect_deviations-deviation_processed')
    def process_deviation(arg):
        return arg

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_fields(request):
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(
                {
                    'document': {
                        'order': {
                            'application': 'android',
                            'nz': 'kaliningrad',
                            'performer': {
                                'db_id': 'some_park',
                                'uuid': 'some_id',
                            },
                            'request': {
                                'class': ['business'],
                                'destinations': [{'country': 'Россия'}],
                            },
                            'user_uid': 'some_uid',
                        },
                    },
                },
            ),
        )

    @mockserver.handler('/taxi-tariffs/v1/tariff_zones')
    def _mock_taxi_tariffs(request):
        return mockserver.make_response(
            status=200,
            json={
                'zones': [
                    {
                        'name': 'kaliningrad',
                        'time_zone': 'Europe/Kaliningrad',
                        'country': 'rus',
                    },
                ],
            },
        )

    @mockserver.json_handler('/taxi-api-tracker/v2/issues')
    def _issues(request):
        return mockserver.make_response(
            status=201, json={'key': 'TAXIUNSAFEROAD-1', 'id': 'some_id'},
        )

    @mockserver.handler('/chatterbox/v1/tasks')
    def _mock_chatterbox(request):
        return mockserver.make_response(
            status=200, json={'id': 'chat_id', 'status': 'created'},
        )

    @mockserver.handler('/crypta-api/portal/me/profile')
    def _mock_crypta(request):
        return mockserver.make_response(
            status=200,
            json={
                'gender': {
                    'female': 0.804365,
                    'male': 0.195634,
                    'timestamp': 1654075871,
                },
            },
        )

    @mockserver.handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        return mockserver.make_response(
            status=200,
            json={
                'profiles': [
                    {
                        'data': {'full_name': {'middle_name': 'Андреевич'}},
                        'park_driver_profile_id': 'some_id',
                    },
                ],
            },
        )

    async with taxi_safety_events_watcher.spawn_task('detect-deviations'):
        await start_work.wait_call()

        for i in range(DRIVERS_COUNT):
            timelefts = {
                'timestamp': timestamp * 1000,
                'update_timestamp': timestamp * 1000,
                'tracking_type': 'RouteTracking',
                'contractor_id': 'dbid_uuid{}'.format(i),
                'route_id': '0',
                'adjusted_pos': [
                    37.65 + (i + 1) * 0.02,
                    55.73 + (i + 1) * 0.02,
                ],
                'timeleft_data': [
                    {
                        'destination_position': [37.66, 55.71],
                        'distance_left': 2500 + i * 100,
                        'service_id': (
                            'processing:driving'
                            if i == 0
                            else 'processing:transporting'
                        ),
                        'order_id': 'order_id{}'.format(0),
                        'time_left': 34235,
                    },
                ],
                'adjusted_segment_index': 0,
            }

            message = {'timestamp': timestamp, 'payload': [timelefts]}

            redis_store.publish(
                TIMELEFTS_CHANNEL,
                geobus.timelefts.serialize_message(message, now),
            )

        for i in range(DRIVERS_COUNT):
            await got_message.wait_call()

        await detect_deviation.wait_call()

        await process_deviation.wait_call()

    assert (
        [
            _issues.next_call()['request'].json
            for _ in range(_issues.times_called)
        ]
        == [
            {
                'description': '',
                'queue': 'TAXIUNSAFEROAD',
                'summary': 'Urgent - Отклонение от маршрута - order_id0',
                'unique': 'order_id0',
            },
        ]
    )

    assert (
        [
            _mock_chatterbox.next_call()['request'].json
            for _ in range(_mock_chatterbox.times_called)
        ]
        == [
            {
                'external_id': 'TAXIUNSAFEROAD-1',
                'metadata': {
                    'update_meta': [
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'order_id0',
                        },
                    ],
                    'update_tags': [
                        {
                            'change_type': 'add',
                            'tag': 'taxi_urgent_unsafe_road',
                        },
                    ],
                },
                'type': 'startrack',
            },
        ]
    )
