# coding: utf-8

import six
import yatest.common as yc


if six.PY3:
    YAV_DEPLOY_BINARY = 'passport/backend/vault/cli/yav_deploy/bin_py3/yav-deploy'
else:
    YAV_DEPLOY_BINARY = 'passport/backend/vault/cli/yav_deploy/bin/yav-deploy'


def test_lucid_compatibility():
    yc.check_glibc_version(
        yc.binary_path(YAV_DEPLOY_BINARY),
    )
