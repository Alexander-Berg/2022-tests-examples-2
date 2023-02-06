from __future__ import absolute_import

import copy
import json
import pprint
import datetime as dt

from sandbox.common import mds as common_mds
from sandbox.yasandbox.database import mapping

from sandbox.services.modules import mds_cleaner

METAS = {
    105: json.dumps([
        {"type": "file", "key": "105/0/key1"},
    ]),
    106: json.dumps([
        {"type": "file", "key": "106/0/key1"},
        {"type": "file", "key": "106/1/key2"},
    ]),
    107: json.dumps([
        {"type": "file", "key": "107/aaa/key1"},
        {"type": "file", "key": "107/bbb/key2"},
    ]),
    108: json.dumps([
        {"type": "file", "key": "108/aaa/key1"},
    ]),
    109: json.dumps([
        {"type": "file", "key": "109/aaa/key1"},
    ]),
}

STORAGE = {
    "bucket1": {
        "101/key": "",
        "102/key": "",
        "103/key": "",
        "104/key": "",
        "105/0/key1": "",
        "105/resource": METAS[105],
        "203/key": "",
        "204/key": "",
        "106/resource": METAS[106],
        "106/0/key1": "",
        "106/1/key2": "",
        "106/2/key3": "",
        "106/aaa/key4": "",
        "107/resource": METAS[107],
        "107/aaa/key1": "",
        "107/bbb/key2": "",
        "107/ccc/key3": "",
        "107/1/key4": "",
        "108/resource": METAS[108],
        "109": METAS[109],
        "110": "",
        "110/resource": "",
        "110/resource.index": "",
        "111/zzz/key1": "",
        "111/yyy/key2": "",
        "111/resource": "",  # invalid meta
        "112": "",
        "112/resource": "",  # tarball without index
    },
    "bucket2": {
        "201/a/key": "",
        "202/a/key": "",
        "203/key": "",
        "204": "",
        "aaa": "",
    },
}

RESOURCES_BY_BUCKETS = {
    "bucket1": [102, 103, 105, 106, 107, 108, 109, 110, 111, 112],
    "bucket2": [203, 204],
}

EXPECTED_STORAGE = {
    "bucket1": {
        "102/key": "",
        "103/key": "",
        "105/0/key1": "",
        "105/resource": METAS[105],
        "106/resource": METAS[106],
        "106/0/key1": "",
        "106/1/key2": "",
        "107/resource": METAS[107],
        "107/aaa/key1": "",
        "107/bbb/key2": "",
        "108/resource": METAS[108],
        "109": METAS[109],
        "110": "",
        "110/resource": "",
        "110/resource.index": "",
        "111/zzz/key1": "",
        "111/yyy/key2": "",
        "111/resource": "",
        "112": "",
        "112/resource": "",
    },
    "bucket2": {
        "203/key": "",
        "204": "",
    },
}


# noinspection PyPep8Naming
class S3ClientMock(object):
    LAST_MODIFIED = dt.datetime(1, 1, 1)

    def __init__(self):
        self.storage = {}

    def list_objects_v2(self, Bucket=None, **_):
        result = {}
        objects = self.storage.get(Bucket)
        if objects is not None:
            result["Contents"] = [
                {"Key": key, "Size": 0, "LastModified": self.LAST_MODIFIED} for key in sorted(objects)
            ]
        return result

    def get_object(self, Bucket=None, Key=None):
        return {"Body": [self.storage[Bucket][Key]]}

    def delete_objects(self, Bucket=None, Delete=None):
        resources = self.storage.get(Bucket, {})
        for obj in Delete["Objects"]:
            resources.pop(obj["Key"], None)
        return {}


class ResourceMappingMock(object):
    def __init__(self, rids_by_bucket):
        self.rids_by_bucket = rids_by_bucket
        self.__id__in = None
        self.__mds__namespace = None

    def objects(self, id__in=None, mds__namespace=None):
        self.__id__in = id__in
        self.__mds__namespace = mds__namespace
        return self

    def fast_scalar(self, *args):
        assert len(args) == 1 and args[0] == "id"
        return set(self.rids_by_bucket.get(self.__mds__namespace, [])) & set(self.__id__in)


def test__cleanup_bucket_garbage(monkeypatch):
    s3 = S3ClientMock()
    monkeypatch.setattr(common_mds.S3, "s3_client", lambda _: s3)
    bucket_stats = {"objects_parts_size": 102400, "deleted_objects_size": 204800}
    monkeypatch.setattr(common_mds.S3, "bucket_stats", staticmethod(lambda _: bucket_stats))
    resource_mapping = ResourceMappingMock({})
    monkeypatch.setattr(mapping, "Resource", resource_mapping)
    service = mds_cleaner.MDSCleaner()

    s3.storage = copy.deepcopy(STORAGE)
    resource_mapping.rids_by_bucket = RESOURCES_BY_BUCKETS
    for bucket in STORAGE:
        gc_state = mds_cleaner.GCState(bucket)
        assert gc_state.load(gc_state.dump()) == gc_state
        assert not gc_state.clean
        service._cleanup_bucket_garbage(gc_state, None, "test")
        assert gc_state.load(gc_state.dump()) == gc_state
        assert gc_state.clean
    assert s3.storage == EXPECTED_STORAGE, pprint.pformat(s3.storage)
