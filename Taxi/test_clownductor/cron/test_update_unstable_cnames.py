import pytest

from dns_api import components as dns_api

from clownductor.crontasks import update_unstable_cnames
from clownductor.generated.cron import run_cron


@pytest.fixture(name='clowny_balancers_mock')
def _clowny_balancers_mock(mockserver, mock_clowny_balancer):
    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _handler(request):
        if request.query['service_id'] == '1':
            return {
                'namespaces': [
                    {
                        'id': 1,
                        'awacs_namespace': 'ns1',
                        'env': 'testing',
                        'abc_quota_source': 'some',
                        'is_external': False,
                        'is_shared': False,
                        'entry_points': [
                            {
                                'protocol': 'http',
                                'dns_name': 'abc',
                                'is_external': False,
                                'awacs_domain_id': 'some',
                                'upstreams': [
                                    {
                                        'env': 'unstable',
                                        'branch_id': 4,
                                        'awacs_backend_id': 'abc',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            }
        return mockserver.make_response(
            json={'code': '', 'message': ''}, status=404,
        )


@pytest.mark.usefixtures('clowny_balancers_mock')
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'update_unstable_cnames': True,
        'recreate_broken_cname': True,
        'delete_broken_cname': True,
    },
)
async def test_no_deleted_branches(patch, dns_mockserver):
    dns_mockserver()

    @patch('clownductor.internal.unstable_cnames.check_fqdn')
    async def _check_fqdn(unstable_branch, resolver):
        return True, unstable_branch.host

    await run_cron.main(
        ['clownductor.crontasks.update_unstable_cnames', '-t', '0', '-d'],
    )

    calls = _check_fqdn.calls
    branch = calls[0]['unstable_branch'].branch
    assert len(calls) == 1
    assert branch['id'] == 1


@pytest.mark.usefixtures('clowny_balancers_mock')
@pytest.mark.parametrize(
    'resolves_to, times_called, add_data, delete_data',
    [
        ('test-fqdn', 0, None, None),
        ('something-else', 2, 'test-fqdn', 'something-else'),
        (None, 1, 'test-fqdn', None),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'update_unstable_cnames': True,
        'recreate_broken_cname': True,
        'delete_broken_cname': True,
    },
)
async def test_find_and_remove_alias(
        patch,
        dns_mockserver,
        resolves_to,
        times_called,
        add_data,
        delete_data,
):
    mock = dns_mockserver()

    @patch('clownductor.internal.unstable_cnames.check_fqdn')
    async def _check_fqdn(unstable_branch, resolver):
        if resolves_to == unstable_branch.host:
            return True, unstable_branch.host
        return False, resolves_to

    await run_cron.main(
        ['clownductor.crontasks.update_unstable_cnames', '-t', '0', '-d'],
    )

    assert mock.times_called == times_called
    if not times_called:
        return
    calls = []
    while mock.has_calls:
        calls.append(mock.next_call())
    assert {'PUT'} == {x['request'].method for x in calls}

    operations = set()
    if add_data:
        operations.add('add')
    if delete_data:
        operations.add('delete')
    assert operations == {
        x['request'].json['primitives'][0]['operation'] for x in calls
    }
    if add_data:
        assert {add_data} == {
            x['request'].json['primitives'][0]['data']
            for x in calls
            if x['request'].json['primitives'][0]['operation'] == 'add'
        }
    if delete_data:
        assert {delete_data} == {
            x['request'].json['primitives'][0]['data']
            for x in calls
            if x['request'].json['primitives'][0]['operation'] == 'delete'
        }
    assert {'test-service.yataxi.net'} == {
        x['request'].json['primitives'][0]['name'] for x in calls
    }


@pytest.mark.usefixtures('clowny_balancers_mock')
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'update_unstable_cnames': True,
        'recreate_broken_cname': True,
        'delete_broken_cname': True,
    },
)
async def test_conflict_on_create(monkeypatch, patch, dns_mockserver):
    mock = dns_mockserver()

    # pylint: disable=protected-access
    _orig = update_unstable_cnames._process_branch
    _mock_calls = []

    async def _mock(*args, **kwargs):
        err = None
        try:
            return await _orig(*args, **kwargs)
        except Exception as exc:
            err = exc
            raise
        finally:
            _mock_calls.append((args, kwargs, err))

    monkeypatch.setattr(
        'clownductor.crontasks.update_unstable_cnames._process_branch', _mock,
    )

    @patch('clownductor.internal.unstable_cnames.check_fqdn')
    async def _check_fqdn(unstable_branch, resolver):
        return False, None

    await run_cron.main(
        ['clownductor.crontasks.update_unstable_cnames', '-t', '0', '-d'],
    )

    assert mock.times_called == 1
    calls = []
    while mock.has_calls:
        calls.append(mock.next_call())
    assert {'PUT'} == {x['request'].method for x in calls}

    assert len(_mock_calls) == 1
    assert not isinstance(_mock_calls[0][2], dns_api.Conflict)
