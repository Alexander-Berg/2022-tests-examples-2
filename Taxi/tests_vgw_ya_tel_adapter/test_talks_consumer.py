import logging
import typing

import pytest

logger = logging.getLogger(__name__)


def _rich_stats(stats: typing.Dict) -> typing.Dict:
    new_stats = {
        'msg.extracted.ok.1min': 0,
        'msg.extracted.error.1min': 0,
        'msg.skipped.unparsed.1min': 0,
        'msg.skipped.bad_call_id.1min': 0,
        'msg.skipped.bad_redirection_id.1min': 0,
        'msg.skipped.bad_datetime.1min': 0,
        'msg.skipped.bad_length.1min': 0,
        'processing.total_talks_saved.1min': 0,
        'processing.batch_size.1min.max': 0,
        'processing.is_broken': 0,
    }
    new_stats.update(stats)
    return new_stats


def _check_stats(stats: typing.Dict, expected_stats: typing.Dict):
    for stat_key, expected_value in expected_stats.items():
        keys = stat_key.split('.')
        value = stats['talks-consumer']
        for key in keys:
            value = value[key]
        logger.info('Checking stat path %s', stat_key)
        assert value == expected_value
        logger.info('ok')


@pytest.mark.parametrize(
    (
        'messages',
        'expected_processed',
        'expected_talks_request',
        'expected_stats',
    ),
    (
        (
            ['message_min_1.json', 'message_full.json'],
            2,
            'expected_talks_request.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.extracted.error.1min': 1,
                    'processing.total_talks_saved.1min': 2,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_min_2.json', 'message_full.json'],
            2,
            'expected_talks_request.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.extracted.error.1min': 1,
                    'processing.total_talks_saved.1min': 2,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_min_3.json', 'message_full.json'],
            2,
            'expected_talks_request.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.extracted.error.1min': 1,
                    'processing.total_talks_saved.1min': 2,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_min_4.json', 'message_full.json'],
            2,
            'expected_talks_request.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.extracted.error.1min': 1,
                    'processing.total_talks_saved.1min': 2,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_bad_datetime_1.json', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.bad_datetime.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_bad_datetime_2.json', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.bad_datetime.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_bad_length.json', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.bad_length.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_bad_call_id.json', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.bad_call_id.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_no_redirection_id.json', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.bad_redirection_id.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['message_bad_redirection_id.json', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.bad_redirection_id.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['{}', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.unparsed.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['{', 'message_full.json'],
            1,
            'expected_talks_request_single.json',
            _rich_stats(
                {
                    'msg.extracted.ok.1min': 1,
                    'msg.skipped.unparsed.1min': 1,
                    'processing.total_talks_saved.1min': 1,
                    'processing.batch_size.1min.max': 2,
                },
            ),
        ),
        (
            ['{'],
            0,
            None,
            _rich_stats(
                {
                    'msg.skipped.unparsed.1min': 1,
                    'processing.batch_size.1min.max': 1,
                },
            ),
        ),
    ),
)
@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_TALKS_LB_SETTINGS={
        'max_batch_size': 10,
        'send_delay_ms': 0,
        'retrying_policy': {
            'min_retry_delay_ms': 10,
            'delay_multiplier': 1.6,
            'max_random_delay_ms': 20,
            'max_possible_delay_ms': 1000,
        },
    },
)
async def test_consume_messages(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        mockserver,
        load_json,
        testpoint,
        lb_message_sender,
        messages,
        expected_processed,
        expected_talks_request,
        expected_stats,
):
    @mockserver.json_handler('/vgw-api/v1/talks/')
    def mock_talks(request):
        assert request.json == load_json(expected_talks_request)
        return mockserver.make_response(status=200, json={})

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    @testpoint('talks-consumer-processed')
    def processed(data):
        return

    await lb_message_sender.send(messages, 'talks')

    async with taxi_vgw_ya_tel_adapter.spawn_task('talks-consumer'):
        messages_processed = await processed.wait_call()
        assert messages_processed['data'] == expected_processed
        assert mock_talks.times_called == int(bool(expected_talks_request))
        for _ in messages:
            await commit.wait_call()

        stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics(
            'talks-consumer',
        )
        _check_stats(stats, expected_stats)


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_TALKS_LB_SETTINGS={
        'max_batch_size': 2,
        'send_delay_ms': 0,
        'retrying_policy': {
            'min_retry_delay_ms': 10,
            'delay_multiplier': 1.6,
            'max_random_delay_ms': 20,
            'max_possible_delay_ms': 1000,
        },
    },
)
async def test_batch(
        taxi_vgw_ya_tel_adapter,
        mockserver,
        load_json,
        testpoint,
        lb_message_sender,
):
    idx = 0
    expected_requests = [
        'expected_talks_request.json',
        'expected_talks_request_single.json',
    ]

    @mockserver.json_handler('/vgw-api/v1/talks/')
    def mock_talks(request):
        nonlocal idx
        assert request.json == load_json(expected_requests[idx])
        idx += 1
        return mockserver.make_response(status=200, json={})

    @testpoint('talks-consumer-processed')
    def processed(data):
        return

    messages = ['message_min_1.json', 'message_full.json', 'message_full.json']
    await lb_message_sender.send(messages, 'talks')

    async with taxi_vgw_ya_tel_adapter.spawn_task('talks-consumer'):
        for i in range(2):
            messages_processed = await processed.wait_call()
            assert messages_processed['data'] == 2 - i

    assert mock_talks.times_called == 2


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_TALKS_LB_SETTINGS={
        'max_batch_size': 10,
        'send_delay_ms': 0,
        'retrying_policy': {
            'min_retry_delay_ms': 10,
            'delay_multiplier': 2,
            'max_random_delay_ms': 0,
            'max_possible_delay_ms': 100,
        },
    },
)
async def test_retry_delay(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        testpoint,
        mock_vgw_api,
):
    await taxi_vgw_ya_tel_adapter.invalidate_caches()
    sleep_delays = list()

    @testpoint('talks-consumer-loop-sleep')
    def sleep(data):
        sleep_delays.append(data)

    async with taxi_vgw_ya_tel_adapter.spawn_task('talks-consumer'):
        for _ in range(5):
            await sleep.wait_call()

    assert sleep_delays == [10, 20, 40, 80, 100]
    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics('talks-consumer')
    assert stats['talks-consumer']['processing']['total_sleep_ms'][
        '1min'
    ] == sum(sleep_delays)


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_TALKS_LB_SETTINGS={
        'max_batch_size': 10,
        'send_delay_ms': 0,
        'retrying_policy': {
            'min_retry_delay_ms': 10,
            'delay_multiplier': 2,
            'max_random_delay_ms': 0,
            'max_possible_delay_ms': 100,
        },
    },
)
async def test_fail_retry_delay(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        testpoint,
        mock_vgw_api_fail,
        lb_message_sender,
):
    await taxi_vgw_ya_tel_adapter.invalidate_caches()
    sleep_delays = list()

    @testpoint('talks-consumer-loop-sleep')
    def sleep(data):
        sleep_delays.append(data)

    await lb_message_sender.send('message_full.json', 'talks')

    async with taxi_vgw_ya_tel_adapter.spawn_task('talks-consumer'):
        for _ in range(5):
            await sleep.wait_call()

    assert mock_vgw_api_fail.talks.times_called >= 5
    assert sleep_delays == [10, 20, 40, 80, 100]
    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics('talks-consumer')
    assert stats['talks-consumer']['processing']['total_sleep_ms'][
        '1min'
    ] == sum(sleep_delays)
    assert stats['talks-consumer']['processing']['is_broken'] == 1


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_TALKS_LB_SETTINGS={
        'max_batch_size': 10,
        'send_delay_ms': 0,
        'retrying_policy': {
            'min_retry_delay_ms': 100,
            'delay_multiplier': 1,
            'max_random_delay_ms': 20,
            'max_possible_delay_ms': 1000,
        },
    },
)
async def test_delay_jitter(taxi_vgw_ya_tel_adapter, testpoint, mock_vgw_api):
    await taxi_vgw_ya_tel_adapter.invalidate_caches()
    sleep_delays = list()

    @testpoint('talks-consumer-loop-sleep')
    def sleep(data):
        sleep_delays.append(data)

    async with taxi_vgw_ya_tel_adapter.spawn_task('talks-consumer'):
        for _ in range(7):
            await sleep.wait_call()

    for i in range(1, len(sleep_delays)):
        assert sleep_delays[i] - sleep_delays[i - 1] <= 20  # max_random_delay


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_TALKS_LB_SETTINGS={
        'max_batch_size': 1,
        'send_delay_ms': 10,
        'retrying_policy': {
            'min_retry_delay_ms': 10,
            'delay_multiplier': 2,
            'max_random_delay_ms': 0,
            'max_possible_delay_ms': 100,
        },
    },
)
async def test_finish_delay(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        testpoint,
        mock_vgw_api,
        lb_message_sender,
):
    await taxi_vgw_ya_tel_adapter.invalidate_caches()

    @testpoint('talks-consumer-finish-sleep')
    def sleep(data):
        assert data == 10

    await lb_message_sender.send(['message_full.json'] * 5, 'talks')

    async with taxi_vgw_ya_tel_adapter.spawn_task('talks-consumer'):
        for _ in range(5):
            await sleep.wait_call()

    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics('talks-consumer')
    assert (
        stats['talks-consumer']['processing']['total_sleep_ms']['1min'] == 50
    )
