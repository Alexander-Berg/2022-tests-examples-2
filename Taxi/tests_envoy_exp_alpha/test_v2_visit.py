import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(dest=[], info=[{'key': 'service', 'value': 'alpha'}]),
        tpl(
            dest=['alpha'],
            info=[
                {'key': 'service', 'value': 'alpha'},
                {'key': 'error', 'value': 'wrong dest "alpha"'},
            ],
        ),
        tpl(
            dest=['charlie'],
            info=[
                {'key': 'service', 'value': 'alpha'},
                {'key': 'error', 'value': 'wrong dest "charlie"'},
            ],
        ),
    ],
)
async def test_success(taxi_envoy_exp_alpha, dest, info):
    response = await taxi_envoy_exp_alpha.post('v2/visit', json={'dest': dest})
    assert response.status_code == 200
    assert response.json() == {'info': info}


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(
            dest='bravo',
            info=[
                {'key': 'service', 'value': 'alpha'},
                {'key': 'service', 'value': 'bravo'},
            ],
        ),
        tpl(
            dest='delta',
            info=[
                {'key': 'service', 'value': 'alpha'},
                {'key': 'service', 'value': 'delta'},
            ],
        ),
    ],
)
async def test_success_mock(taxi_envoy_exp_alpha, mockserver, dest, info):
    @mockserver.json_handler(f'/envoy-exp-{dest}/v2/visit')
    async def _handler(request):
        return {'info': [{'key': 'service', 'value': dest}]}

    response = await taxi_envoy_exp_alpha.post(
        'v2/visit', json={'dest': [dest]},
    )

    assert _handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'info': info}


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(
            dest='bravo',
            info=[
                {'key': 'service', 'value': 'alpha'},
                {'key': 'error', 'value': 'bravo request fails'},
            ],
        ),
        tpl(
            dest='delta',
            info=[
                {'key': 'service', 'value': 'alpha'},
                {'key': 'error', 'value': 'delta request fails'},
            ],
        ),
    ],
)
async def test_fail_mock(taxi_envoy_exp_alpha, mockserver, dest, info):
    @mockserver.json_handler(f'/envoy-exp-{dest}/v2/visit')
    async def _handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_envoy_exp_alpha.post(
        'v2/visit', json={'dest': [dest]},
    )

    assert _handler.times_called > 0
    assert response.status_code == 200
    assert response.json() == {'info': info}
