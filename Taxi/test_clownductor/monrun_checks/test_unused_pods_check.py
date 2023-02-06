import pytest

from clownductor.generated.cron import run_monrun


async def test_ok():
    msg = await run_monrun.run(['clownductor.monrun_checks.unused_pods_check'])
    assert msg == '0; Check done'


@pytest.mark.now('2020-02-21T19:00:00.0Z')
@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.config(
    CLOWNDUCTOR_SEARCH_UNUSED_PODS={
        'max_age_in_hours': 168,
        'yp_regions': ['sas', 'vla', 'man'],
        'skip_for_services': [],
        'skip_for_branches': ['test-branch-2'],
    },
)
async def test_warn(
        mockserver, nanny_yp_mockserver, add_service, add_nanny_branch,
):
    # will fail on getting pods from yp_nanny
    service = await add_service('test', 'test-service')
    await add_nanny_branch(
        service['id'], 'test-branch', direct_link='test-branch',
    )

    # skipped by config
    service2 = await add_service('test', 'test-service-2')
    await add_nanny_branch(
        service2['id'], 'test-branch-2', direct_link='test-branch-2',
    )

    # will return 1 inactive non used pod
    service3 = await add_service('test', 'test-service-3')
    await add_nanny_branch(
        service3['id'], 'test-branch-3', direct_link='test-branch-3',
    )

    nanny_yp_mockserver()

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        assert request.method == 'POST'
        data = request.json
        assert data['serviceId'] in {'test-branch', 'test-branch-3'}
        assert data['cluster'] in {'SAS', 'VLA', 'MAN'}
        if data['cluster'] in {'SAS', 'VLA'}:
            return {'pods': []}
        if data['serviceId'] == 'test-branch':
            return {}
        return {
            'pods': [
                {
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [{'currentState': 'ACTIVE'}],
                            },
                        },
                    },
                    'meta': {
                        'creationTime': '1582300700000000',
                        'id': '1',
                        'podSetId': 'test-service-podset',
                    },
                },  # active pod
                {
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [
                                    {
                                        'currentState': 'PREPARED',
                                        'feedback': {
                                            'hooks': {
                                                'updateTimestamp': (
                                                    '1582300600000'
                                                ),
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    },
                    'meta': {
                        'creationTime': '1582300600000000',
                        'id': '2',
                        'podSetId': 'test-service-podset',
                    },
                },  # inactive not expired
                {
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [
                                    {
                                        'currentState': 'PREPARED',
                                        'feedback': {
                                            'hooks': {
                                                'updateTimestamp': (
                                                    '1522300600000'
                                                ),
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    },
                    'meta': {
                        'creationTime': '1522300600000000',
                        'id': '3',
                        'podSetId': 'test-service-podset',
                    },
                },  # inactive expired
            ],
        }

    msg: str = await run_monrun.run(
        ['clownductor.monrun_checks.unused_pods_check'],
    )
    assert msg.startswith('1; WARN: ')
    msg = msg.replace('1; WARN: ', '')
    assert sorted(msg.split(', ', maxsplit=1)) == [
        'Failed to get pods for test-branch (reason "KeyError(\'pods\')")',
        'Nanny service test-branch-3, pod 3',
    ]
