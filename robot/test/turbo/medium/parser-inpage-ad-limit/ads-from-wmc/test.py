#!/usr/bin/env python

from os.path import join as pj
import json
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.queries_pb2 import TTurboRSSItem
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TContentPluginsResult
)
from robot.protos.crawl.zoracontext_pb2 import TUkropZoraContext
from quality.functionality.turbo.protos.turbo_context_pb2 import (
    EFeedOrigin,
    EFeedSource,
)


def test_get_feed_error_if_isinpage_is_true_and_no_alias_for_inpage_ad():
    # ARRANGE
    turbo_test = TurboTest(output="no_inpage_alias_test")

    docs = [_create_document("https://no-inpage-alias.test", [("general-ad-alias", None, None, None)])]
    expected_docs_errors = [("https://no-inpage-alias.test", ["Parser.Item.InpageAliasNotSpecified"])]

    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)

        # ACT
        turbo_test.run_rthub_parser()

    docs_status = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)
    docs_status = sorted([(doc.FeedUrl, [error['code'] for error in json.loads(doc.DocumentErrors)]) for doc in docs_status], key=lambda x: x[0])

    # ASSERT
    assert docs_status == expected_docs_errors


def test_get_feed_error_if_same_alias_name_in_inpage_block(links):
    # ARRANGE
    turbo_test = TurboTest(output="alias_test")

    docs = [_create_document("https://same-aliases.test", [("ad", "ad", None, None)])]
    expected_docs_errors = [("https://same-aliases.test", ["Parser.Item.SameInpageAliasAndMainAlias"])]

    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)

        # ACT
        turbo_test.run_rthub_parser()

    docs_status = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)
    docs_status = sorted([(doc.FeedUrl, [error['code'] for error in json.loads(doc.DocumentErrors)]) for doc in docs_status], key=lambda x: x[0])

    # ASSERT
    assert docs_status == expected_docs_errors


def test_get_feed_error_if_more_than_one_inpage_blocks(links):
    # ARRANGE
    turbo_test = TurboTest(output="inpage_count_test")
    docs = [
        _create_document("https://1-inpage-blocks.test", [("m_ad", "m_inpage_ad", None, None)]),
        _create_document("https://1-touch-inpage-and-1-desktop-inpage.test", [("m_ad1", "m_inpage_ad1", True, None), ("d_ad2", "d_inpage_ad2", False, True)]),
        _create_document("https://2-touch-inpage.test", [("m_ad1", "m_inpage_ad1", True, None), ("m_ad2", "m_inpage_ad2", True, None)]),
        _create_document("https://2-desktop-inpage.test", [("d_ad1", "d_inpage_ad1", False, True), ("d_ad2", "d_inpage_ad2", False, True)]),
        _create_document("https://1-inpage-for-touch-and-desktop.test", [("d_ad1", "d_inpage_ad1", True, True)])
    ]

    expected_docs_errors = [
        ("https://1-inpage-blocks.test", []),
        ("https://1-inpage-for-touch-and-desktop.test", []),
        ("https://1-touch-inpage-and-1-desktop-inpage.test", []),

        ("https://2-desktop-inpage.test", ["Parser.Item.MoreThanOneInpageAdBlock"]),
        ("https://2-touch-inpage.test", ["Parser.Item.MoreThanOneInpageAdBlock"])
    ]

    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)

        # ACT
        turbo_test.run_rthub_parser()

    docs_status = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub--turbo-json"), TContentPluginsResult)
    docs_status = sorted([(doc.FeedUrl, [error['code'] for error in json.loads(doc.DocumentErrors)]) for doc in docs_status], key=lambda x: x[0])

    # ASSERT
    assert docs_status == expected_docs_errors


def _create_document(url, inpage_ad=[]):
    ads_block = ""
    for i in inpage_ad:
        alias, inpage_alias, is_mobile, is_desktop = i
        tmp = "<figure inpage=true"
        tmp += ' data-turbo-ad-id="{}"'.format(alias)
        if inpage_alias:
            tmp += ' data-turbo-inpage-ad-id="{}"'.format(inpage_alias)
        if is_mobile is not None:
            tmp += ' data-platform-mobile={}'.format("true" if is_mobile else "false")
        if is_desktop is not None:
            tmp += ' data-platform-desktop={}'.format("true" if is_desktop else "false")
        tmp += "></figure>\n "
        ads_block += tmp

    doc = TTurboRSSItem()
    doc.Url = url
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
                <title>title</title>
                <link>""" + url + """</link>
                <description>desc</description>
                <language>ru</language>

                <item turbo=\"true\">
                    <title>title</title>
                    <link>""" + url + """/0</link>
                    <turbo:topic>topic</turbo:topic>
                    <turbo:source>""" + url + """/feed/rss/</turbo:source>
                        <turbo:content>
                        <![CDATA[
                            <header>
                                <h1>Ресторан «Полезный завтрак»</h1>
                                <h2>Вкусно и полезно</h2>
                                <figure>
                                    <img src="https://avatars.mds.yandex.net/get-sbs-sd/403988/e6f459c3-8ada-44bf-a6c9-dbceb60f3757/orig">
                                </figure>
                                <menu>
                                    <a href="http://example.com/page1.html">Пункт меню 1</a>
                                    <a href="http://example.com/page2.html">Пункт меню 2</a>
                                </menu>
                            </header>
                            """ + ads_block + """
                            <p>Как хорошо начать день? Вкусно и полезно позавтракать!</p>
                            <p>Приходите к нам на завтрак. Фотографии наших блюд ищите <a href="#">на нашем сайте</a>.</p>
                            <h2>Меню</h2>
                            <figure>
                                <img src="https://avatars.mds.yandex.net/get-sbs-sd/369181/49e3683c-ef58-4067-91f9-786222aa0e65/orig">
                                <figcaption>Омлет с травами</figcaption>
                            </figure>
                            <p>В нашем меню всегда есть свежие, вкусные и полезные блюда.</p>
                            <p>Убедитесь в этом сами.</p>
                            <p>Наш адрес: <a href="#">Nullam dolor massa, porta a nulla in, ultricies vehicula arcu.</a></p>
                            <p>Фотографии — http://unsplash.com</p>
                        ]]>
                    </turbo:content>
                </item>
            </channel>
        </rss>"""
    return doc


def _unpack_resources(turbo_test):
    turbo_test.unpack_standard_resources()
