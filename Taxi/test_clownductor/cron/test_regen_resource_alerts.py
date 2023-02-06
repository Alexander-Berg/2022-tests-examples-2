# pylint: disable=redefined-outer-name
import pytest

from clownductor.crontasks import regen_resource_alerts
from clownductor.generated.cron import run_cron


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'add_juggler_alerts_for_created_golovan': True},
    CLOWNDUCTOR_IGNORE_REGEN_SERVICES={
        'taxi': {'error-service': ['stable', 'testing']},
    },
)
async def test_regen_resource_alerts(
        patch,
        nanny_mockserver,
        nanny_yp_mockserver,
        golovan_mockserver,
        login_mockserver,
        abc_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
):
    nanny_yp_mockserver()
    login_mockserver()
    abc_mockserver()
    golovan_mock = golovan_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some-service')
    await add_service('taxi', 'error-service')
    for env in ['unstable', 'testing', 'stable']:
        await add_nanny_branch(service['id'], env, direct_link=env, env=env)

    @patch('clownductor.crontasks.regen_resource_alerts.get_service_resources')
    async def _get_service_resources(*_args):
        return regen_resource_alerts.ServiceResources(
            pods_num=1, vcpus=1, mem=4 * 1024 ** 3, datacenters=2,
        )

    await run_cron.main(
        ['clownductor.crontasks.regen_resource_alerts', '-t', '0'],
    )

    calls = []
    while golovan_mock.has_calls:
        calls.append(golovan_mock.next_call())
    assert len(calls) == 4
    create_or_patch = [
        x
        for x in calls
        if x['request'].path != '/client-golovan/srvambry/alerts/get'
    ]
    assert len(create_or_patch) == 2
    assert [x['request'].json for x in create_or_patch] == [
        {
            'name': 'taxi_some-service_stable_high_cpu_usage',
            'signal': 'portoinst-cpu_usage_cores_tmmv',
            'tags': {
                'itype': ['some-service'],
                'ctype': ['stable', 'prestable'],
            },
            'crit': [162.0, 1000000000],
            'warn': [129.6, 162.0],
            'mgroups': ['ASEARCH'],
            'value_modify': {'type': 'summ', 'window': 1800},
            'juggler_check': {
                'refresh_time': 5,
                'tags': [
                    'a_mark_yasm_taxi_some-service_stable_high_cpu_usage',
                    'a_itype_some-service',
                    'a_ctype_stable',
                    'a_ctype_prestable',
                ],
                'notifications': [],
                'host': 'yasm_taxi_some-service_stable_high_cpu_usage',
                'meta': {},
                'ttl': 900,
                'methods': [],
                'service': 'taxi_some-service_stable_high_cpu_usage',
                'aggregator': 'logic_or',
                'namespace': 'taxi.ops.prod',
                'aggregator_kwargs': {
                    'unreach_service': [{'check': 'yasm_alert:virtual-meta'}],
                    'nodata_mode': 'force_ok',
                    'unreach_mode': 'force_ok',
                },
            },
        },
        {
            'name': 'taxi_some-service_testing_high_cpu_usage',
            'signal': 'portoinst-cpu_usage_cores_tmmv',
            'tags': {'itype': ['some-service'], 'ctype': ['testing']},
            'crit': [162.0, 1000000000],
            'warn': [129.6, 162.0],
            'mgroups': ['ASEARCH'],
            'value_modify': {'type': 'summ', 'window': 1800},
            'juggler_check': {
                'refresh_time': 5,
                'tags': [
                    'a_mark_yasm_taxi_some-service_testing_high_cpu_usage',
                    'a_itype_some-service',
                    'a_ctype_testing',
                ],
                'notifications': [],
                'host': 'yasm_taxi_some-service_testing_high_cpu_usage',
                'meta': {},
                'ttl': 900,
                'methods': [],
                'service': 'taxi_some-service_testing_high_cpu_usage',
                'aggregator': 'logic_or',
                'namespace': 'taxi.ops.test',
                'aggregator_kwargs': {
                    'unreach_service': [{'check': 'yasm_alert:virtual-meta'}],
                    'nodata_mode': 'force_ok',
                    'unreach_mode': 'force_ok',
                },
            },
        },
    ]
