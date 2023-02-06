import pytest


async def test_empty(taxi_configs_sidecar):
    response = await taxi_configs_sidecar.post(
        '/configs/values', json={'ids': ['USERVER_RPS_CCONTROL_ENABLED']},
    )
    assert response.json() == {
        'configs': {'USERVER_RPS_CCONTROL_ENABLED': False},
    }


@pytest.mark.config(USERVER_RPS_CCONTROL_ENABLED=True)
async def test_change(taxi_configs_sidecar):
    response = await taxi_configs_sidecar.post(
        '/configs/values', json={'ids': ['USERVER_RPS_CCONTROL_ENABLED']},
    )
    assert response.json() == {
        'configs': {'USERVER_RPS_CCONTROL_ENABLED': True},
    }


async def test_not_found(taxi_configs_sidecar):
    response = await taxi_configs_sidecar.post(
        '/configs/values', json={'ids': ['UNKNOWN']},
    )
    assert response.json() == {'configs': {}, 'not_found': ['UNKNOWN']}


@pytest.mark.config(USERVER_HTTP_PROXY='')
async def test_multiple(taxi_configs_sidecar):
    response = await taxi_configs_sidecar.post(
        '/configs/values',
        json={'ids': ['USERVER_RPS_CCONTROL_ENABLED', 'USERVER_HTTP_PROXY']},
    )
    assert response.json() == {
        'configs': {
            'USERVER_RPS_CCONTROL_ENABLED': False,
            'USERVER_HTTP_PROXY': '',
        },
    }


async def test_cache(taxi_configs_sidecar, mockserver):
    ids = ['USERVER_RPS_CCONTROL_ENABLED']

    async def request():
        await taxi_configs_sidecar.post('/configs/values', json={'ids': ids})

    await request()

    @mockserver.json_handler('/configs-service/configs/values')
    async def _mock_values(request):
        assert set(request.json['ids']) == set(ids + ['USERVER_CACHES'])
        return {'configs': {}}

    await request()
    assert _mock_values.times_called == 0

    ids.append('UNKNOWN')
    await request()
    assert _mock_values.times_called == 1

    await request()
    assert _mock_values.times_called == 1


@pytest.mark.parametrize('param', ['service', 'stage_name', 'updated_since'])
async def test_unsupported_argument(taxi_configs_sidecar, param):
    response = await taxi_configs_sidecar.post(
        '/configs/values',
        json={
            'ids': ['USERVER_RPS_CCONTROL_ENABLED'],
            param: '2017-04-04T15:32:22+1000',
        },
    )
    assert response.json() == {
        'code': 'UNSUPPORTED_ARGUMENT',
        'message': (
            'stage_name, updated_since, service arguments are not supported'
        ),
    }
