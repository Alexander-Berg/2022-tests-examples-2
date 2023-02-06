#!/usr/bin/env python

import yatest.common

from delivery_common import DeliveryTestParams
from delivery_common import do_run_delivery


def test_entry(links):
    params = DeliveryTestParams(yatest.common.get_param_dict_copy())
    do_run_delivery(params, links)
