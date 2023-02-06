import json

import pytest

from testsuite.utils import callinfo


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
async def test_logbroker_message_commit_order(taxi_cashback_levels, testpoint):
    # Этот тестпоинт будет активирован на каждый commit каждого сообщения
    items = [i for i in range(10)]
    items_iter = iter(items)

    @testpoint('logbroker_commit')
    def commit(cookie):
        # По cookie можно проверить, в каком порядке коммитятся сообщения
        assert cookie == f'cookie{next(items_iter)}'

    # Эмуляция записи сообщения в логброкер
    for i in items:
        response = await taxi_cashback_levels.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'cashback-levels-mission-progress-lb-consumer',
                    'data': str(i),
                    'topic': 'smth',
                    'cookie': f'cookie{i}',
                },
            ),
        )
        assert response.status_code == 200
        await commit.wait_call()


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
async def test_non_proto_message_serialization_message_committed_no_sideeffect(
        send_message_to_logbroker, messages_to_b64_protoseq, testpoint, pgsql,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    response = await send_message_to_logbroker(
        consumer='cashback-levels-mission-progress-lb-consumer',
        data_b64=messages_to_b64_protoseq(b'kek', b'lol'),
    )

    await commit.wait_call()
    assert response.status_code == 200

    cursor = pgsql['cashback_levels'].cursor()
    cursor.execute('SELECT COUNT (*) from cashback_levels.missions_completed')
    assert next(cursor)[0] == 0


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=False)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
async def test_messages_not_read_when_consumer_disabled(
        taxi_cashback_levels,
        taxi_config,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    response = await send_message_to_logbroker(
        consumer='cashback-levels-mission-progress-lb-consumer',
        data_b64=messages_to_b64_protoseq(b'another_kek', b'another_lol'),
    )

    with pytest.raises(callinfo.CallQueueTimeoutError):
        await commit.wait_call(2)
    assert response.status_code == 200

    # Нужно вычитать невычитанные сообщения, иначе это повлияет на другие тесты
    taxi_config.set_values(
        {'CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED': True},
    )
    await taxi_cashback_levels.invalidate_caches()
    await commit.wait_call()
    assert response.status_code == 200
