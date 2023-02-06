# -*- coding: utf-8 -*-

from unittest import mock

from botocore.exceptions import ClientError
import pytest
from redis import RedisError
from redis.sentinel import MasterNotFoundError

from passport.backend.takeout.common.touch import (
    TOUCH_DIR_NAME,
    TouchFiles,
)
from passport.backend.takeout.test_utils.fixtures import (
    conf,
    s3_client,
    redis_mock,
)


conf  # noqa
s3_client  # noqa
redis_mock  # noqa


def test_touch_set(s3_client, redis_mock):
    tf = TouchFiles('uid', 'extract-id', 'service-name')
    with mock.patch('passport.backend.takeout.common.touch.get_config') as get_config_mock:
        get_config_mock.return_value = {
            'redis': {
                'touch_files_ttl': 123456,
            },
        }
        tf.set('touch-name')

    calls = redis_mock.redis_calls_by_method('setex')
    assert len(calls) == 1
    key = calls[0].args[0]
    ttl = calls[0].args[1]
    value = calls[0].args[2]
    assert key == 'takeout:extract:touch:uid:extract-id:service-name:touch-name'
    assert ttl == 123456
    assert value == ''


@pytest.mark.parametrize('skip_errors', [True, False])
@pytest.mark.parametrize(
    'sentinel_exc, redis_exc',
    [
        (MasterNotFoundError(), None),
        (None, RedisError()),
    ],
)
def test_touch_set_skip_errors(redis_mock, skip_errors, sentinel_exc, redis_exc):
    def attempt_set():
        tf = TouchFiles('uid', 'extract-id', 'service-name')
        tf.set('touch-name', skip_errors=skip_errors)

    redis_mock.sentinel_mock.return_value.discover_master.side_effect = sentinel_exc
    redis_mock.redis_set_side_effect('setex', redis_exc)

    if skip_errors:
        if sentinel_exc:
            attempt_set()
            assert len(redis_mock.sentinel_mock.return_value.mock_calls) == 1
        elif redis_exc:
            attempt_set()
            assert len(redis_mock.redis_calls_by_method('setex')) == 1
            actual_key = redis_mock.redis_calls_by_method('setex')[0].args[0]
            assert actual_key == 'takeout:extract:touch:uid:extract-id:service-name:touch-name'
    else:
        if sentinel_exc:
            with pytest.raises(MasterNotFoundError):
                attempt_set()
            assert len(redis_mock.sentinel_mock.return_value.mock_calls) == 1
        elif redis_exc:
            with pytest.raises(RedisError):
                attempt_set()
            assert len(redis_mock.redis_calls_by_method('setex')) == 1
            actual_key = redis_mock.redis_calls_by_method('setex')[0].args[0]
            assert actual_key == 'takeout:extract:touch:uid:extract-id:service-name:touch-name'


def test_unset(s3_client, redis_mock):
    s3_client.set_response_value(
        'delete_object',
        {
            'ResponseMetadata': {
                'HTTPStatusCode': 204,
            },
        },
    )
    tf = TouchFiles('uid', 'extract-id', 'service-name')
    tf.unset('touch-name')

    assert len(s3_client.calls_by_method('delete_object')) == 1
    actual_key = s3_client.calls_by_method('delete_object')[0]['Key']
    assert actual_key == 'uid/extract-id/service-name/' + TOUCH_DIR_NAME + '/touch-name'

    assert len(redis_mock.redis_calls_by_method('delete')) == 1
    actual_key = redis_mock.redis_calls_by_method('delete')[0].args[0]
    assert actual_key == 'takeout:extract:touch:uid:extract-id:service-name:touch-name'


def test_if_set_s3__true(s3_client, redis_mock):
    redis_mock.redis_set_side_effect('exists', [0])

    tf = TouchFiles('uid', 'extract-id', 'service-name')
    is_set = tf.is_set('touch-name')

    assert len(s3_client.calls_by_method('head_object')) == 1
    actual_key = s3_client.calls_by_method('head_object')[0]['Key']
    assert actual_key == 'uid/extract-id/service-name/' + TOUCH_DIR_NAME + '/touch-name'

    assert len(redis_mock.redis_calls_by_method('exists')) == 1
    actual_key = redis_mock.redis_calls_by_method('exists')[0].args[0]
    assert actual_key == 'takeout:extract:touch:uid:extract-id:service-name:touch-name'

    assert is_set


def test_if_set__false(s3_client, redis_mock):
    redis_mock.redis_set_side_effect('exists', [0])

    s3_client.set_response_side_effect(
        'head_object',
        ClientError({'Error': {'Code': '404'}}, 'test-arg'),
    )

    tf = TouchFiles('uid', 'extract-id', 'service-name')
    is_set = tf.is_set('touch-name')

    assert len(s3_client.calls_by_method('head_object')) == 1
    actual_key = s3_client.calls_by_method('head_object')[0]['Key']
    assert actual_key == 'uid/extract-id/service-name/' + TOUCH_DIR_NAME + '/touch-name'

    assert len(redis_mock.redis_calls_by_method('exists')) == 1
    actual_key = redis_mock.redis_calls_by_method('exists')[0].args[0]
    assert actual_key == 'takeout:extract:touch:uid:extract-id:service-name:touch-name'

    assert not is_set


def test_if_set_redis__true(s3_client, redis_mock):
    s3_client.set_response_side_effect(
        'head_object',
        ClientError({'Error': {'Code': '404'}}, 'test-arg'),
    )

    redis_mock.redis_set_side_effect('exists', [1])

    tf = TouchFiles('uid', 'extract-id', 'service-name')
    is_set = tf.is_set('touch-name')

    assert len(s3_client.calls_by_method('head_object')) == 1
    actual_key = s3_client.calls_by_method('head_object')[0]['Key']
    assert actual_key == 'uid/extract-id/service-name/' + TOUCH_DIR_NAME + '/touch-name'

    assert len(redis_mock.redis_calls_by_method('exists')) == 1
    actual_key = redis_mock.redis_calls_by_method('exists')[0].args[0]
    assert actual_key == 'takeout:extract:touch:uid:extract-id:service-name:touch-name'

    assert is_set
