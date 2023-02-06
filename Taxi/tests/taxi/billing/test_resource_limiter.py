import copy
import math

import aiohttp
import pytest

from taxi import config
from taxi import stats
from taxi.billing import resource_limiter
from taxi.clients import solomon

TEST_SERVICE_NAME = 'TEST_SERVICE_NAME'
TEST_SERVICE_TVM_NAME = 'TEST_SERVICE_TVM_NAME'
TEST_CLIENT_TVM_NAME = 'TEST_CLIENT_TVM_NAME'

DEFAULT_QUOTA_SETTINGS = {
    'TEST_SERVICE_TVM_NAME': {
        'work_mode': 'hard',
        'resource_1': {
            '__anonym__': {'quota': 10, 'burst': 10, 'unit': 1},
            '__default__': {'quota': 20, 'burst': 20, 'unit': 1},
            'TEST_CLIENT_TVM_NAME': {'quota': 50, 'burst': 100, 'unit': 1},
        },
        'resource_2': {
            '__anonym__': {'quota': 10, 'burst': 10, 'unit': 1},
            '__default__': {'quota': 20, 'burst': 20, 'unit': 1},
            'TEST_CLIENT_TVM_NAME': {'quota': 50, 'burst': 100, 'unit': 1},
        },
        'resource_3': {
            'TEST_CLIENT_TVM_NAME': {'quota': 50, 'burst': 100, 'unit': 1},
        },
    },
}


class _Config(config.Config):
    def __init__(self, quota_settings: dict = None):
        super(_Config, self).__init__()
        # pylint:disable=invalid-name
        self.BILLING_RESOURCE_QUOTA_SETTINGS = (
            quota_settings or DEFAULT_QUOTA_SETTINGS
        )


@pytest.fixture
async def session_mock():
    session = aiohttp.client.ClientSession()
    yield session
    await session.close()


def test_bucket(patch):
    _patch_time_monotonic(patch, return_value=0.0)

    def _equal(var1: float, var2: float):
        return math.isclose(var1, var2, abs_tol=1e-09)

    bucket = resource_limiter.Bucket()

    # init bucket
    bucket.rebuild(bucket_size=100, refill_amount=100, unit=10)
    assert _equal(bucket.get_remaining_tokens(), 100)

    # decrease bucket size
    bucket.rebuild(bucket_size=50, refill_amount=100, unit=10)
    assert _equal(bucket.get_remaining_tokens(), 50)

    # remove tokens
    bucket.remove_tokens(20)
    assert _equal(bucket.get_remaining_tokens(), 30)

    # increase bucket size
    bucket.rebuild(bucket_size=200, refill_amount=100, unit=10)
    assert _equal(bucket.get_remaining_tokens(), 180)

    # refill
    _patch_time_monotonic(patch, return_value=1.0)
    bucket.refill()
    assert _equal(bucket.get_remaining_tokens(), 190)

    # change rate & unit, test on refill
    bucket.rebuild(bucket_size=200, refill_amount=5, unit=1)
    _patch_time_monotonic(patch, return_value=2.0)
    bucket.refill()
    assert _equal(bucket.get_remaining_tokens(), 195)

    # add tokens
    bucket.add_tokens(1)
    assert _equal(bucket.get_remaining_tokens(), 196)

    # add tokens more than bucket size
    bucket.add_tokens(100)
    assert _equal(bucket.get_remaining_tokens(), 200)

    # remove tokens > bucket size
    bucket.remove_tokens(300)
    assert _equal(bucket.get_remaining_tokens(), -100)

    # huge refill
    _patch_time_monotonic(patch, return_value=1000.0)
    bucket.refill()
    assert _equal(bucket.get_remaining_tokens(), 200)

    # ugly sizes
    bucket.rebuild(bucket_size=10.5, refill_amount=15, unit=10)
    assert _equal(bucket.get_remaining_tokens(), 10.5)
    bucket.remove_tokens(1.5)
    _patch_time_monotonic(patch, return_value=1000.5)
    bucket.refill()
    assert _equal(bucket.get_remaining_tokens(), 9.75)

    # negative token amount after bucket resize
    bucket.remove_tokens(9.75)
    bucket.rebuild(bucket_size=10.0, refill_amount=15, unit=10)
    assert _equal(bucket.get_remaining_tokens(), -0.5)


