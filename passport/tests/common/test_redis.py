# -*- coding: utf-8 -*-
from passport.backend.takeout.common.redis import maybe_ignore_errors
import pytest
import redis
from redis.sentinel import MasterNotFoundError


@pytest.mark.parametrize(
    'exc',
    [
        redis.RedisError,
        MasterNotFoundError,
    ],
)
def test_ignore_errors(exc):
    with maybe_ignore_errors(True):
        raise exc('this exception will be ignored')


@pytest.mark.parametrize(
    'exc',
    [
        redis.RedisError,
        MasterNotFoundError,
    ],
)
def test_dont_ignore_errors(exc):
    with pytest.raises(exc):
        with maybe_ignore_errors(False):
            raise exc('this exception will be thrown')
