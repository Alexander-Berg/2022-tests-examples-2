#!/usr/bin/env python
import yatest.common
from os.path import join as pj
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TContentPluginsResult,
    THostSettings,
)
import json


def test_GetSettingsFromCache_WhenNoSettingsInDoc():
    # ARRANGE
    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-cache-settings/delay_test/data.yql"),
                           output=yatest.common.work_path("doc_without_settings"))
    docs = [
        _create_document("https://throw-error.doc-without-settings.test"),
    ]

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        _unpack_resources(turbo_test)
        turbo_test.run_rthub_postprocess()

    # ASSERT
    docs_in_delayed = turbo_test.restore_pb_from_file(pj(turbo_test.output, "turbo-pages@rthub--loopback-1-prestable"), TContentPluginsResult)
    settings = []
    for doc in docs_in_delayed:
        settings.append((doc.Url, doc.HostSettings))

    assert settings == [('https://throw-error.doc-without-settings.test', _host_settings(True, 1))]


def test_GetSettingsFromCache_WhenBanStatusIsNoInformation():
    # ARRANGE
    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-cache-settings/delay_test/data.yql"),
                           output=yatest.common.work_path("ban_status_is_noinformation"))
    docs = [
        _create_document("https://ban-status-is-noinformation.test", banStatus=3, cmntEnabled=False),  # 3 - NoInformations
    ]

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        _unpack_resources(turbo_test)
        turbo_test.run_rthub_postprocess()

    # ASSERT
    docs_in_delayed = turbo_test.restore_pb_from_file(pj(turbo_test.output, "turbo-pages@rthub--loopback-1-prestable"), TContentPluginsResult)
    settings = []
    for doc in docs_in_delayed:
        settings.append((doc.Url, doc.HostSettings))

    assert settings == [('https://ban-status-is-noinformation.test',  _host_settings(False, 1))]


def test_NoGetSettingsFromCache_WhenSettingsInDoc():
    # ARRANGE
    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-cache-settings/delay_test/data.yql"),
                           output=yatest.common.work_path("doc_with_settings"))
    docs = [
        _create_document("https://doc-with-settings.test", banStatus=0, cmntEnabled=False),
    ]

    # ACT
    with turbo_test:
        turbo_test.save_pb_to_file(docs, pj(turbo_test.test_data, "rthub--turbo-json"))
        _unpack_resources(turbo_test)

        turbo_test.run_rthub_postprocess()

    # ASSERT
    docs_in_delayed = turbo_test.restore_pb_from_file(pj(turbo_test.output, "turbo-pages@rthub--loopback-1-prestable"), TContentPluginsResult)
    settings = []
    for doc in docs_in_delayed:
        settings.append((doc.Url, doc.HostSettings))

    assert settings == [('https://doc-with-settings.test',  _host_settings(False, 0))]  # No need to update settings from cache, if settings already exisst in document


def _host_settings(cmnt_enabled, ban_stat):
    host_settings = THostSettings()
    host_settings.CmntEnabled = cmnt_enabled
    host_settings.BanStatus = ban_stat
    host_settings.IsInitialized = True

    return host_settings.SerializeToString()


def _create_document(url, banStatus=None, cmntEnabled=None):
    json_string = [
        {
            "url": url,
            "title": "title",
            "noindex": "yandex",
            "content": [{
                "content": [{"content_type": "image", "src": {"__image": url+"/image/1.jpg"}, "alt": "alt"}]
            }]
        }
    ]

    doc = TContentPluginsResult()
    doc.Url = url
    doc.SaasKey = url
    doc.Json = json.dumps(json_string)    # add an image to send document to delay
    doc.FeedUrl = url + "/feed"
    doc.IsFast = True
    if banStatus is not None or cmntEnabled is not None:
        host_settings = THostSettings()
        host_settings.CmntEnabled = cmntEnabled
        host_settings.BanStatus = banStatus
        host_settings.IsInitialized = True
        doc.HostSettings = host_settings.SerializeToString()
    return doc


def _unpack_resources(turbo_test):
    turbo_test.unpack_standard_resources()
