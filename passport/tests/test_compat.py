# coding: utf-8

import yatest.common as yc


def test_lucid_compatibility():
    yc.check_glibc_version(
        yc.binary_path('passport/backend/vault/cli/yav/bin/yav'),
    )
