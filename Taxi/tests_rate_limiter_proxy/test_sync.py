import flatbuffers
import pytest
# pylint: disable=import-error
import rate_limiter.fbs.Client as FbClient
import rate_limiter.fbs.Counters as FbCounters
import rate_limiter.fbs.PathCounters as FbPathCounters


def _parse_sync_message(data):
    result = {}
    counters = FbCounters.Counters.GetRootAsCounters(data, 0)
    result['lamport'] = counters.Lamport()
    result['limits_version'] = counters.LimitsVersion()
    result['paths'] = {}
    for i in range(counters.PathsLength()):
        path_counters = counters.Paths(i)
        path = path_counters.Path().decode('utf-8')
        result['paths'][path] = {}
        for j in range(path_counters.ClientsLength()):
            client_counter = path_counters.Clients(j)
            result['paths'][path][
                client_counter.Name().decode('utf-8')
            ] = client_counter.Count()
    return result


def _serialize_sync_message(message):
    builder = flatbuffers.Builder(0)

    paths = []
    for path, path_counters in message['paths'].items():
        clients = []
        for client, counter in path_counters.items():
            name_offset = builder.CreateString(client)
            FbClient.ClientStart(builder)
            FbClient.ClientAddName(builder, name_offset)
            FbClient.ClientAddCount(builder, counter)
            clients.append(FbClient.ClientEnd(builder))

        FbPathCounters.PathCountersStartClientsVector(builder, len(clients))
        for client in clients:
            builder.PrependUOffsetTRelative(client)
        clients_offset = builder.EndVector(len(clients))

        path_offset = builder.CreateString(path)
        FbPathCounters.PathCountersStart(builder)
        FbPathCounters.PathCountersAddPath(builder, path_offset)
        FbPathCounters.PathCountersAddClients(builder, clients_offset)
        paths.append(FbPathCounters.PathCountersEnd(builder))

    FbCounters.CountersStartPathsVector(builder, len(paths))
    for path in paths:
        builder.PrependUOffsetTRelative(path)
    paths_offset = builder.EndVector(len(paths))

    FbCounters.CountersStart(builder)
    FbCounters.CountersAddLamport(builder, message['lamport'])
    FbCounters.CountersAddLimitsVersion(builder, message['limits_version'])
    FbCounters.CountersAddPaths(builder, paths_offset)
    builder.Finish(FbCounters.CountersEnd(builder))
    return bytes(builder.Output())


async def test_response_codes(taxi_rate_limiter_proxy):
    headers = {'Content-Type': 'application/flatbuffer'}
    shard = 'test_response_codes'

    # invalid sync message
    response = await taxi_rate_limiter_proxy.post(
        'sync', headers=headers, params={'shard': shard}, data='invalid fb',
    )
    assert response.status_code == 400

    # no shard
    response = await taxi_rate_limiter_proxy.post(
        'sync', headers=headers, data='',
    )
    assert response.status_code == 400

    # limits version conflict
    response = await taxi_rate_limiter_proxy.post(
        'sync', headers=headers, params={'shard': shard}, data='',
    )
    assert response.status_code == 409
    message = _parse_sync_message(response.content)

    # correct
    response = await taxi_rate_limiter_proxy.post(
        'sync',
        headers=headers,
        params={'shard': shard},
        data=_serialize_sync_message(message),
    )
    assert response.status_code == 200


@pytest.mark.config(
    TVM_SERVICES={
        'auto': 2345,
        'statistics': 777,
        'client1': 23456,
        'client2': 234567,
    },
    RATE_LIMITER_LIMITS={
        'auto': {
            '/test/sync1': {
                'client1': {'rate': 100, 'unit': 60},
                'client2': {'rate': 10, 'unit': 1},
            },
        },
    },
)
async def test_sync(taxi_rate_limiter_proxy, mocked_time):
    headers = {'Content-Type': 'application/flatbuffer'}

    # detect current limits version
    response = await taxi_rate_limiter_proxy.post(
        'sync', headers=headers, params={'shard': 'test_sync'}, data='',
    )
    assert response.status_code == 409
    message = _parse_sync_message(response.content)
    limits_version = message['limits_version']

    # pre init shard counters
    shard1 = 'test_sync1'
    shard1_lamport = 1
    shard1_message = {
        'paths': {},
        'lamport': shard1_lamport,
        'limits_version': limits_version,
    }
    response = await taxi_rate_limiter_proxy.post(
        'sync',
        headers=headers,
        params={'shard': shard1},
        data=_serialize_sync_message(shard1_message),
    )
    assert response.status_code == 200

    shard2 = 'test_sync2'
    shard2_lamport = 1
    shard2_message = {
        'paths': {},
        'lamport': shard2_lamport,
        'limits_version': limits_version,
    }
    response = await taxi_rate_limiter_proxy.post(
        'sync',
        headers=headers,
        params={'shard': shard2},
        data=_serialize_sync_message(shard2_message),
    )
    assert response.status_code == 200

    # do first actual counters update
    mocked_time.sleep(1)

    shard1_lamport = shard1_lamport + 1
    shard1_message = {
        'paths': {'/test/sync1': {'client1': 100}},
        'lamport': shard1_lamport,
        'limits_version': limits_version,
    }
    response = await taxi_rate_limiter_proxy.post(
        'sync',
        headers=headers,
        params={'shard': shard1},
        data=_serialize_sync_message(shard1_message),
    )
    assert response.status_code == 200
    message = _parse_sync_message(response.content)
    assert message['lamport'] == shard1_message['lamport']
    assert message['limits_version'] == shard1_message['limits_version']
    assert {'/test/sync1'} == set(message['paths'].keys())
    assert {'client1'} == set(message['paths']['/test/sync1'].keys())

    shard2_lamport = shard2_lamport + 1
    shard2_message = {
        'paths': {'/test/sync1': {'client1': 50, 'client2': 150}},
        'lamport': shard2_lamport,
        'limits_version': limits_version,
    }
    response = await taxi_rate_limiter_proxy.post(
        'sync',
        headers=headers,
        params={'shard': shard2},
        data=_serialize_sync_message(shard2_message),
    )
    assert response.status_code == 200
    message = _parse_sync_message(response.content)
    assert message['lamport'] == shard2_message['lamport']
    assert message['limits_version'] == shard2_message['limits_version']
    assert {'/test/sync1'} == set(message['paths'].keys())
    assert {'client1', 'client2'} == set(
        message['paths']['/test/sync1'].keys(),
    )

    mocked_time.sleep(1)

    shard1_lamport = shard1_lamport + 1
    shard1_message = {
        'paths': {'/test/sync1': {'client1': 150}},
        'lamport': shard1_lamport,
        'limits_version': limits_version,
    }
    response = await taxi_rate_limiter_proxy.post(
        'sync',
        headers=headers,
        params={'shard': shard1},
        data=_serialize_sync_message(shard1_message),
    )
    assert response.status_code == 200
    message = _parse_sync_message(response.content)
    assert message['lamport'] == shard1_message['lamport']
    assert message['limits_version'] == shard1_message['limits_version']
    assert {'/test/sync1'} == set(message['paths'].keys())
    assert {'client1', 'client2'} == set(
        message['paths']['/test/sync1'].keys(),
    )
