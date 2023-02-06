import pytest
# pylint: disable=import-error
from rate_limiter.fbs.Limits import Limits


def _parse_limits(data):
    result = {}
    limits = Limits.GetRootAsLimits(data, 0)
    for i in range(limits.PathsLength()):
        path_limit = limits.Paths(i)
        result.setdefault(path_limit.Path().decode('utf-8'), {})[
            path_limit.Client().decode('utf-8')
        ] = (
            {
                'rate': path_limit.Rate(),
                'burst': path_limit.Burst(),
                'unit': path_limit.Unit(),
            }
        )
    return result


async def get_limits(taxi_rate_limiter_proxy):
    response = await taxi_rate_limiter_proxy.get('limits')
    assert response.status_code == 200
    return _parse_limits(response.content)


@pytest.mark.config(
    TVM_SERVICES={
        'auto': 2345,
        'statistics': 777,
        'client_1': 23456,
        'client_2': 234567,
    },
    RATE_LIMITER_LIMITS={
        'auto': {
            '/test1': {
                'client_1': {'rate': 100, 'unit': 60},
                '__default__': {'rate': 10, 'unit': 1},
                '__anonym__': {'rate': 5, 'unit': 1},
            },
            '/test2': {
                'client_1': {'rate': 500, 'burst': 600, 'unit': 1},
                'client_2': {'rate': 1000, 'burst': 2000, 'unit': 1},
                'unknown': {'rate': 100},
            },
            '__default__': {
                'client_1': {'rate': 500, 'burst': 600, 'unit': 1},
            },
        },
    },
)
async def test_limits(taxi_rate_limiter_proxy):
    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        '/test1': {
            '23456': {'rate': 100, 'burst': 500, 'unit': 60},
            '': {'rate': 10, 'burst': 50, 'unit': 1},
            'anonym': {'rate': 5, 'burst': 25, 'unit': 1},
        },
        '/test2': {
            '23456': {'rate': 500, 'burst': 600, 'unit': 1},
            '234567': {'rate': 1000, 'burst': 2000, 'unit': 1},
            'unknown': {'rate': 100, 'burst': 500, 'unit': 1},
        },
        '': {'23456': {'rate': 500, 'burst': 600, 'unit': 1}},
    }


@pytest.mark.config(
    RATE_LIMITER_LIMITS={
        'auto': {'/test1': {'__default__': {'rate': 10, 'unit': 1}}},
    },
)
async def test_limits_version(taxi_rate_limiter_proxy, taxi_config):
    response = await taxi_rate_limiter_proxy.get('limits')
    assert response.status_code == 200
    limits = Limits.GetRootAsLimits(response.content, 0)
    version = limits.Version()

    taxi_config.set_values(
        {
            'RATE_LIMITER_LIMITS': {
                'sample': {
                    '/test1': {'__default__': {'rate': 100, 'unit': 1}},
                },
            },
        },
    )
    await taxi_rate_limiter_proxy.invalidate_caches()
    response = await taxi_rate_limiter_proxy.get('limits')
    assert response.status_code == 200
    limits = Limits.GetRootAsLimits(response.content, 0)
    assert version < limits.Version()


@pytest.mark.config(
    RATE_LIMITER_LIMITS={
        'auto': {'/test1': {'client1': {'rate': 10, 'unit': 1}}},
    },
)
async def test_limits_default_burst(taxi_rate_limiter_proxy, taxi_config):
    # default
    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        '/test1': {'client1': {'rate': 10, 'burst': 50, 'unit': 1}},
    }

    taxi_config.set_values({'RATE_LIMITER_DEFAULT_BURST': {'__default__': 4}})
    await taxi_rate_limiter_proxy.invalidate_caches()
    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        '/test1': {'client1': {'rate': 10, 'burst': 40, 'unit': 1}},
    }

    taxi_config.set_values(
        {'RATE_LIMITER_DEFAULT_BURST': {'__default__': 4, 'auto': 3.5}},
    )
    await taxi_rate_limiter_proxy.invalidate_caches()
    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        '/test1': {'client1': {'rate': 10, 'burst': 35, 'unit': 1}},
    }


@pytest.mark.config(
    TVM_SERVICES={
        'auto': 2345,
        'statistics': 777,
        'client_1': 123,
        'client_2': 456,
    },
    RATE_LIMITER_LIMITS={
        'auto': {'/test1': {'client_1': {'rate': 100, 'unit': 60}}},
    },
)
async def test_post_limits(taxi_rate_limiter_proxy):
    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        '/test1': {'123': {'rate': 100, 'burst': 500, 'unit': 60}},
    }

    response = await taxi_rate_limiter_proxy.post(
        'limits',
        json={
            '/test1': {
                'client_1': {'rate': 50, 'unit': 20},
                'client_2': {'rate': 100, 'unit': 10},
            },
            '/test2': {
                'client_1': {'rate': 40, 'burst': 100, 'unit': 20},
                'client_2': {'rate': 30, 'burst': 200, 'unit': 10},
                '__default__': {'rate': 20, 'unit': 1},
            },
        },
    )
    assert response.status_code == 200

    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        # config has higher priority
        '/test1': {'123': {'rate': 100, 'burst': 500, 'unit': 60}},
        '/test2': {
            '123': {'rate': 40, 'burst': 100, 'unit': 20},
            '456': {'rate': 30, 'burst': 200, 'unit': 10},
            '': {'rate': 20, 'burst': 100, 'unit': 1},
        },
    }

    # turn off limiting for test_2 handle
    response = await taxi_rate_limiter_proxy.post(
        'limits',
        json={
            '/test1': {
                'client_1': {'rate': 50, 'unit': 20},
                'client_2': {'rate': 100, 'unit': 10},
            },
        },
    )
    assert response.status_code == 200

    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        '/test1': {'123': {'rate': 100, 'burst': 500, 'unit': 60}},
    }

    # cleanup external limits
    response = await taxi_rate_limiter_proxy.post('limits', json={})
    assert response.status_code == 200
    limits = await get_limits(taxi_rate_limiter_proxy)
    assert limits == {
        '/test1': {'123': {'rate': 100, 'burst': 500, 'unit': 60}},
    }
