# -*- coding: utf-8 -*-

from sandbox import sdk2


class PrebillingBackup(sdk2.Resource):
    any_arch = False
    auto_backup = True


class PrebillingBin(sdk2.Resource):
    any_arch = False
    auto_backup = True
    releasable = True


class PrebillingCompareResultrs(sdk2.Resource):
    auto_backup = True
