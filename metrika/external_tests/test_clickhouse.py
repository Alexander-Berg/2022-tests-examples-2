from metrika.pylib.clickhouse import ClickHouse, Query
from metrika.pylib.log import base_logger, init_logger
import pytest
import requests_mock
import os
import json
from requests.exceptions import RequestException, HTTPError
from six.moves import collections_abc

logger = base_logger.getChild('clickhouse.tests')
init_logger('mtutils', stdout=True)
init_logger('urllib3', stdout=True)


@pytest.fixture()
def ch_credits():
    user = os.getenv('CH_USER')
    password = os.getenv('CH_PASSWORD')
    yield user, password


@pytest.fixture()
def ch_one_host(ch_credits):
    ch = ClickHouse(host='clickhouse.metrika.yandex.net', user=ch_credits[0], password=ch_credits[1], check_select=False)
    yield ch


@pytest.fixture()
def ch_many_hosts(ch_credits):
    ch = ClickHouse(host=['mtch01k.metrika.yandex.net', 'mtch01m.metrika.yandex.net'], user=ch_credits[0], password=ch_credits[1], check_select=False)
    yield ch


@pytest.fixture()
def ch_many_weighted_hosts(ch_credits):
    ch = ClickHouse(host=['mtch01k.metrika.yandex.net', 'mtch01m.metrika.yandex.net'], user=ch_credits[0], password=ch_credits[1], check_select=False, round_robin_hosts=False)
    yield ch


@pytest.fixture()
def query():
    yield Query(query="select hostName() as h")


@pytest.fixture()
def query_stream():
    yield Query(query="SELECT arrayJoin(range(1000)) AS x", stream=True)


@pytest.fixture()
def query_many_lines():
    yield Query(query="SELECT arrayJoin(range(1000)) AS x")


def test_one_host(ch_one_host, query):
    """
    :param (ClickHouse) ch_one_host:
    :param (Query) query:
    """
    result = ch_one_host.execute(query, retry_kwargs={'exception_to_check': RequestException})

    logger.debug(json.dumps(result.data))

    assert result.data[0].h in ('mtch01k.metrika.yandex.net', 'mtch01m.metrika.yandex.net')


def test_many_hosts(ch_many_hosts, query):
    """
    :param (ClickHouse) ch_many_hosts:
    :param (Query) query:
    """
    result = ch_many_hosts.execute(query)
    assert result.data[0].h == 'mtch01k.metrika.yandex.net'

    result = ch_many_hosts.execute(query)
    assert result.data[0].h == 'mtch01m.metrika.yandex.net'

    with requests_mock.Mocker() as m:
        m.get('http://mtch01k.metrika.yandex.net:8123', status_code=503)
        m.get('http://mtch01m.metrika.yandex.net:8123', real_http=True)

        result = ch_many_hosts.execute(query)

    assert result.data[0].h == 'mtch01m.metrika.yandex.net'


def test_many_failed_hosts(ch_many_hosts, query):
    """
    :param (ClickHouse) ch_many_hosts:
    :param (Query) query:
    """
    with pytest.raises(HTTPError):
        with requests_mock.Mocker() as m:
            m.get('http://mtch01k.metrika.yandex.net:8123', status_code=503)
            m.get('http://mtch01m.metrika.yandex.net:8123', status_code=501)

            ch_many_hosts.execute(query, retry_kwargs={'exception_to_check': HTTPError})


def test_query_stream(ch_one_host, query_stream):
    result = ch_one_host.execute(query_stream)
    assert isinstance(result, collections_abc.Iterable)

    i = None
    for i, line in enumerate(result):
        assert line.x == i

    assert i == 999

    i = None
    for i, line in enumerate(result):
        assert line

    assert i is None


def test_result_iterable(ch_one_host, query_many_lines):
    result = ch_one_host.execute(query_many_lines)
    assert isinstance(result, collections_abc.Iterable)

    i = None
    for i, line in enumerate(result):
        assert line.x == i

    assert i == 999

    i = None
    for i, line in enumerate(result):
        assert line.x == i

    assert i == 999


def test_many_weighted_hosts(ch_many_weighted_hosts, query):
    """
    :param (ClickHouse) ch_many_weighted_hosts:
    :param (Query) query:
    """
    result = ch_many_weighted_hosts.execute(query)
    assert result.data[0].h == 'mtch01m.metrika.yandex.net'

    result = ch_many_weighted_hosts.execute(query)
    assert result.data[0].h == 'mtch01m.metrika.yandex.net'

    with requests_mock.Mocker() as m:
        m.get('http://mtch01m.metrika.yandex.net:8123', status_code=503)
        m.get('http://mtch01k.metrika.yandex.net:8123', real_http=True)

        result = ch_many_weighted_hosts.execute(query)

    assert result.data[0].h == 'mtch01k.metrika.yandex.net'

    result = ch_many_weighted_hosts.execute(query)
    assert result.data[0].h == 'mtch01k.metrika.yandex.net'

    result = ch_many_weighted_hosts.execute(query)
    assert result.data[0].h == 'mtch01k.metrika.yandex.net'
