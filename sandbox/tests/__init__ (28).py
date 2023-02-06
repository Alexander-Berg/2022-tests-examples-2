# coding: utf-8

import io
import pytest
import datetime as dt

import six

import sandbox.common.vcs.cache as cvc


def _to_time(ts):
    return str(dt.datetime.fromtimestamp(ts))


CACHE_TESTS = [
    (
        [
            cvc.CacheRecord(path="0", update_time=_to_time(42), is_permanent=True, rep_type="svn")
        ] + [
            cvc.CacheRecord(path=str(ind), update_time=_to_time(ind), rep_type="svn")
            for ind in six.moves.range(1, cvc.CacheableArcadia.DIRS_LIMIT * 2)
        ],
        [str(p) for p in six.moves.range(1, cvc.CacheableArcadia.DIRS_LIMIT)]
    ),
    (
        [
            cvc.CacheRecord(path=str(ind), update_time=_to_time(ind), is_permanent=True, rep_type="svn")
            for ind in six.moves.range(cvc.CacheableArcadia.DIRS_LIMIT + 1)
        ] + [
            cvc.CacheRecord(path="unknown1", update_time=_to_time(42), is_permanent=True, rep_type="unknown1"),
            cvc.CacheRecord(path="unknown2", update_time=_to_time(43), is_permanent=True, rep_type="unknown2"),
        ],
        ["unknown1", "unknown2"]
    ),
    (
        [
            cvc.CacheRecord(path=str(ind), update_time=_to_time(ind), rep_type="svn")
            for ind in six.moves.range(cvc.CacheableArcadia.DIRS_LIMIT + 1)
        ] + [
            cvc.CacheRecord(path=str(0), update_time=_to_time(42), rep_type="svn"),
        ],
        ["1"]
    ),
]


@pytest.fixture()
def vcs_cache():
    return cvc.VCSCache()


class TestVCS(object):

    @pytest.mark.parametrize(["records", "expected_to_delete"], CACHE_TESTS)
    def test__cache_records_dump(self, records, expected_to_delete):
        out = io.BytesIO()
        for record in records:
            out.write(six.ensure_binary(record.dump()))

        new_records = [cvc.CacheRecord.load(line) for line in io.BytesIO(out.getvalue())]
        assert new_records and len(records) == len(new_records)
        for orig_rec, new_rec in zip(records, new_records):
            assert orig_rec == new_rec

    @pytest.mark.parametrize(["records", "expected_to_delete"], CACHE_TESTS)
    def test__cache_records_filtering(self, vcs_cache, records, expected_to_delete):
        to_delete = vcs_cache._get_caches_to_delete(cvc.CacheableArcadia, records)
        assert sorted(to_delete) == sorted(expected_to_delete)
