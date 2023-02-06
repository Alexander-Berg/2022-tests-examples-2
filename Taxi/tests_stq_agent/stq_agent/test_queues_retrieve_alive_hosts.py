import pytest

from testsuite import utils


@pytest.mark.parametrize(
    'sleep_period, get_configs_again, hosts_after_sleep',
    [(30, False, ['host1']), (31, False, []), (31, True, ['host1'])],
)
@pytest.mark.config(STQ_AGENT_ALIVE_HOSTS_OUTDATE_TIMEOUT=40)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_retrieve_alive_hosts_dead_host(
        taxi_stq_agent,
        mocked_time,
        get_stq_config,
        sleep_period,
        get_configs_again,
        hosts_after_sleep,
):
    for get_configs, hosts in (
            (True, ['host1']),
            (get_configs_again, hosts_after_sleep),
    ):
        if get_configs:
            await get_stq_config('host1', ['queue11'])
            await taxi_stq_agent.invalidate_caches()

        await _check_queues_retrieve_alive_hosts(
            taxi_stq_agent, [{'queue_name': 'queue11', 'hosts': hosts}],
        )

        mocked_time.sleep(sleep_period)
        await taxi_stq_agent.invalidate_caches()


@pytest.mark.parametrize(
    'host, queue', [('host1', 'queue100500'), ('host100500', 'queue11')],
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_retrieve_alive_hosts_not_exist(
        taxi_stq_agent, get_stq_config, host, queue,
):
    await get_stq_config(host, [queue])
    await taxi_stq_agent.invalidate_caches()

    await _check_queues_retrieve_alive_hosts(
        taxi_stq_agent, [{'queue_name': queue, 'hosts': [host]}],
    )


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_retrieve_alive_hosts_reset(
        taxi_stq_agent, get_stq_config,
):
    await get_stq_config('host1', ['queue11'])
    await taxi_stq_agent.invalidate_caches()

    alive_hosts = [{'queue_name': 'queue11', 'hosts': ['host1']}]

    await _check_queues_retrieve_alive_hosts(taxi_stq_agent, alive_hosts)

    await get_stq_config('host1', ['queue12'])
    await taxi_stq_agent.invalidate_caches()

    alive_hosts.append({'queue_name': 'queue12', 'hosts': ['host1']})

    await _check_queues_retrieve_alive_hosts(taxi_stq_agent, alive_hosts)


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_retrieve_alive_hosts_outdated(
        taxi_stq_agent, mocked_time, get_stq_config,
):
    await _check_queues_retrieve_alive_hosts(taxi_stq_agent, expected_code=500)

    await get_stq_config('host1', ['queue11'])
    await taxi_stq_agent.invalidate_caches()

    await _check_queues_retrieve_alive_hosts(taxi_stq_agent)

    mocked_time.sleep(11)
    await taxi_stq_agent.invalidate_caches()

    await _check_queues_retrieve_alive_hosts(taxi_stq_agent, expected_code=500)


async def _check_queues_retrieve_alive_hosts(
        taxi_stq_agent, hosts=None, expected_code=200,
):
    response = await taxi_stq_agent.post('queues/retrieve_alive_hosts')
    assert response.status_code == expected_code
    if response.status_code == 200 and hosts is not None:
        utils.ordered_object.assert_eq(
            response.json(), {'hosts': hosts}, ['hosts', 'hosts.hosts'],
        )