@pytest.mark.parametrize(
    'client_name, required_resources, work_mode, multiplier, '
    'expected_exception',
    [
        (
            TEST_CLIENT_TVM_NAME,
            # out of limit, soft
            [resource_limiter.Resource(name='resource_1', amount=10000)],
            'soft',
            None,
            None,
        ),
        (
            TEST_CLIENT_TVM_NAME,
            # out of limit, hard
            [resource_limiter.Resource(name='resource_1', amount=10000)],
            'hard',
            None,
            resource_limiter.NoAvailableQuota,
        ),
        (
            TEST_CLIENT_TVM_NAME,
            [
                resource_limiter.Resource(name='resource_1', amount=10),
                resource_limiter.Resource(name='resource_2', amount=2),
            ],
            'hard',
            None,
            None,
        ),
        (
            TEST_CLIENT_TVM_NAME,
            [
                resource_limiter.Resource(
                    name='no_limited_resource', amount=100,
                ),
            ],
            'hard',
            None,
            None,
        ),
        (
            TEST_CLIENT_TVM_NAME,
            [resource_limiter.Resource(name='resource_1', amount=10)],
            'hard',
            0.05,  # 100 * 0.05 = 5 available tokens
            resource_limiter.NoAvailableQuota,
        ),
        (
            None,  # anonym access
            [
                resource_limiter.Resource(name='resource_1', amount=1),
                resource_limiter.Resource(name='resource_3', amount=100000),
                resource_limiter.Resource(name='resource_2', amount=20),
            ],
            'hard',
            None,
            resource_limiter.NoAvailableQuota,
        ),
        (
            'client_with_default_quota',
            [
                resource_limiter.Resource(name='resource_1', amount=20),
                resource_limiter.Resource(name='resource_2', amount=20),
                resource_limiter.Resource(name='resource_3', amount=100000),
            ],
            'hard',
            None,
            None,
        ),
        (
            'client_with_default_quota',
            [
                resource_limiter.Resource(name='resource_1', amount=30),
                resource_limiter.Resource(name='resource_2', amount=30),
            ],
            'hard',
            None,
            resource_limiter.NoAvailableQuota,
        ),
    ],
)
async def test_limiter_quota_request(
        patch,
        client_name,
        required_resources,
        work_mode,
        multiplier,
        expected_exception,
):
    quota_settings = copy.deepcopy(DEFAULT_QUOTA_SETTINGS)
    quota_settings[TEST_SERVICE_TVM_NAME].update({'work_mode': work_mode})
    if multiplier:
        quota_settings[TEST_SERVICE_TVM_NAME].update(
            {'multiplier': multiplier},
        )
    limiter = await _create_resource_limiter(patch, quota_settings)
    exception_from_limiter = None

    try:
        limiter.request_resources(
            client_tvm_service_name=client_name,
            required_resources=required_resources,
            log_extra={},
        )
    except Exception as exc:  # pylint: disable = W0703
        exception_from_limiter = exc

    if expected_exception:
        assert isinstance(exception_from_limiter, expected_exception)
    else:
        assert exception_from_limiter is None


@pytest.mark.parametrize(
    'requested_resources, ' 'spent_resources, ' 'expected_remaining_resources',
    [
        ([], [], []),
        (
            [
                resource_limiter.Resource(name='resource_1', amount=0),
                resource_limiter.Resource(name='resource_2', amount=0),
            ],
            [],
            [
                resource_limiter.Resource(name='resource_1', amount=100),
                resource_limiter.Resource(name='resource_2', amount=100),
            ],
        ),
        (
            [
                resource_limiter.Resource(name='resource_1', amount=10),
                resource_limiter.Resource(name='resource_2', amount=10),
            ],
            [
                resource_limiter.Resource(name='resource_1', amount=20),
                resource_limiter.Resource(name='resource_2', amount=5),
            ],
            [
                resource_limiter.Resource(name='resource_1', amount=80),
                resource_limiter.Resource(name='resource_2', amount=95),
            ],
        ),
        (
            [
                resource_limiter.Resource(name='resource_1', amount=100),
                resource_limiter.Resource(name='resource_2', amount=100),
            ],
            [
                resource_limiter.Resource(name='resource_1', amount=200),
                resource_limiter.Resource(name='resource_2', amount=0),
            ],
            [
                resource_limiter.Resource(name='resource_1', amount=-100),
                resource_limiter.Resource(name='resource_2', amount=100),
            ],
        ),
    ],
)
async def test_limiter_set_spent_resources(
        patch,
        requested_resources,
        spent_resources,
        expected_remaining_resources,
):
    limiter = await _create_resource_limiter(patch)
    limiter.request_resources(
        client_tvm_service_name=TEST_CLIENT_TVM_NAME,
        required_resources=requested_resources,
        log_extra={},
    )
    limiter.adjust_resources(
        client_tvm_service_name=TEST_CLIENT_TVM_NAME,
        requested_resources=requested_resources,
        spent_resources=spent_resources,
        log_extra={},
    )
    remaining_resources = limiter.get_remaining_resources(TEST_CLIENT_TVM_NAME)

    assert remaining_resources == expected_remaining_resources


