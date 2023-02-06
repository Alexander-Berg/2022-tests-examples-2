#!/usr/bin/env python

from delivery_common import DeliveryTargetTestParams
from delivery_common import do_run_delivery


# This test runs local delivery
# for single specified target.
# To run - set TARGET_TEST_ENABLED = True
# and fill in parameter values.
# See also https://a.yandex-team.ru/arc/trunk/arcadia/robot/jupiter/delivery/cmpy/delivery_config.json
# for current delivery config in production.
#
# IMPORTANT: run test with --test-disable-timeout.

TARGET_TEST_ENABLED = False
TARGET_TEST_PARAMS = {
    'delivery_target': 'delivery.cleanup.<target-name>',
    'delivery_cluster': 'hahn',
    'delivery_mr_prefix': '<yt-path>',
    'delivery_timeout': 28800,
}


def test_entry(links):
    if TARGET_TEST_ENABLED:
        params = DeliveryTargetTestParams(TARGET_TEST_PARAMS)
        do_run_delivery(params, links)
