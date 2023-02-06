# -*- coding: utf-8 -*-
from passport.backend.takeout.common.exceptions import (
    BadSignature,
    MalformedJobId,
    UnsupportedJobIdVersion,
)
from passport.backend.takeout.common.job_id import (
    DELIMITER as job_id_delimiter,
    make_job_id_v1,
    parse_job_id,
)
import pytest


def test_job_id_v1_ok():
    raw_job_id = make_job_id_v1('test-uid', 'test-service', 'test-extract-id')
    assert raw_job_id
    job_id = parse_job_id(raw_job_id)
    assert job_id
    assert job_id.uid == 'test-uid'
    assert job_id.service_name == 'test-service'
    assert job_id.extract_id == 'test-extract-id'


def test_job_id_unsupported_version():
    raw_job_id = make_job_id_v1('test-uid', 'test-service', 'test-extract-id')
    new_raw_job_id = raw_job_id.replace('v1' + job_id_delimiter, 'v2' + job_id_delimiter)

    with pytest.raises(UnsupportedJobIdVersion):
        parse_job_id(new_raw_job_id)


def test_job_id_malformed_job_id_1():
    raw_job_id = make_job_id_v1('test-uid', 'test-service', 'test-extract-id')
    new_raw_job_id = raw_job_id.replace(
        job_id_delimiter + 'job_id' + job_id_delimiter,
        job_id_delimiter + 'di_boj' + job_id_delimiter,
    )

    with pytest.raises(MalformedJobId):
        parse_job_id(new_raw_job_id)


def test_job_id_malformed_job_id_2():
    raw_job_id = make_job_id_v1('test-uid', 'test-service', 'test-extract-id')
    new_raw_job_id = raw_job_id + job_id_delimiter + 'foobar'

    with pytest.raises(MalformedJobId):
        parse_job_id(new_raw_job_id)


def test_job_id_bad_signature():
    raw_job_id = make_job_id_v1('test-uid', 'test-service', 'test-extract-id')
    bits = raw_job_id.split(job_id_delimiter)
    bits[1] = 'bad-signature'
    new_raw_job_id = job_id_delimiter.join(bits)

    with pytest.raises(BadSignature):
        parse_job_id(new_raw_job_id)
