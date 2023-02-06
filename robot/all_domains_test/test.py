#!/usr/bin/env python
import yatest.common
from os.path import join as pj
from robot.rthub.test.turbo.medium.turbo_test_lib.turbo_test import TurboTest
from robot.rthub.yql.protos.content_plugins_pb2 import (
    TContentPluginsResult,
    THostSettings
)
import json


def test_GetSettingsFromCache_WhenNoSettingsInDoc():
    # ARRANGE

    turbo_test = TurboTest(data_yql=yatest.common.source_path("robot/rthub/test/turbo/medium/postprocess-cache-settings/all_domains_test/data.yql"),
                           output=yatest.common.work_path("test-domain-subdomain"))
    docs = [
        _create_document("https://a.domain1-subdomain0.com"),
        _create_document("https://a.domain0-subdomain1.com"),
        _create_document("https://a.domainNull-subdomain1.com"),
        _create_document("https://a.domain1-subdomainNull.com"),
        _create_document("https://a.domain0-subdomain0.com"),
        _create_document("https://a.domainNull-subdomainNull.com")
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

    def sorted_by_first(arg):
        return sorted(arg, key=lambda t: t[0])

    canon = sorted_by_first([('https://a.domain1-subdomain0.com', _host_settings(False, 0)),
                            ('https://a.domain0-subdomain1.com', _host_settings(True, 0)),
                            ('https://a.domainNull-subdomain1.com', _host_settings(True, 0)),
                            ('https://a.domain1-subdomainNull.com', _host_settings(True, 0)),
                            ('https://a.domain0-subdomain0.com', _host_settings(False, 0)),
                            ('https://a.domainNull-subdomainNull.com', _host_settings(False, 0))])

    assert sorted_by_first(settings) == canon


def _host_settings(cmnt_enabled, ban_stat):
    host_settings = THostSettings()
    host_settings.CmntEnabled = cmnt_enabled
    host_settings.IsInitialized = True
    host_settings.BanStatus = ban_stat

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
    doc.Json = json.dumps(json_string)  # add an image to send document to delay
    doc.FeedUrl = url + "/feed"
    doc.IsFast = True
    if banStatus or cmntEnabled:
        doc.CmntEnabledForHost = cmntEnabled
        doc.BanStatus = banStatus
    return doc


def _unpack_resources(turbo_test):
    turbo_test.unpack_standard_resources()
