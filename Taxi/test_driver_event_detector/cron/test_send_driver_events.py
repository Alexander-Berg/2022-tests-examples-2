# pylint: disable=redefined-outer-name
import concurrent.futures

import pytest

from driver_event_detector.generated.cron import run_cron


@pytest.fixture
def lb_topic_test_file():
    return 'lb-topic-data.json'


@pytest.fixture
def logbroker_mock(patch, mock, monkeypatch, load_json, lb_topic_test_file):
    class DummyPqlibApi:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result('start result')
            return future

        def stop(self):
            pass

        def create_consumer(
                self, consumer_configurator, credentials_provider=None,
        ):
            return DummyPqlibConsumer()

    class DummyStartConsumerResult:
        @staticmethod
        def HasField(field):  # pylint: disable=invalid-name
            if field == 'init':
                return True
            return False

    class DummyPqlibConsumer:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result(DummyStartConsumerResult)
            return future

        def stop(self):
            future = concurrent.futures.Future()
            future.set_result('stop result')
            return future

        def commit(self, cookie):
            pass

        def next_event(self):
            pass

    @patch('driver_event_detector.lib.logbroker.Logbroker._create_api')
    def _create_api(*args, **kwargs):
        return DummyPqlibApi()

    @patch('driver_event_detector.lib.logbroker.TopicConsumer.read')
    def _read():
        data = load_json(lb_topic_test_file)
        for batch in data:
            yield (message for message in batch)


@pytest.mark.now('2022-02-16T08:10:00+0000')
@pytest.mark.config(
    DRIVER_EVENT_DETECTOR_CONFIGS={
        'is_event_sender_running': True,
        'lb_topic': 'taxi/driver-event-detector/testing/cron-kd-drivers',
        'lb_client_id': '/taxi/consumers/testing/driver-event-detector',
        'lb_timeout': 1,
        'lb_num_retries': 1,
        'time_of_obsolescence': 300,
        'sending_limit': 900,
    },
)
@pytest.mark.parametrize('lb_topic_test_file', ['topic-kd-drivers.json'])
async def test_send_driver_events(
        logbroker_mock, mock_driver_metrics_storage, lb_topic_test_file,
):
    # noqa: E501
    sent_dms_events = []

    @mock_driver_metrics_storage('/v1/event/new/bulk')
    async def _handler(request):
        sent_dms_events.extend(request.json['events'])
        return {
            'events': [{'idempotency_token': event['idempotency_token']}]
            for event in request.json['events']
        }

    await run_cron.main(['driver_event_detector.crontasks.send_driver_events'])

    assert sent_dms_events == [
        {
            'idempotency_token': '2fa6946cbfd1aedb2c4e5ebc9fb3beef',
            'type': 'kd_seen',
            'unique_driver_id': '5ac60e8ce342c7944b89957c',
            'created': '2022-02-16T11:06:14+03:00',
            'park_driver_profile_id': '6a757d94fd354135a2b779db8b8ef411_d54b43ebae064ee31267c18fbf858c92',  # noqa: E501
            'tariff_zone': 'moscow',
        },
        {
            'idempotency_token': '17ca486dea63cfb721d563b70ba34b45',
            'type': 'kd_seen',
            'unique_driver_id': '56f3ee667c0aa65c446aee97',
            'created': '2022-02-16T11:06:14+03:00',
            'park_driver_profile_id': '58c5017882f2423b847d2a4e96091752_c921178697fb45e599be4c731434d6dd',  # noqa: E501
            'tariff_zone': 'moscow',
        },
        # Here other event for udid="56f3ee667c0aa65c446aee97"
        # is ignored due to sending_limit=900
        {
            'idempotency_token': 'a6169164e83a8e31ae6582115b3a6ce0',
            'type': 'kd_seen',
            'unique_driver_id': '606886798fe28d5ce494691f',
            'created': '2022-02-16T11:06:15+03:00',
            'park_driver_profile_id': 'b1c0eb98a81149e48e8eaa95da7b807b_7e78eaeee3e2d9736683bcb0e6b9b6ff',  # noqa: E501
            'tariff_zone': 'moscow',
        },
        {
            'idempotency_token': 'bbd3627f8b7d2b9b5c3665ec2e252e51',
            'type': 'kd_seen',
            'unique_driver_id': '606886798fe28d5ce494691f',
            'created': '2022-02-16T11:06:15+03:00',
            'park_driver_profile_id': 'f434953455af4784b3ebfd3bad5a4259_f78543e52c7a4af5b48587ccd0f1defe',  # noqa: E501
            'tariff_zone': 'moscow',
        },
    ]


@pytest.mark.now('2022-02-16T08:10:00+0000')
@pytest.mark.config(
    DRIVER_EVENT_DETECTOR_CONFIGS={
        'is_event_sender_running': True,
        'lb_topic': 'taxi/driver-event-detector/testing/cron-kd-drivers',
        'lb_client_id': '/taxi/consumers/testing/driver-event-detector',
        'lb_timeout': 1,
        'lb_num_retries': 1,
        'time_of_obsolescence': 300,
        'sending_limit': 0,
    },
)
@pytest.mark.parametrize(
    'lb_topic_test_file', ['topic-kd-drivers-idempotency.json'],
)
async def test_idempotency(
        logbroker_mock, mock_driver_metrics_storage, lb_topic_test_file,
):
    sent_dms_events = []

    @mock_driver_metrics_storage('/v1/event/new/bulk')
    async def _handler(request):
        sent_dms_events.extend(request.json['events'])
        return {
            'events': [{'idempotency_token': event['idempotency_token']}]
            for event in request.json['events']
        }

    await run_cron.main(['driver_event_detector.crontasks.send_driver_events'])

    assert len(sent_dms_events) == 2
    first_event, second_event = sent_dms_events  # pylint: disable=W0632

    assert first_event['unique_driver_id'] == second_event['unique_driver_id']
    # Because sending_limit=0 and these events happened in one minute
    assert (
        first_event['idempotency_token'] == second_event['idempotency_token']
    )
