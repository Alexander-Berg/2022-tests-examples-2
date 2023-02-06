# import pytest
# from urllib3.exceptions import ConnectionError
from sandbox.projects.yabs.auto_supbs_2.lib.matching_funnel_issue_processor.yql_query import get_chyt_analyzer_query, get_auction_analyzer_query
from sandbox.projects.yabs.auto_supbs_2.lib.matching_funnel_issue_processor.yql_query import get_auction_top_competitors_analyzer_query, get_result_path
from sandbox.projects.yabs.auto_supbs_2.lib.matching_funnel_issue_processor.yql_query import get_matching_funnel_yql_query, make_yql_running_message, get_yql_title


def test_get_matching_funnel_yql_query():
    query_text, auction_query_text = get_matching_funnel_yql_query('SUPBS-18584', '155148326', '1', '1', '2022-02-22', '2022-02-23', 'path/to/tmp/folder')
    return query_text, auction_query_text


def test_make_yql_running_message():
    message = make_yql_running_message('155148326', '-1', '-1', '2022-02-22', '2022-02-23', 'https://yql.yandex-team.ru/Operations/test1', 'https://yql.yandex-team.ru/Operations/test2')
    return message


def test_get_chyt_analyzer_query():
    query_text = get_chyt_analyzer_query('SUPBS-18584', '155148326', 'path/to/tmp/folder')
    return query_text


def test_get_yql_title():
    title = get_yql_title('155148326', '-1', '-1', '2022-02-22', '2022-02-23')
    assert title is not None


def test_get_auction_analyzer_query():
    select_percentiles = ',\n '.join('quantile({})(cnt) as AuctionPosition{}'.format((int(item) / 100.0), int(item)) for item in {10, 50, 90})

    query = get_auction_analyzer_query('SUPBS-18584', '155148326', 'path/to/tmp/folder', select_percentiles)
    assert query is not None


def test_get_auction_top_competitors_analyzer_query():
    top_competitors = 10
    auction_top_text = get_auction_top_competitors_analyzer_query('SUPBS-18584', '155148326', 'path/to/tmp/folder', top_competitors)
    assert auction_top_text is not None


def test_get_result_path():
    path = get_result_path('SUPBS-18584', '155148326', 'path/to/tmp/folder', 'tmp_table_name')

    assert path == 'path/to/tmp/folder/SUPBS-18584/155148326/1.1_tmp_table_name'
