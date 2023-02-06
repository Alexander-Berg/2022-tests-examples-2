import logging
import os
import pytest
import tempfile
import shutil

import library.python.resource as lpr
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.report_utils import make_logs_statistics_report_data, make_logs_statistics_report_text
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.report import CmpCliReport
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.analyze_logs import (
    Agg, GroupBy, Func, aggregate_statistics,
    hitlogid_bannerid_eventcost_rank, hitlogid_bannerid_clicks, hitlogid_bannerid_shows
)
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.compare import ChunksData, CLI_DIFF_DIRNAME, SingleComparisonResult
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.operations import avg, size


def test_make_logs_statistics_report_text():
    aggregated_statistics = {
        'event': {
            'field': (1, 2, 3, 4),
            '<b>bold_field</b>': (2, 2, 8, 16)
        }
    }
    result = make_logs_statistics_report_text(aggregated_statistics)
    expected = lpr.find('/test_render_log_statistics_expected.html')
    assert result == expected


@pytest.fixture
def log_dict():
    return {
        'HitLogID': [1, 1, 2, 2, 3],
        'BannerID': [4, 4, 5, 6, 7],
        'EventCost': [0, 10, 11, 12, 13],
        'Rank': [100, 100, 100, 100, 100],
        'CounterType': [1, 1, 1, 2, 2],
    }


def test_make_logs_statistics_report_from_log_data(log_dict):
    statistics = {
        'data': {'event': log_dict},
        'counts': {'event': 5}
    }
    config = {
        'event': {
            'EventCost': [sum, avg],
            ('EventCost', 'Rank'): [sum, avg],
            'Rank': [avg],
            GroupBy(by=('HitLogID', 'BannerID'), aggs=Agg('EventCost', 'max'), name='MaxEventCost'): [sum, avg],
            Func(function=hitlogid_bannerid_eventcost_rank, name='<b>dot(MaxEventCost, MaxRank)</b>', used_fields=tuple()): [sum, avg],
            Func(function=hitlogid_bannerid_clicks, name='<b>Clicks</b>', used_fields=tuple()): [size],
            Func(function=hitlogid_bannerid_shows, name='<b>Shows</b>', used_fields=tuple()): [size],
        }
    }
    aggregates = aggregate_statistics(statistics, config)
    logs_statistics_data = make_logs_statistics_report_data(aggregates, aggregates, aggregates, aggregates)
    report = make_logs_statistics_report_text(logs_statistics_data)
    expected = lpr.find('/test_make_logs_statistics_report_from_log_data.html')
    assert report == expected


@pytest.fixture
def tempdir():
    d = tempfile.mkdtemp(prefix='pytest_data_')
    logging.debug('Tempdir for tests: %s', d)
    yield d
    shutil.rmtree(d)


