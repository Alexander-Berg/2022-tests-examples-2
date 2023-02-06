# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import logging
import typing

from google.protobuf import timestamp_pb2
import phonecheck_message_pb2
import pytest
import telephony_platform_pb2 as tel_pb

from tests_vgw_ya_tel_adapter import consts

logger = logging.getLogger(__name__)


def _rich_stats(stats: typing.Dict) -> typing.Dict:
    new_stats = {
        'msg.set_quarantine.1min': 0,
        'msg.skipped.no_action.1min': 0,
        'msg.skipped.unparsed.1min': 0,
        'msg.skipped.old.1min': 0,
        'msg.skipped.not_found.1min': 0,
        'msg.skipped.ya_tel_error.1min': 0,
        'total_commited.1min': 0,
        'lb_messages.bulk_size.1min.max': 0,
        'processing.is_broken': 0,
    }
    new_stats.update(stats)
    return new_stats


def _check_stats(stats: typing.Dict, expected_stats: typing.Dict):
    for stat_key, expected_value in expected_stats.items():
        keys = stat_key.split('.')
        value = stats['phonecheck-consumer']
        for key in keys:
            value = value[key]
        logger.info('Checking stat path %s', stat_key)
        assert value == expected_value
        logger.info('ok')


def _to_proto(messages: typing.List[typing.Dict[str, typing.Any]]) -> str:
    if messages and messages[0].get('invalid'):
        return 'invalid_message'
    actions = [
        phonecheck_message_pb2.ServiceNumberAction(
            serviceNumberID=message['service_number_id'],
            description=message['description'],
            created=timestamp_pb2.Timestamp(
                seconds=message['created_at']['seconds'],
                nanos=message['created_at']['nanos'],
            ),
            release=phonecheck_message_pb2.ServiceNumberAction.ReleaseAction()
            if message.get('action') == 'set_quarantine'
            else None,
        )
        for message in messages
    ]
    return str(
        phonecheck_message_pb2.ServiceNumberActionBatch(actions=actions),
    )


