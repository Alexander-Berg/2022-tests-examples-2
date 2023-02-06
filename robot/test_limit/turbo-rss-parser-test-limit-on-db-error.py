#!/usr/bin/env python

from os.path import join as pj

from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import TContentPluginsResult
from collections import Counter


def test_rthub_turbo_rss_parser_with_db_error(links):
    turbo_test = TurboTest()

    with turbo_test:
        turbo_test.unpack_standard_resources()

        output1 = pj(turbo_test.output, "ok")
        output2 = pj(turbo_test.output, "error")

        # ACT
        turbo_test.output = output1
        turbo_test.run_rthub_parser()

        turbo_test.output = output2
        turbo_test.run_rthub_parser({'KIKIMR_PROXY': 'incorrect_endpoint'})

        # ASSERT
        items_when_db_ok = turbo_test.restore_pb_from_file(pj(output1, "rthub--turbo-json"), TContentPluginsResult)
        items_when_db_error = turbo_test.restore_pb_from_file(pj(output2, "rthub--turbo-json"), TContentPluginsResult)

        items_when_db_ok_count = Counter(x.FeedUrl for x in items_when_db_ok)
        items_when_db_error_count = Counter(x.FeedUrl for x in items_when_db_error)

        items_when_db_error_count = sorted(items_when_db_error_count.items(), key=lambda x: x[0])
        items_when_db_ok_count = sorted(items_when_db_ok_count.items(), key=lambda x: x[0])

    assert items_when_db_error_count == [('feed-30items.com/feed', 10), ('feed-5items.com/feed', 5)]
    assert items_when_db_ok_count == [('feed-30items.com/feed', 30), ('feed-5items.com/feed', 5)]
