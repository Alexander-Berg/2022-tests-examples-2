import pytest


def tpl(**kwargs):
    return tuple(kwargs.values())


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(dest=[], info=[{'key': 'service', 'value': 'bravo'}]),
        tpl(
            dest=['alpha'],
            info=[
                {'key': 'service', 'value': 'bravo'},
                {'key': 'error', 'value': 'wrong dest "alpha"'},
            ],
        ),
        tpl(
            dest=['bravo'],
            info=[
                {'key': 'service', 'value': 'bravo'},
                {'key': 'error', 'value': 'wrong dest "bravo"'},
            ],
        ),
    ],
)
async def test_success(taxi_envoy_exp_bravo_web, dest, info):
    response = await taxi_envoy_exp_bravo_web.post(
        'v2/visit', json={'dest': dest},
    )

    assert response.status == 200

    content = await response.json()
    assert content == {'info': info}


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(
            dest='charlie',
            info=[
                {'key': 'service', 'value': 'bravo'},
                {'key': 'service', 'value': 'charlie'},
            ],
        ),
        tpl(
            dest='delta',
            info=[
                {'key': 'service', 'value': 'bravo'},
                {'key': 'service', 'value': 'delta'},
            ],
        ),
    ],
)
async def test_success_mock(taxi_envoy_exp_bravo_web, mockserver, dest, info):
    @mockserver.json_handler(f'/envoy-exp-{dest}/v2/visit')
    async def _handler(request):
        return {'info': [{'key': 'service', 'value': dest}]}

    response = await taxi_envoy_exp_bravo_web.post(
        'v2/visit', json={'dest': [dest]},
    )

    assert _handler.times_called == 1
    assert response.status == 200

    content = await response.json()
    assert content == {'info': info}


@pytest.mark.parametrize(
    ['dest', 'info'],
    [
        tpl(
            dest='charlie',
            info=[
                {'key': 'service', 'value': 'bravo'},
                {'key': 'error', 'value': 'charlie request fails'},
            ],
        ),
        tpl(
            dest='delta',
            info=[
                {'key': 'service', 'value': 'bravo'},
                {'key': 'error', 'value': 'delta request fails'},
            ],
        ),
    ],
)
async def test_fail_mock(taxi_envoy_exp_bravo_web, mockserver, dest, info):
    @mockserver.json_handler(f'/envoy-exp-{dest}/v2/visit')
    async def _handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_envoy_exp_bravo_web.post(
        'v2/visit', json={'dest': [dest]},
    )

    assert _handler.times_called > 0
    assert response.status == 200

    content = await response.json()
    assert content == {'info': info}