@pytest.mark.parametrize(
    (
        'messages',
        'expected_processed',
        'expected_disabled_numbers',
        'expected_disabled_service_num_ids',
        'expected_stats',
    ),
    (
        pytest.param(
            ['message_1.json'],
            1,
            ['+74950101010'],
            ['79a2d7179a4266178b00b817c0c1e6cd'],
            _rich_stats(
                {
                    'msg.set_quarantine.1min': 1,
                    'total_commited.1min': 1,
                    'lb_messages.bulk_size.1min.max': 1,
                },
            ),
            id='single ok message',
        ),
        pytest.param(
            ['message_1.json', 'message_big.json', 'message_3.json'],
            4,
            ['+74950000000', '+74950101010', '+74950202020'],
            [
                '7e229f69420049719c99e09e0c37126f',
                '79a2d7179a4266178b00b817c0c1e6cd',
                'a95ffcd10c7215bc9f102535a466848f',
            ],
            _rich_stats(
                {
                    'msg.set_quarantine.1min': 3,
                    'total_commited.1min': 3,
                    'lb_messages.bulk_size.1min.max': 3,
                },
            ),
            id='several ok messages',
        ),
        pytest.param(
            [
                'message_big.json',  # 2 extracted
                'message_empty.json',
                'message_invalid.json',
                'message_locked_number.json',  # 1 extracted
                'message_no_action.json',  # 1 extracted
                'message_old.json',  # 1 extracted
                'message_unknown_number.json',  # 1 extracted
            ],
            6,
            # +74990101010 is not put on quarantine in ya-tel, however still
            # considered broken for vgw-api
            ['+74950101010', '+74950202020', '+74990101010'],
            [
                '79a2d7179a4266178b00b817c0c1e6cd',
                'a95ffcd10c7215bc9f102535a466848f',
            ],
            _rich_stats(
                {
                    'msg.set_quarantine.1min': 2,
                    'msg.skipped.no_action.1min': 1,
                    'msg.skipped.unparsed.1min': 1,
                    'msg.skipped.old.1min': 1,
                    'msg.skipped.not_found.1min': 1,
                    'msg.skipped.ya_tel_error.1min': 1,
                    'total_commited.1min': 7,
                    'lb_messages.bulk_size.1min.max': 7,
                },
            ),
            id='all message types',
        ),
        pytest.param(
            ['message_empty.json'],
            0,
            [],
            [],
            _rich_stats(
                {
                    'total_commited.1min': 1,
                    'lb_messages.bulk_size.1min.max': 1,
                },
            ),
            id='single empty message',
        ),
        pytest.param(
            ['message_1.json', 'message_2.json', 'message_3.json'],
            3,
            [],
            [],
            _rich_stats(
                {
                    'msg.skipped.ya_tel_error.1min': 3,
                    'total_commited.1min': 3,
                    'lb_messages.bulk_size.1min.max': 3,
                },
            ),
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT  # noqa: E501
                + 1,
            ),
            id='service numbers get error',
        ),
    ),
)
@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_PHONECHECK_LB_SETTINGS={
        'enabled': True,
        'quarantine_enabled': True,
        'quarantine_duration_sec': 86400,
        'max_batch_size': 10,
        'retry_delay_ms': 100,
        'intermediate_delay_ms': 100,
    },
    VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT,  # noqa: E501
)
@consts.mock_tvm_configs()
async def test_consume_messages(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        mockserver,
        mock_ya_tel_grpc,
        mock_ya_tel,
        load_json,
        testpoint,
        lb_message_sender,
        messages,
        expected_processed,
        expected_disabled_numbers,
        expected_disabled_service_num_ids,
        expected_stats,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings/state')
    def mock_forwardings_state(request):
        request.json['filter']['redirection_phones'] = sorted(
            request.json['filter']['redirection_phones'],
        )
        assert request.json == {
            'filter': {'redirection_phones': expected_disabled_numbers},
            'state': 'broken',
        }
        return mockserver.make_response(status=200, json={})

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    @testpoint('phonecheck-consumer-processed')
    def processed(data):
        return

    @testpoint('phonecheck-consumer-intermediate-sleep')
    def intermediate_sleep(data):
        assert data == 100

    @testpoint('phonecheck-consumer-loop-sleep')
    def loop_sleep(data):
        assert data == 100

    for message in messages:
        await lb_message_sender.send(
            _to_proto(load_json(message)), 'phonecheck',
        )

    numbers_disabled = bool(expected_disabled_numbers)
    async with taxi_vgw_ya_tel_adapter.spawn_task('phonecheck-consumer'):
        if numbers_disabled:
            await intermediate_sleep.wait_call()
        messages_processed = await processed.wait_call()
        assert messages_processed['data'] == expected_processed

        for service_num_id in expected_disabled_service_num_ids:
            assert (
                mock_ya_tel_grpc.service_numbers[service_num_id]['state']
                == tel_pb.ServiceNumberState.IN_QUARANTINE
            )
            # just in case check that label is not null string
            assert mock_ya_tel_grpc.service_numbers[service_num_id]['label']
        assert mock_forwardings_state.times_called == int(numbers_disabled)

        for _ in messages:
            await commit.wait_call()

        # check that in new loop there is nothing left to process
        # must wait, because not all metrics written right after commit
        await loop_sleep.wait_call()

    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics(
        'phonecheck-consumer',
    )
    _check_stats(stats, expected_stats)


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_PHONECHECK_LB_SETTINGS={
        'enabled': True,
        'quarantine_enabled': True,
        'quarantine_duration_sec': 86400,
        'max_batch_size': 2,
        'retry_delay_ms': 100,
        'intermediate_delay_ms': 100,
    },
    VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT,  # noqa: E501
)
@consts.mock_tvm_configs()
async def test_batch(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        mockserver,
        mock_ya_tel,
        mock_ya_tel_grpc,
        load_json,
        testpoint,
        lb_message_sender,
):
    idx = 0
    expected_disabled_numbers = [
        ['+74950101010', '+74950202020'],
        ['+74950101010'],
    ]

    @mockserver.json_handler('/vgw-api/v1/forwardings/state')
    def mock_forwardings_state(request):
        nonlocal idx
        request.json['filter']['redirection_phones'] = sorted(
            request.json['filter']['redirection_phones'],
        )
        assert request.json == {
            'filter': {'redirection_phones': expected_disabled_numbers[idx]},
            'state': 'broken',
        }
        idx += 1
        return mockserver.make_response(status=200, json={})

    @testpoint('phonecheck-consumer-processed')
    def processed(data):
        return

    @testpoint('phonecheck-consumer-loop-sleep')
    def loop_sleep(data):
        assert data == 100

    messages = ['message_1.json', 'message_2.json', 'message_1.json']
    for message in messages:
        await lb_message_sender.send(
            _to_proto(load_json(message)), 'phonecheck',
        )

    async with taxi_vgw_ya_tel_adapter.spawn_task('phonecheck-consumer'):
        for i in range(2):
            messages_processed = await processed.wait_call()
            assert messages_processed['data'] == 2 - i
        # check that in new loop there is nothing left to process
        # must wait, because not all metrics written right after commit
        await loop_sleep.wait_call()

    for service_num_id in [
            '79a2d7179a4266178b00b817c0c1e6cd',
            'a95ffcd10c7215bc9f102535a466848f',
    ]:
        assert (
            mock_ya_tel_grpc.service_numbers[service_num_id]['state']
            == tel_pb.ServiceNumberState.IN_QUARANTINE
        )

    assert mock_forwardings_state.times_called == 2

    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics(
        'phonecheck-consumer',
    )
    _check_stats(
        stats,
        _rich_stats(
            {
                'msg.set_quarantine.1min': 3,
                'total_commited.1min': 3,
                'lb_messages.bulk_size.1min.max': 2,
            },
        ),
    )


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_PHONECHECK_LB_SETTINGS={
        'enabled': True,
        'quarantine_enabled': True,
        'quarantine_duration_sec': 86400,
        'max_batch_size': 10,
        'retry_delay_ms': 200,
        'intermediate_delay_ms': 100,
    },
)
async def test_retry_delay(
        taxi_vgw_ya_tel_adapter, taxi_vgw_ya_tel_adapter_monitor, testpoint,
):
    await taxi_vgw_ya_tel_adapter.invalidate_caches()

    @testpoint('phonecheck-consumer-loop-sleep')
    def loop_sleep(data):
        assert data == 200

    async with taxi_vgw_ya_tel_adapter.spawn_task('phonecheck-consumer'):
        for _ in range(5):
            await loop_sleep.wait_call()

    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics(
        'phonecheck-consumer',
    )
    assert stats['phonecheck-consumer']['sleep']['total']['1min'] == 1000
    assert stats['phonecheck-consumer']['processing']['is_broken'] == 0


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_PHONECHECK_LB_SETTINGS={
        'enabled': True,
        'quarantine_enabled': True,
        'quarantine_duration_sec': 86400,
        'max_batch_size': 10,
        'retry_delay_ms': 100,
        'intermediate_delay_ms': 100,
    },
    VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT,  # noqa: E501
)
@consts.mock_tvm_configs()
async def test_fail_retry_delay(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        testpoint,
        mock_vgw_api_fail,
        mock_ya_tel,
        mock_ya_tel_grpc,
        load_json,
        lb_message_sender,
):
    await taxi_vgw_ya_tel_adapter.invalidate_caches()

    @testpoint('phonecheck-consumer-loop-sleep')
    def loop_sleep(data):
        assert data == 100

    await lb_message_sender.send(
        _to_proto(load_json('message_1.json')), 'phonecheck',
    )

    async with taxi_vgw_ya_tel_adapter.spawn_task('phonecheck-consumer'):
        for _ in range(5):
            await loop_sleep.wait_call()

    assert mock_vgw_api_fail.forwardings_state.times_called >= 5
    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics(
        'phonecheck-consumer',
    )
    assert stats['phonecheck-consumer']['sleep']['total']['1min'] == 500
    assert stats['phonecheck-consumer']['msg']['set_quarantine']['1min'] == 5
    assert stats['phonecheck-consumer']['processing']['is_broken'] == 1


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_PHONECHECK_LB_SETTINGS={
        'enabled': False,
        'quarantine_enabled': True,
        'quarantine_duration_sec': 86400,
        'max_batch_size': 10,
        'retry_delay_ms': 100,
        'intermediate_delay_ms': 100,
    },
)
@consts.mock_tvm_configs()
async def test_disabled(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        mockserver,
        mock_ya_tel_grpc,
        mock_vgw_api,
        load_json,
        testpoint,
        lb_message_sender,
):
    @testpoint('phonecheck-consumer-processed')
    def processed(data):
        return

    @testpoint('phonecheck-consumer-bulk-processed')
    def bulk_processed(data):
        return

    messages = ['message_1.json', 'message_2.json', 'message_1.json']
    for message in messages:
        await lb_message_sender.send(
            _to_proto(load_json(message)), 'phonecheck',
        )

    async with taxi_vgw_ya_tel_adapter.spawn_task('phonecheck-consumer'):
        for _ in range(5):
            await bulk_processed.wait_call()

    assert not processed.times_called
    for service_num_id in [
            '79a2d7179a4266178b00b817c0c1e6cd',
            'a95ffcd10c7215bc9f102535a466848f',
    ]:
        assert (
            mock_ya_tel_grpc.service_numbers[service_num_id]['state']
            == tel_pb.ServiceNumberState.ACTIVE
        )
    assert not mock_vgw_api.forwardings_state.times_called

    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics(
        'phonecheck-consumer',
    )
    _check_stats(stats, _rich_stats({'lb_messages.bulk_size.1min.max': 3}))


