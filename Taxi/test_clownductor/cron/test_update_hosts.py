# pylint: disable=redefined-outer-name
import pytest

from clownductor.generated.cron import run_cron


CLOWNDUCTOR_FEATURES = {
    'enable_sync_nanny_hosts': True,
    'enable_sync_conductor_hosts': True,
    'enable_sync_pg_hosts': True,
    'enable_sync_redis_hosts': True,
    'enable_sync_mongo_hosts': True,
    'enable_sync_mysql_hosts': True,
}


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'enable_sync_nanny_hosts': True})
async def test_update_hosts_nanny(
        web_app_client,
        login_mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        abc_mockserver,
        conductor_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
):
    login_mockserver()
    nanny_yp_mockserver()
    abc_mockserver()
    conductor_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some-service')
    branch_id = await add_nanny_branch(
        service['id'], 'some-branch', direct_link='some-branch',
    )

    await run_cron.main(['clownductor.crontasks.sync_nanny_hosts', '-t', '0'])

    hosts = await web_app_client.get(
        '/api/hosts', params={'branch_id': branch_id},
    )
    assert hosts.status == 200

    hosts = await hosts.json()

    assert len(hosts) == 1
    assert hosts[0]['name'] == 'qqbyrftajycoh7q2.vla.yp-c.yandex.net'
    assert hosts[0]['datacenter'] == 'vla'
    assert hosts[0]['branch_id'] == branch_id
    assert hosts[0]['branch_name'] == 'some-branch'
    assert hosts[0]['project_name'] == 'taxi'


@pytest.mark.parametrize(
    'cluster_type, cron_name',
    [
        ('conductor', 'sync_conductor_hosts'),
        ('redis_lxc', 'sync_redis_hosts'),
        ('mongo_lxc', 'sync_mongo_hosts'),
    ],
)
@pytest.mark.config(CLOWNDUCTOR_FEATURES=CLOWNDUCTOR_FEATURES)
async def test_update_hosts_conductor(
        cluster_type,
        cron_name,
        web_app_client,
        login_mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        abc_mockserver,
        conductor_mockserver,
        staff_mockserver,
        add_service,
        add_conductor_branch,
):
    login_mockserver()
    nanny_yp_mockserver()
    abc_mockserver()
    conductor_mockserver()
    staff_mockserver()

    service = await add_service(
        'taxi',
        'some-service',
        type_=cluster_type,
        direct_link='fake_direct_link',
    )

    branch_id = await add_conductor_branch(
        service['id'], 'unstable', direct_link='taxi_unstable_service',
    )

    await run_cron.main([f'clownductor.crontasks.{cron_name}', '-t', '0'])

    hosts = await web_app_client.get(
        '/api/hosts', params={'branch_id': branch_id},
    )
    assert hosts.status == 200

    hosts = await hosts.json()

    assert len(hosts) == 1
    assert hosts[0]['name'] == 'some-service-sas-01.taxi.dev.yandex.net'
    assert hosts[0]['datacenter'] == 'sas'
    assert hosts[0]['branch_id'] == branch_id
    assert hosts[0]['branch_name'] == 'unstable'
    assert hosts[0]['service_name'] == 'some-service'
    assert hosts[0]['project_name'] == 'taxi'


@pytest.mark.parametrize(
    'cluster_type, cron_name',
    [
        ('postgres', 'sync_pgaas_hosts'),
        ('redis_mdb', 'sync_redis_hosts'),
        ('mongo_mdb', 'sync_mongo_hosts'),
        ('mysql', 'sync_mysql_hosts'),
    ],
)
@pytest.mark.config(CLOWNDUCTOR_FEATURES=CLOWNDUCTOR_FEATURES)
async def test_update_hosts_mdb(
        cron_name,
        cluster_type,
        web_app_client,
        login_mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        abc_mockserver,
        conductor_mockserver,
        staff_mockserver,
        add_service,
        add_conductor_branch,
        mdb_mockserver,
):
    login_mockserver()
    nanny_yp_mockserver()
    abc_mockserver()
    conductor_mockserver()
    staff_mockserver()
    mdb_mockserver(slug='test-db')

    service = await add_service('taxi', 'some-service', type_=cluster_type)
    branch_id = await add_conductor_branch(
        service['id'], 'unstable', direct_link='mdbq9iqofu9vus91r2j9',
    )

    await run_cron.main([f'clownductor.crontasks.{cron_name}', '-t', '0'])

    hosts = await web_app_client.get(
        '/api/hosts', params={'branch_id': branch_id},
    )
    assert hosts.status == 200

    hosts = await hosts.json()

    assert len(hosts) == 3
    expected_hosts = [
        {
            'branch_id': 1,
            'name': 'man-zj0xk1xvjmmzzjfk.db.yandex.net',
            'datacenter': 'man',
            'branch_name': 'unstable',
            'service_name': 'some-service',
            'direct_link': 'mdbq9iqofu9vus91r2j9',
            'service_id': 1,
            'project_name': 'taxi',
            'project_id': 1,
        },
        {
            'branch_id': 1,
            'branch_name': 'unstable',
            'datacenter': 'sas',
            'direct_link': 'mdbq9iqofu9vus91r2j9',
            'name': 'sas-xjutiwxck3s3ifgi.db.yandex.net',
            'project_id': 1,
            'project_name': 'taxi',
            'service_id': 1,
            'service_name': 'some-service',
        },
        {
            'branch_id': 1,
            'branch_name': 'unstable',
            'datacenter': 'vla',
            'direct_link': 'mdbq9iqofu9vus91r2j9',
            'name': 'vla-27udw4m48zcufcv7.db.yandex.net',
            'project_id': 1,
            'project_name': 'taxi',
            'service_id': 1,
            'service_name': 'some-service',
        },
    ]
    assert hosts == expected_hosts
