from __future__ import unicode_literals, print_function

from sandbox.yasandbox.database import mapping


class TestBucket(object):
    def test__abcd_account_name(self):
        assert mapping.Bucket.abcd_account_name("service") is None
        assert mapping.Bucket.abcd_account_name("service-123") is None
        assert mapping.Bucket.abcd_account_name("sandbox-name") is None
        assert mapping.Bucket.abcd_account_name("sandbox-123") == mapping.Bucket.DEFAULT_ABCD_ACCOUNT
        assert mapping.Bucket.abcd_account_name("sandbox-321") == mapping.Bucket.DEFAULT_ABCD_ACCOUNT
        assert mapping.Bucket.abcd_account_name("sandbox-321-name") == "name"
        assert mapping.Bucket.abcd_account_name("sandbox-321-name_1") == "name_1"
        assert mapping.Bucket.abcd_account_name("sandbox-321-name-1") == "name-1"
        assert mapping.Bucket.abcd_account_name("sandbox-321-name-1-2-3") == "name-1-2-3"
