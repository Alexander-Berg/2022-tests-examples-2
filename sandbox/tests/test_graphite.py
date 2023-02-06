import socket
import pytest
import logging
import textwrap

import graphite


# Helpers

MANUAL_SEND_OK1 = 'bsgraphite-ok1:2024'
MANUAL_SEND_OK2 = 'bsgraphite-ok2:2024'
MANUAL_SEND_FAIL = 'bsgraphite-fail:2024'


class SocketMock(object):
    assert_hosts = set()
    assert_data = None

    @classmethod
    def expect_hosts(cls, hosts):
        cls.assert_hosts.update(hosts)

    def __init__(self, host_tuple, timeout):
        self.host = '{}:{}'.format(*host_tuple)
        assert self.host in self.assert_hosts
        self.assert_hosts.remove(self.host)

    def sendall(self, data):
        if self.assert_data is not None:
            assert data == self.assert_data
        if self.host == MANUAL_SEND_FAIL:
            logging.info('Raising socket error')
            raise socket.error('Test socket error')
        logging.info('Sending data %s for %s', data.replace('\n', '\\n'), self.host)

    def close(self):
        pass


def make_good_data():
    return [graphite.metric_point(graphite.one_min_metric('test'), 0, 100500)]


# Rules

def setup_module(module):
    socket.create_connection = SocketMock


def setup_function(function):
    SocketMock.assert_data = None
    SocketMock.assert_hosts.clear()


def teardown_function(function):
    assert len(SocketMock.assert_hosts) == 0


# Positive tests

def test_normalize_hostname():
    assert graphite.normalize_hostname('bs-test.yandex.net') == 'bs-test_yandex_net'


def test_metric_name():
    just_metric = graphite.one_min_metric('test')
    with_hostname = graphite.one_min_metric('test', hostname='another_test')

    append = just_metric('append')
    append_again = append('again')
    append_another = just_metric('append_another')
    append_multi = just_metric('append', 'multi')

    change_hostname = just_metric(hostname='host')
    explicit_no_hostname = just_metric(hostname=None)
    append_and_hostname = just_metric('append', hostname='host')

    flush_section = append_and_hostname('flush')
    append_with_hostname_after_without_hostname = flush_section('append', hostname='another_host')

    assert str(just_metric) == 'one_min.bs.test'
    assert str(with_hostname) == 'one_min.another_test.test'
    assert str(append) == 'one_min.bs.test.append'
    assert str(append_again) == 'one_min.bs.test.append.again'
    assert str(append_another) == 'one_min.bs.test.append_another'
    assert str(append_multi) == 'one_min.bs.test.append.multi'
    assert str(change_hostname) == 'one_min.host.test'
    assert str(explicit_no_hostname) == 'one_min.test'
    assert str(append_and_hostname) == 'one_min.host.test.append'
    assert str(flush_section) == 'one_min.host.test.append.flush'
    assert str(append_with_hostname_after_without_hostname) == 'one_min.another_host.test.append.flush.append'


def test_metric_point():
    metric = graphite.one_hour_metric('test')
    ethalon = '{} {} {}'.format(metric, 10.0, 123456)

    mp = graphite.metric_point
    assert mp(metric, 10, 123456.0) == ethalon
    assert mp(metric, 10.0, 123456) == ethalon
    assert mp(metric, '10.0', 123456) == ethalon
    assert mp(metric, 10, '123456.0') == ethalon
    assert mp(metric, timestamp=123456, value=10) == ethalon


def test_send():
    metrics = [
        'one_min.bs.test1 111 100500',
        '{} {} {}'.format(graphite.one_min_metric('test2'), 0, 123456),
        {'name': graphite.one_min_metric('test3'), 'value': 100, 'timestamp': 654321},
        (graphite.one_min_metric('test4'), 999, 0),
    ]
    SocketMock.assert_data = textwrap.dedent("""\
        one_min.bs.test1 111.0 100500
        one_min.bs.test2 0.0 123456
        one_min.bs.test3 100.0 654321
        one_min.bs.test4 999.0 0
    """)
    SocketMock.expect_hosts(graphite.YABS_SERVERS)
    graphite.Graphite().send(metrics)


def test_send_manual_servers():
    hosts = [MANUAL_SEND_OK1, MANUAL_SEND_OK2]
    SocketMock.expect_hosts(hosts)
    graphite.Graphite(hosts=hosts).send(make_good_data())


def test_send_socket_error():
    hosts = [MANUAL_SEND_FAIL]
    SocketMock.expect_hosts(hosts)
    graphite.Graphite(hosts=hosts).send(make_good_data())


# Negative tests

@pytest.mark.parametrize(('bad_value', 'exception_type'), [
    ('ERR', ValueError),
    (None, TypeError),
    (object, TypeError),
    (object(), TypeError),
    ((lambda: None), TypeError),
])
def test_metric_point_bad_value(bad_value, exception_type):
    for field in ('value', 'timestamp'):
        dct = {'name': '', 'value': 0, 'timestamp': 100500}
        dct[field] = bad_value
        with pytest.raises(exception_type):
            graphite.metric_point(**dct)


@pytest.mark.parametrize(('bad_object', 'exception_type'), [
    ('name 0', TypeError),                              # str, not enough parts
    (('name', 0), TypeError),                           # tuple, not enough parts
    ('name 0 100500 extra_data', TypeError),            # str, too many parts
    (('name', 0, 100500, 'extra_data'), TypeError),     # tuple, too many parts
    ({'value': 0, 'timestamp': 100500}, TypeError),     # dict, required field is absent
    ({'name': '', 'timestamp': 100500}, TypeError),     # dict, required field is absent
    ({'name': '', 'value': 0}, TypeError),              # dict, required field is absent
    (None, RuntimeError),                               # object of unexpected type
    (object, RuntimeError),                             # object of unexpected type
    (object(), RuntimeError),                           # object of unexpected type
    ((lambda: None), RuntimeError),                     # object of unexpected type
])
def test_send_bad_objects(bad_object, exception_type):
    with pytest.raises(exception_type):
        graphite.Graphite().send([bad_object])


def test_MetricName_restrictions():
    with pytest.raises(TypeError):
        class NoInheritance(graphite._MetricName):
            pass
    with pytest.raises(TypeError):
        graphite._MetricName('')  # direct instantiation
    with pytest.raises(ValueError):
        graphite.one_min_metric()  # empty metric
    with pytest.raises(ValueError):
        graphite.one_min_metric(hostname='test')  # empty metric despite the hostname
