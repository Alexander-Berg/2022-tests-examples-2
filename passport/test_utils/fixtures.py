# -*- coding: utf-8 -*-
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.s3.faker.fake_s3 import FakeS3Client
from passport.backend.takeout.common.conf import configure_settings
from passport.backend.takeout.test_utils.fake_redis import FakeRedis
import pytest


@pytest.fixture()
def conf():
    configure_settings()


@pytest.yield_fixture
def s3_client(conf):
    s3_faker = FakeS3Client()
    s3_faker.start()
    yield s3_faker
    s3_faker.stop()


@pytest.yield_fixture
def grants(conf):
    grants_faker = FakeGrants()
    grants_faker.start()
    grants_faker.set_grant_list([])
    yield grants_faker
    grants_faker.stop()


@pytest.yield_fixture
def redis_mock():
    fake_redis = FakeRedis()
    fake_redis.start()
    yield fake_redis
    fake_redis.stop()
