from os.path import join as pj

from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import TProcessingDocument
from robot.rthub.yql.protos.queries_pb2 import TTurboRSSItem
from robot.protos.crawl.zoracontext_pb2 import TUkropZoraContext
from quality.functionality.turbo.protos.turbo_context_pb2 import (
    EFeedOrigin,
    EFeedSource,
)
import json
import inspect


def test_empty_document():
    doc = [
        _create_document_with_size(0)
    ]

    expected_feed_errors = ["Parser.EmptyXML"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        turbo_test.unpack_standard_resources()

        # ACT
        turbo_test.run_rthub_parser()
    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)[0]
    feed_error = [error["code"] for error in json.loads(document.Errors)]

    # ASSERT
    assert expected_feed_errors == feed_error


def test_too_big_document():
    doc = [
        _create_document_with_size(250 * 1024 * 1024)
    ]

    expected_feed_errors = ["Parser.TooBigSize"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        # import pdb; pdb.set_trace()
        turbo_test.unpack_standard_resources()

        # ACT
        turbo_test.run_rthub_parser(max_input_message_size=300*1024*1024)
    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)[-1]
    feed_error = [error["code"] for error in json.loads(document.Errors)]

    # ASSERT
    assert expected_feed_errors == feed_error


def _get_func_name():
    return inspect.getframeinfo(inspect.currentframe().f_back).function


def _create_document_with_size(size):
    doc = TTurboRSSItem()
    doc.Url = "https://yandex.ru/feed.xml"
    doc.HttpCode = 200
    doc.LastAccess = 123445
    zora_ctx = TUkropZoraContext()
    turbo_ctx = zora_ctx.TurboContext
    turbo_ctx.FeedOrigin = EFeedOrigin.Value("EFO_WMC")
    turbo_ctx.FeedSource = EFeedSource.Value("EFS_RSS")
    doc.ZoraCtx = zora_ctx.SerializeToString()
    doc.Content = 'a' * size
    return doc