def test_move_cli_report(tempdir):
    cli_report = CmpCliReport(cli_report_dir=tempdir)
    chunks_data = ChunksData()
    results = {
        '1603300073800': SingleComparisonResult(
            test_id='1603300073800',
            has_diff=True,
            pre_code=200,
            test_code=301,
            handler='handler',
            diff_tags=set({'logs_data', 'ext_req'}),
            diff='--- pre\n+++ test\n@@ -1,3 +1,3 @@\n-1\n 2\n 3\n+4\n',
            request='GET /count/WCyejI_zO4m0BGO0r0X8c4xIgP-ZOWK0J04nPhsLNm00000ueEWJy0BWdFY02_050Q06nA01oGOm0sDlfBlNHz46C9UOvgIxrqUVVkEt7tCkwZDW0G000010c0wmXepxnlJkwqVW3m6e4S24FUaIYBjW7ggPqllO5S6AzkoZZxpyO_395l0_WHUe5mcP6D0O8VWOW1cm6RWP_m4I06aGZ3C5WuAxAXecqIr2D6PWbosZ20wGQP9LHkNgvYUMH6UygxuEEs02M8D6L7ES-HsEGG40~1=WSuejI_zO5419Gu0P1UKSoC8KGAEoFRWgHE00VkSkvC1Y07K-V7-I901uCxEx3UO0VgElFS_e07gvPZiDwW1-8wyzp-u0RQcvi0Us060p8qSu06cXOiSw06Q0VW1ykRblW6W0hJexXUm0uU00OW5fA81a0M2em6m1Q4fk0MvAU05FQW6nA01k0U01V47002WX9gqzyaAa0CwFjXvq_WAWBKOsGkVVkEt7tCkwkWBfA81Y0povkM-0QaCPgMveuBJwR_e39i2c0tAySNwZJkW3h-4FTaFW132h_aMq12vyx9Vc16sxGQX0-yoNJgQdZ_f4eYxO1wgcTBxc1C4g1F7pkhU-xl9nTu1u1EvAQ0KkIce58AZXEc_zGNe50pG5S2YyFi5s1N1YlRieu-y_6EO5j2ry_i5e1RGsFZx1R0MlGF95j0MykRblW615vWNdUkk8S0NDTWNm8Gzw1S5cHYW61Mm6D3yj_m5k1W5-1ZulvIlkOwHx3w06OaPp0AG6G6W6SIW0HW0KWVH3MNqIImDaUOzGhS0LA-V1hAvb5Wx65qa4TAB60YU8ZRkg5LFgIeN4eW3J02-_804In43svBtEU2Jns9CSRELAgMpSPFjm040~1 HTTP/1.1\r\ncookie: is_gdpr=0; yandexuid=5176812611603465008; i=SL4M6ZstYlBLxU%2BOFX8mlOZfCeRzVbcpkInz2oTEDQmjEabXcwHsd91dnp%2BU95vDXkvHHSjtc%2BF1nkZHvb8TQjq628c%3D; ymex=1606057112.oyu.2555079461603465009%231918825009.yrts.1603465009%231918825112.yrtsi.1603465112; yp=1635001054.brd.0896040003%231635001054.cld.2275473%231635001054.gd.5kGJj%2F%2F%2B8eVrdHnpPwiJvkaGND8FvtygsdGWNkz%2BFXBSIK9q%2Be1IviQuDCFA6%2FCDtY1KlA%253D%253D%231603551512.yu.2555079461603465009%231619233114.szm.1%3A1024x768%3A1024x635; my=YwA%3D; is_gdpr_b=CIecPxCxCCgC; _ym_uid=16035952541042386759; _ym_d=1603595254; mda=0; ys=ybzcc.ru%23svt.1%23def_bro.1; yabs-exp-sid=8dfdd2c712345678\r\naccept: application/json\r\naccept-encoding: gzip,deflate\r\ncontent-encoding: gzip\r\ncontent-type: application/json\r\nhost: an.yandex.ru\r\nuser-agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.137 YaBrowser/17.4.1.919 Yowser/2.5 Safari/537.36\r\nx-forwarded-for: 37.212.93.21, 2a02:6b8:c11:e96:10e:faf8:0:5e9f, 2a02:6b8:c0c:1399:0:1452:48cc:1e87\r\nx-forwarded-proto: https\r\nx-forwarded-proto-version: HTTP/1.1\r\nx-real-ip: 37.212.93.21\r\nx-real-port: 60140\r\nx-request-origin-ip: 2a02:6b8:c0b:4014:0:1452:6660:216a\r\nx-yabs-balancer-samogon-key: 2\r\nx-yabs-debug-options-json: {\"logs\": true, \"business\": false, \"mx_zero_features\": false, \"filter_log\": false, \"trafaret\": false, \"debug_log\": false, \"keywords\": false, \"exts\": true, \"trace\": false, \"force_event_log\": false, \"match_log\": false, \"ext_http_entities\": false, \"mx\": false}\r\nx-yabs-debug-output: proto-binary\r\nx-yabs-debug-token: 8dfdd2c712345678\r\nx-yabs-deterministic-request-id: 1\r\nx-yabs-presets-from-balancer: W10=\r\nx-yabs-test-random: 2996909253\r\nx-yabs-test-time: 1603648870\r\nx-yabs-request-id: 1603300073800\r\nConnection: Close\r\n\r\n',  # noqa: E501
        )
    }
    chunk_name = '0'
    chunks_data.add_unified_diffs_chunk(results, chunk_name)
    chunks_data.add_cli_diffs_index(results.values(), 'chunk')
    chunks_data.merge_cli_diffs_indices()
    assert set(os.listdir(chunks_data._chunk_dir)) == set(['tests', CLI_DIFF_DIRNAME, 'report_index.txt', 'diff'])
    assert set(os.listdir(chunks_data.get_cli_diffs_dir())) == set(['0.diff', '0.requests'])
    assert os.path.exists(chunks_data.get_cli_diffs_index())
    assert [CLI_DIFF_DIRNAME] == os.listdir(cli_report.get_local_path())
    cli_report.move_from_chunks_data(chunks_data)
    assert set(os.listdir(chunks_data._chunk_dir)) == set(['tests', 'diff'])
    assert set(os.listdir(cli_report.get_local_path())) == set([CLI_DIFF_DIRNAME, 'report_index.txt', 'README.md'])
    chunks_data.clear()
