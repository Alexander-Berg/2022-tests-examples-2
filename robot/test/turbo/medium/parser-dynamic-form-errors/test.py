#!/usr/bin/env python

from os.path import join as pj

from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import TContentPluginsResult
from robot.rthub.yql.protos.queries_pb2 import TTurboRSSItem
from robot.protos.crawl.zoracontext_pb2 import TUkropZoraContext
from quality.functionality.turbo.protos.turbo_context_pb2 import (
    EFeedOrigin,
    EFeedSource,
)
import json
import inspect


def test_missing_required_attr_name_in_textarea():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="input-block">
                        <span type="textarea" required="true" label="Это поле видно, когда почтой и адрес test" placeholder="Да"></span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
            </form>""")
    ]

    expected_document_errors = ["Parser.Item.TurboContent.NoRequiredAttr"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_empty_input_block():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                     <div type="input-block">
                     </div>
                     <div type="result-block">
                        <span type="text" field="description"></span>
                     </div>
             </form>""")
    ]

    expected_document_errors = ["Parser.Item.TurboContent.EmptyBlockInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_empty_result_block():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                     <div type="input-block">
                         <span type="checkbox" name="foo" content="single"></span>
                     </div>
                     <div type="result-block">
                     </div>
             </form>""")
    ]

    expected_document_errors = ["Parser.Item.TurboContent.EmptyBlockInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_result_block_does_not_exist():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                     <div type="input-block">
                         <span type="checkbox" name="foo" content="single"></span>
                     </div>
             </form>""")
    ]

    expected_document_errors = ["Parser.Item.TurboContent.EmptyBlockInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_checked_should_be_bool():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="input-block">
                        <span type="radio" name="delivery" label="label">
                            <span type="option" value="courier1" checked="istina" label="Курьером, 500₽" meta="1 день, Внутри МКАД"> </span>
                            <span type="option" value="courier2" checked="false" label="Курьером, 1500₽" meta="0 день, Снаружи МКАД"> </span>
                        </span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
            </form>""")
    ]

    expected_document_errors = ["Parser.Item.TurboContent.InvalidValue"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_count_of_options_should_be_ge_than_1():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="input-block">
                        <span type="radio" name="delivery" label="label">
                        </span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
            </form>"""),
    ]

    expected_document_errors = ["Parser.Item.TurboContent.TooFewOptionsInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_unexpected_type_in_span():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="input-block">
                        <span type="checkbox" name="foo" content="single"></span>
                        <span type="unexpected" name="delivery" label="label"></span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
            </form>"""),
    ]

    expected_document_errors = ["Parser.Item.TurboContent.InvalidLineTypeInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_unexpected_input_type():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="input-block">
                        <span type="input" required="true" label="label1" name="input-text" name="name" placeholder="Да" input-type="text"></span>
                        <span type="input" required="true" label="label2" name="input-numb" name="name" placeholder="Да" input-type="undefined"></span>
                    </div>
                    <div type="result-block">
                        <span type="link" field="help"></span>
                    </div>
            </form>"""),
    ]

    expected_document_errors = ["Parser.Item.TurboContent.InvalidValue"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def test_unexpected_type_in_block():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="unexpected-block">
                        <span type="unexpected" name="delivery" label="label"></span>
                    </div>
                    <div type="input-block">
                        <span type="checkbox" name="foo" content="single"></span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
            </form>"""),
    ]

    expected_document_errors = ["Parser.Item.TurboContent.InvalidBlockTypeInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def multiple_input_blocks():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="input-block">
                        <span type="checkbox" name="foo" content="single"></span>
                    </div>
                    <div type="input-block">
                        <span type="checkbox" name="foo" content="single"></span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
            </form>"""),
    ]

    expected_document_errors = ["Parser.Item.TurboContent.MultipleBlocksOfTheSameTypeInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def multiple_result_blocks():
    doc = [
        _create_document_with_form(
            """<form data-type="dynamic-form" end_point="http://exmaple.com/post-form.php">
                    <div type="input-block">
                        <span type="checkbox" name="foo" content="single"></span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
                    <div type="result-block">
                        <span type="text" field="description"></span>
                    </div>
            </form>"""),
    ]

    expected_document_errors = ["Parser.Item.TurboContent.MultipleBlocksOfTheSameTypeInDynamicForm"]

    with TurboTest(output=_get_func_name()) as turbo_test:
        turbo_test.save_pb_to_file(doc, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)
        # ACT
        turbo_test.run_rthub_parser()

    document = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)[0]
    document_error = [error["code"] for error in json.loads(document.DocumentErrors)]

    # ASSERT
    assert expected_document_errors == document_error


def _unpack_resources(turbo_test):
    turbo_test.unpack_standard_resources()


def _create_document_with_form(form):
    doc = TTurboRSSItem()
    doc.Url = "https://yandex.ru/feed.xml"
    doc.HttpCode = 200
    doc.LastAccess = 123445
    zora_ctx = TUkropZoraContext()
    turbo_ctx = zora_ctx.TurboContext
    turbo_ctx.FeedOrigin = EFeedOrigin.Value("EFO_WMC")
    turbo_ctx.FeedSource = EFeedSource.Value("EFS_RSS")
    doc.ZoraCtx = zora_ctx.SerializeToString()
    doc.Content = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n
        <rss    xmlns:yandex=\"http://news.yandex.ru\"    xmlns:media=\"http://search.yahoo.com/mrss/\" xmlns:turbo=\"http://turbo.yandex.ru\" version=\"2.0\">
            <channel>
            <turbo:cms_plugin>C125AEEC6018B4A0EF9BF40E6615DD17</turbo:cms_plugin>
                <title>title</title>
                <link>https://yandex.ru/feed.xml</link>
                <description>desc</description>
                <language>ru</language>
                <item turbo="true">
                    <title>Textarea Parser</title>
                    <turbo:content><![CDATA[""" + form + """
                    ]]></turbo:content>
                    <author>unknown</author>
                    <pubDate>01 Jan 2017 08:00:00 EST</pubDate>
                    <link>https://yandex.ru/textarea-block-parser</link>
                    <enclosure url="http://example.com/image.jpg" type="image/jpeg" />
                </item>
            </channel>
        </rss>"""
    return doc


def _get_func_name():
    return inspect.getframeinfo(inspect.currentframe().f_back).function