async def test_limiter_refill_buckets(patch):
    limiter = await _create_resource_limiter(patch)
    # time.monotonic returns 0.0 now, see _create_quota_limiter
    resources = [
        resource_limiter.Resource(name='resource_1', amount=50),
        resource_limiter.Resource(name='resource_2', amount=50),
    ]
    # spend
    limiter.request_resources(
        client_tvm_service_name=TEST_CLIENT_TVM_NAME,
        required_resources=resources,
        log_extra={},
    )
    remaining_resources = limiter.get_remaining_resources(TEST_CLIENT_TVM_NAME)
    assert remaining_resources == [
        resource_limiter.Resource(name='resource_1', amount=50),
        resource_limiter.Resource(name='resource_2', amount=50),
    ]
    _patch_time_monotonic(patch, return_value=0.5)
    # do new request after 0.5 sec, it also calls bucket refill
    limiter.request_resources(
        client_tvm_service_name=TEST_CLIENT_TVM_NAME,
        required_resources=resources,
        log_extra={},
    )
    remaining_resources = limiter.get_remaining_resources(TEST_CLIENT_TVM_NAME)
    assert remaining_resources == [
        resource_limiter.Resource(name='resource_1', amount=25),
        resource_limiter.Resource(name='resource_2', amount=25),
    ]


async def test_remove_quota_from_config(patch):
    limiter = await _create_resource_limiter(patch)

    resources = [
        resource_limiter.Resource(name='resource_1', amount=10000),
        resource_limiter.Resource(name='resource_2', amount=10000),
    ]

    with pytest.raises(resource_limiter.NoAvailableQuota):
        limiter.request_resources(
            client_tvm_service_name=TEST_CLIENT_TVM_NAME,
            required_resources=resources,
            log_extra={},
        )
    remaining_resources = limiter.get_remaining_resources(TEST_CLIENT_TVM_NAME)
    # raise on resource_1, only resource_1 bucket created
    assert remaining_resources == [
        resource_limiter.Resource(name='resource_1', amount=100),
    ]

    # remove resource_1 quota
    # pylint: disable=W0212
    limiter._config.BILLING_RESOURCE_QUOTA_SETTINGS[TEST_SERVICE_TVM_NAME].pop(
        'resource_1',
    )
    with pytest.raises(resource_limiter.NoAvailableQuota):
        limiter.request_resources(
            client_tvm_service_name=TEST_CLIENT_TVM_NAME,
            required_resources=resources,
            log_extra={},
        )
    remaining_resources = limiter.get_remaining_resources(TEST_CLIENT_TVM_NAME)
    # raise on resource_2, resource_1 bucket removed, resource_2 bucket created
    assert remaining_resources == [
        resource_limiter.Resource(name='resource_2', amount=100),
    ]

    # remove resource quota from config for all service
    # pylint: disable=W0212
    limiter._config.BILLING_RESOURCE_QUOTA_SETTINGS = {}
    # should be ok now
    limiter.request_resources(
        client_tvm_service_name=TEST_CLIENT_TVM_NAME,
        required_resources=resources,
        log_extra={},
    )
    # all bucket should be removed
    remaining_resources = limiter.get_remaining_resources(TEST_CLIENT_TVM_NAME)
    assert remaining_resources == []


async def _create_resource_limiter(
        patch, quota_settings=None,
) -> resource_limiter.ResourceLimiter:
    _patch_time_monotonic(patch, return_value=0.0)
    stats_component = stats.Stats(
        unit_name=TEST_SERVICE_NAME,
        client_solomon=solomon.SolomonClient(session=session_mock),
    )
    return resource_limiter.ResourceLimiter(
        tvm_service_name=TEST_SERVICE_TVM_NAME,
        config=_Config(quota_settings),
        app_instance=1,
        stats_component=stats_component,
    )


def _patch_time_monotonic(patch, return_value):
    @patch('time.monotonic')
    def _time():
        return return_value
