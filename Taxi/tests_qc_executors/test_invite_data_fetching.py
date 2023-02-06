import pytest

from tests_qc_executors import utils

INVITES = {
    'invite1': {
        'invite_id': 'invite1',
        'created': '2022-02-13T22:12:31.707937+00:00',
        'identity': {'yandex_team': {'yandex_uid': 'asasd'}},
        'comment': 'TEST',
    },
}

EXPECTED = {
    'id1': [
        {'field': 'created', 'value': '2022-02-13T22:12:31.707937+0000'},
        {'field': 'identity.type', 'value': 'yandex_team'},
        {'field': 'identity.yandex_uid', 'value': 'asasd'},
        {'field': 'comment', 'value': 'TEST'},
    ],
    'id2': [
        {'field': 'created', 'value': '2022-02-13T22:12:31.707937+0000'},
        {'field': 'identity.type', 'value': 'yandex_team'},
        {'field': 'identity.yandex_uid', 'value': 'asasd'},
        {'field': 'comment', 'value': 'TEST'},
    ],
    'id3': [
        {'field': 'created', 'value': '2022-02-13T22:12:31.707937+0000'},
        {'field': 'identity.type', 'value': 'yandex_team'},
        {'field': 'identity.yandex_uid', 'value': 'asasd'},
        {'field': 'comment', 'value': 'TEST'},
    ],
}


@pytest.mark.config(
    QC_EXECUTORS_FETCH_INVITE_DATA_SETTINGS={
        'enabled': True,
        'limit': 100,
        'sleep_ms': 100,
        'concurrent_requests_count': 10,
        'pool_name': 'fetch_invite_data',
        'invite_field': 'invite',
        'fetch_fields': [
            'created',
            'media',
            'sanctions',
            'status',
            'reason',
            'identity',
            'comment',
            'expires',
        ],
    },
)
@pytest.mark.parametrize(
    'passes_',
    [
        [
            utils.make_pass(
                'id1',
                'dkvu',
                status='new',
                with_data=False,
                data=[{'field': 'invite', 'value': f'invite1'}],
            ),
            utils.make_pass(
                'id2',
                'dkk',
                status='new',
                with_data=False,
                data=[{'field': 'invite', 'value': f'invite1'}],
            ),
            utils.make_pass(
                'id3',
                'sts',
                entity_type='car',
                with_data=False,
                data=[{'field': 'invite', 'value': f'invite1'}],
            ),
        ],
    ],
)
async def test_simple_scenario_invites_fetcher(
        taxi_qc_executors, testpoint, mockserver, passes_,
):
    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    def _internal_qc_pools_v1_pool_retrieve(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={'items': passes_, 'cursor': 'next'}, status=200,
        )

    @mockserver.json_handler('/qc-invites/api/qc-invites/v1/invite_info')
    def _qc_invites_api_v1_invite_info(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json=INVITES[request.query['invite_id']], status=200,
        )

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    def _internal_qc_pools_v1_pool_push(request):
        assert request.method == 'POST'
        for val in request.json['items']:
            assert val['data'] == EXPECTED[val['id']]

        return mockserver.make_response(json={}, status=200)

    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_qc_executors.spawn_task('fetch-invite-data'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert _internal_qc_pools_v1_pool_retrieve.times_called == 1
    assert _qc_invites_api_v1_invite_info.times_called == 3
    assert _internal_qc_pools_v1_pool_push.times_called == 1