@pytest.mark.now('2020-06-30T13:00:00+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_PHONECHECK_LB_SETTINGS={
        'enabled': True,
        'quarantine_enabled': False,
        'quarantine_duration_sec': 86400,
        'max_batch_size': 10,
        'retry_delay_ms': 100,
        'intermediate_delay_ms': 100,
    },
    VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT,  # noqa: E501
)
@consts.mock_tvm_configs()
async def test_quarantine_disabled(
        taxi_vgw_ya_tel_adapter,
        taxi_vgw_ya_tel_adapter_monitor,
        mockserver,
        mock_ya_tel,
        mock_ya_tel_grpc,
        mock_vgw_api,
        load_json,
        testpoint,
        lb_message_sender,
):
    @testpoint('phonecheck-consumer-processed')
    def processed(data):
        return

    @testpoint('phonecheck-consumer-loop-sleep')
    def loop_sleep(data):
        assert data == 100

    messages = ['message_1.json', 'message_2.json', 'message_1.json']
    for message in messages:
        await lb_message_sender.send(
            _to_proto(load_json(message)), 'phonecheck',
        )

    async with taxi_vgw_ya_tel_adapter.spawn_task('phonecheck-consumer'):
        messages_processed = await processed.wait_call()
        assert messages_processed['data'] == 3
        # check that in new loop there is nothing left to process
        # must wait, because not all metrics written right after commit
        await loop_sleep.wait_call()

    assert not processed.times_called
    for service_num_id in [
            '79a2d7179a4266178b00b817c0c1e6cd',
            'a95ffcd10c7215bc9f102535a466848f',
    ]:
        assert (
            mock_ya_tel_grpc.service_numbers[service_num_id]['state']
            == tel_pb.ServiceNumberState.ACTIVE
        )
    assert not mock_vgw_api.forwardings_state.times_called

    stats = await taxi_vgw_ya_tel_adapter_monitor.get_metrics(
        'phonecheck-consumer',
    )
    _check_stats(
        stats,
        _rich_stats(
            {'total_commited.1min': 3, 'lb_messages.bulk_size.1min.max': 3},
        ),
    )
