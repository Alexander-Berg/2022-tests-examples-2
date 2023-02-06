#!/usr/bin/env python

from StringIO import StringIO
import gzip
import os
from os.path import join as pj
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.queries_pb2 import TTurboRSSItem
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TProcessingDocument
)
from robot.protos.crawl.zoracontext_pb2 import TUkropZoraContext
from quality.functionality.turbo.protos.turbo_context_pb2 import (
    EFeedOrigin,
)


def test_offer_base_no_saas():
    with TurboTest(test_data="data", output="data") as turbo_test:
        doc = _create_document()
        turbo_test.save_pb_to_file([doc], pj(turbo_test.test_data, "rthub--turbo-rss"))
        _unpack_resources(turbo_test)

        turbo_test.run_rthub_parser()
        turbo_test.run_rthub_postprocess()

    results = turbo_test.restore_pb_from_file(pj(turbo_test.output, "rthub-turbo--turbo-documents"), TProcessingDocument)
    ok_doc_urls = set()
    for item in results:
        if item.Status == "ok":
            ok_doc_urls.add(item.Document)
    expected = set([
        'https://spb.profi.ru/autoinstructor/instruktor_po_vozhdeniju_na_mashine_uchenika/',
        'https://spb.profi.ru/autoinstructor/ekstremal_noe_vozhdenie_na_l_du/'
    ])
    assert expected == ok_doc_urls
    assert os.path.getsize(pj(turbo_test.output, "saas@services@turbo@prestable@topics--shard")) == 0


def _compress_content(content):
    out = StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(content)
    return out.getvalue()


def _create_document():
    zora_ctx = TUkropZoraContext()
    turbo_ctx = zora_ctx.TurboContext
    turbo_ctx.FeedOrigin = EFeedOrigin.Value("EFO_OFFER_BASE")

    doc = TTurboRSSItem()
    doc.Url = 'https://spb.profi.ru/prices.yml.gz'
    doc.HttpCode = 200
    doc.LastAccess = 123445
    doc.ZoraCtx = zora_ctx.SerializeToString()
    doc.Content = _compress_content("""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<yml_catalog date="2018-07-17 12:10">
  <shop>
    <name>ПРОФИ.РУ</name>
    <company>OOO ПРОФИ.РУ</company>
    <url>spb.profi.ru</url>
    <platform>Bitrix</platform>
    <version>1.2.45</version>
    <email>email@spb.profi.ru</email>
    <currencies>
      <currency id="RUR" rate="1" />
    </currencies>
    <categories>
      <category id="1">Автоинструкторы</category>
      <category id="2">Мастера красоты</category>
    </categories>
    <cpa>1</cpa>
    <offers>
      <offer id="1">
        <url>https://spb.profi.ru/autoinstructor/instruktor_po_vozhdeniju_na_mashine_uchenika/</url>
        <price>500</price>
        <currencyId>RUR</currencyId>
        <categoryId>1</categoryId>
        <name><![CDATA[Инструктор по вождению на машине ученика в Санкт-Петербурге]]></name>
        <param name="Возможен выезд на дом">да</param>
      </offer>
      <offer id="2">
        <url>https://spb.profi.ru/autoinstructor/ekstremal_noe_vozhdenie_na_l_du/</url>
        <price>800</price>
        <currencyId>RUR</currencyId>
        <categoryId>1</categoryId>
        <name><![CDATA[Экстремальное вождение на льду в Санкт-Петербурге]]></name>
        <param name="Возможен выезд на дом">да</param>
      </offer>
    </offers>
  </shop>
</yml_catalog>""")
    return doc


def _unpack_resources(turbo_test):
    turbo_test.unpack_standard_resources()
