# -*- coding: utf-8 -*-

from datetime import datetime
import httplib

from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.network import wait_port_is_free
from sandbox.projects.common.search.components import get_thumb_daemon
from sandbox.projects.common.search.components import DefaultThumbDaemonParameters
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.projects.common.thumbdaemon import utils


DATE_NAME = 'Date'


class RFC1123:
    str_format = "%a, %d %b %Y %H:%M:%S %Z"

    @staticmethod
    def str2datetime(value):
        return datetime.strptime(value, RFC1123.str_format)

    @staticmethod
    def datetime2str(value):
        # Time zone is not set by default
        return value.strftime(RFC1123.str_format) + 'GMT'


def test_http_request_one_method(port, method, http_path, expected_code, expected_data=None, headers={}):
    try:
        connection = httplib.HTTPConnection('localhost', port)
        connection.request(method, http_path, headers=headers)
        response = connection.getresponse()
    except (IOError, httplib.HTTPException) as e:
        raise SandboxTaskFailureError("Request '%s', failed to retrieve response from server: %s" % (http_path,
                                                                                                     e))

    if expected_code != response.status:
        raise SandboxTaskFailureError("Request '%s', method %s, expected code %d, got %d" % (http_path,
                                                                                             method,
                                                                                             expected_code,
                                                                                             response.status))
    data = response.read()
    if expected_data is not None:
        if data != expected_data:
            raise SandboxTaskFailureError("Request '%s', expected data\n'%s'\ngot\n'%s'\n" %
                                          (http_path, expected_data, data))

    return data, dict([(x[0].lower(), x[1]) for x in response.getheaders()])


def test_http_request(port, http_path, expected_code, expected_data=None, headers={}):
    _, head_headers = test_http_request_one_method(port, 'HEAD', http_path, expected_code, '', headers)
    data, get_headers = test_http_request_one_method(port, 'GET', http_path, expected_code, expected_data, headers)
    head_date = head_headers[DATE_NAME.lower()]
    get_date = get_headers[DATE_NAME.lower()]
    if not dates_are_near(RFC1123.str2datetime(head_date), RFC1123.str2datetime(get_date)):
        raise SandboxTaskFailureError("HEAD and GET dates %s, %s are not near" % (head_date, get_date))
    # To make comparing headers easier
    get_headers[DATE_NAME.lower()] = head_headers[DATE_NAME.lower()]
    if head_headers != get_headers:
        raise SandboxTaskFailureError("Request %s, headers for HEAD and GET are different:\n%s\n%s\n" %
                                      (http_path, head_headers, get_headers))

    return data, get_headers


def dates_are_near(date1, date2):
    return abs((date1 - date2).total_seconds()) < 5


class TestThumbDaemonFunc(SandboxTask):
    """
        Функциональные тесты картиночного конфига (бинарник+конфиг) с продакшн-базой.
    """
    type = 'TEST_THUMB_DAEMON_FUNC'

    input_parameters = DefaultThumbDaemonParameters.params

    def on_execute(self):
        thumb_id = next(utils.get_thumb_ids(self.ctx[DefaultThumbDaemonParameters.Database.name]))

        shard_type, shard_num, shard_timestamp = utils.get_database_version(
            self.ctx[DefaultThumbDaemonParameters.Database.name])

        thumb_daemon = get_thumb_daemon()
        thumb_daemon.start()
        thumb_daemon.wait()

        test_http_request(thumb_daemon.port, '/version', httplib.OK, shard_timestamp)
        test_http_request(thumb_daemon.port, '/shardname', httplib.OK, "-".join((shard_type, shard_num, shard_timestamp)))
        test_http_request(thumb_daemon.port, '/i?id=crazyid', httplib.NOT_FOUND)
        test_http_request(thumb_daemon.port, '/crazypath', httplib.NOT_FOUND)
        test_http_request(thumb_daemon.port, '/robots.txt', httplib.OK, "User-Agent: *\nDisallow: /\n")

        test_http_request(thumb_daemon.port, '/i?id=%s&n=crazy' % thumb_id, httplib.OK)

        content_type_name = 'Content-Type'
        content_length_name = 'Content-Length'
        timing_allow_origin_name = 'Timing-Allow-Origin'
        thumb_path = '/i?id=%s' % thumb_id
        body, headers = test_http_request(thumb_daemon.port, thumb_path, httplib.OK)

        def check_header(name, expected_value):
            value = headers.get(name.lower(), None)
            if value != expected_value:
                raise SandboxTaskFailureError("Header %s: expected %s, got %s" % (name, expected_value, value))

        check_header(content_type_name, 'image/jpeg')
        check_header(content_length_name, str(len(body)))
        check_header(timing_allow_origin_name, '*')
        date_value = headers.get(DATE_NAME.lower(), None)
        if not dates_are_near(RFC1123.str2datetime(date_value), datetime.utcnow()):
            raise SandboxTaskFailureError("Date value %s different from now %s" % date_value)

        # test 304 support
        etag_name = 'ETag'
        if_none_match_name = 'If-None-Match'
        etag_value = headers.get(etag_name.lower(), None)
        if etag_value is None:
            raise SandboxTaskFailureError("Did not get %s header" % etag_name)
        # When an invalid etag comes in If-None-Match, ignore it and serve full response
        test_http_request(thumb_daemon.port, thumb_path, httplib.OK, body, headers={
            if_none_match_name: etag_value[:-2] + 'x"',
        })
        _, headers304 = test_http_request(thumb_daemon.port, thumb_path, httplib.NOT_MODIFIED, '', headers={
            if_none_match_name: etag_value,
        })
        for name in [content_type_name]:
            if name.lower() in headers304:
                raise SandboxTaskFailureError('Unexpected header %s in Not Modified response' % name)

        # shutdown it manually, no .stop() required
        test_http_request_one_method(thumb_daemon.port, 'GET', '/admin?action=shutdown', httplib.OK)

        shutdown_timeout = 3
        if not wait_port_is_free(port=thumb_daemon.port, timeout=shutdown_timeout):
            raise SandboxTaskFailureError("Could not shut down thumbdaemon in %d seconds" % shutdown_timeout)


__Task__ = TestThumbDaemonFunc
