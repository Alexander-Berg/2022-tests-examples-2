#!/usr/bin/python3
import unittest

from io import StringIO
from unittest.mock import patch

import noc.admin.logstat.logstat as logstat


class TestDevice(unittest.TestCase):
    def setUp(self):
        patch('noc.admin.logstat.logstat.macros', {'2a02:6b8:b010:1:2:3:4:5': "TEST"}).start()

    def tearDown(self):
        patch.stopall()

    def test_parse_common_nginx(self):
        line = '2a02:6b8:b010:1:2:3:4:5 - - [23/Jan/2017:11:23:51 +0300] "GET /get/?q=yes HTTP/1.1" 304 0 "-"'
        expected = {
            'client_ip': '2a02:6b8:b010:1:2:3:4:5',
            'url': '/get/',
            'remote_user': '-',
            'remote_addr': '2a02:6b8:b010:1:2:3:4:5',
            'line': '2a02:6b8:b010:1:2:3:4:5 - - [23/Jan/2017:11:23:51 +0300] "GET /get/?q=yes HTTP/1.1" 304 0 "-"',
            'bytes': 0,
            'request': 'GET /get/?q=yes HTTP/1.1',
            'macro': 'TEST',
            'time_local': '23/Jan/2017:11:23:51 +0300',
            'code': 304,
            'http_x_forwarded_for': '-',
            'orig_url': '/get/?q=yes',
            'status': '304',
            'body_bytes_sent': '0',
        }

        logstat.load_schemes()
        res = logstat.SCHEMES["LOG_FORMAT_COMMON"].parse(line)

        self.assertEqual(res, expected)

    def test_parse_hbf(self):
        line = (
            'tskv	tskv_format=hbf-access-log	timestamp=2022-07-18T09:34:55	timezone=+0300	'
            'status=304	protocol=HTTP/1.1	method=POST	request=/get/?output&debug	referer=-	'
            'cookies=-	user_agent=yandex-hbf-agent: 8602569	vhost=prestable.hbf.yandex.net	'
            'ip=2a02:6b8:c02:370:0:604:2d6c:f950	x_forwarded_for=-	x_real_ip=-	'
            'request_id=7e2a028bc77e0e970a7da5928d037986	args=output&debug	scheme=https	port=443	'
            'ssl_handshake_time=0.004	upstream_cache_status=-	upstream_addr=127.0.0.1:9081	'
            'upstream_status=304	http_y_service=-	tcpinfo_rtt=203	tcpinfo_rttvar=68	tcpinfo_snd_cwnd=10	'
            'tcpinfo_rcv_space=13900	range=-	bytes_received=38643	bytes_sent=169	content_length=38354	'
            'upstream_response_time=0.020	request_time=0.017	last_modified=Mon, 18 Jul 2022 06:02:10 GMT'
        )

        expected = {
            'tskv_format': 'hbf-access-log',
            'timestamp': '2022-07-18T09:34:55',
            'timezone': '+0300',
            'status': '304',
            'protocol': 'HTTP/1.1',
            'method': 'POST',
            'request': '/get/?output&debug',
            'referer': '-',
            'cookies': '-',
            'user_agent': 'yandex-hbf-agent: 8602569',
            'vhost': 'prestable.hbf.yandex.net',
            'ip': '2a02:6b8:c02:370:0:604:2d6c:f950',
            'x_forwarded_for': '-',
            'x_real_ip': '-',
            'request_id': '7e2a028bc77e0e970a7da5928d037986',
            'args': 'output&debug',
            'scheme': 'https',
            'port': '443',
            'ssl_handshake_time': '0.004',
            'upstream_cache_status': '-',
            'upstream_addr': '127.0.0.1:9081',
            'upstream_status': '304',
            'http_y_service': '-',
            'tcpinfo_rtt': '203',
            'tcpinfo_rttvar': '68',
            'tcpinfo_snd_cwnd': '10',
            'tcpinfo_rcv_space': '13900',
            'range': '-',
            'bytes_received': '38643',
            'bytes_sent': '169',
            'content_length': '38354',
            'upstream_response_time': '0.020',
            'request_time': '0.017',
            'last_modified': 'Mon, 18 Jul 2022 06:02:10 GMT',
            'remote_addr': '2a02:6b8:c02:370:0:604:2d6c:f950',
            'body_bytes_sent': '169',
            'host': 'prestable.hbf.yandex.net',
            'http_x_forwarded_for': '-',
            'client_ip': '2a02:6b8:c02:370:0:604:2d6c:f950',
            'orig_url': '/get/?output&debug',
            'virtualhost': 'prestable.hbf.yandex.net',
            'code': 304,
            'url': '/get',
            'bytes': 169,
            'macro': '',
            'time': 17,
        }
        logstat.load_schemes()
        res = logstat.SCHEMES["LOG_FORMAT_HBF"].parse(line)

        res.pop('line')
        self.assertEqual(res, expected)

    def test_nginx_rt(self):
        line = '2a02:6b8:b010:1:2:3:4:5 - - [23/Jan/2017:16:51:01 +0300] racktables "GET /test/ HTTP/1.1" 401 363 0.016 "-" "Mozilla" "-"'
        expected = {
            'macro': 'TEST',
            'url': '/test/',
            'http_x_forwarded_for': '-',
            'remote_addr': '2a02:6b8:b010:1:2:3:4:5',
            'time_local': '23/Jan/2017:16:51:01 +0300',
            'time': 16,
            'code': 401,
            'request_time': '0.016',
            'line': '2a02:6b8:b010:1:2:3:4:5 - - [23/Jan/2017:16:51:01 +0300] racktables "GET /test/ HTTP/1.1" 401 363 0.016 "-" "Mozilla" "-"',
            'http_referer': '-',
            'orig_url': '/test/',
            'client_ip': '2a02:6b8:b010:1:2:3:4:5',
            'request': 'GET /test/ HTTP/1.1',
            'remote_user': '-',
            'http_user_agent': 'Mozilla',
            'host': 'racktables',
            'virtualhost': 'racktables',
            'bytes': 363,
            'status': '401',
            'body_bytes_sent': '363',
        }

        logstat.load_schemes()
        res = logstat.SCHEMES["LOG_FORMAT_RT"].parse(line)
        self.assertEqual(res, expected)

    def test_nginx_rt_ip_from_forward(self):
        line = (
            '2a02:6b8:0:3400::117 - - [15/Jan/2017:00:00:03 +0300] racktables '
            '"GET /export/slb-info.php HTTP/1.0" 429 0 0.000 "-" "Wget" "2a02:6b8:b010:1:2:3:4:5"'
        )
        logstat.load_schemes()
        res = logstat.SCHEMES["LOG_FORMAT_RT"].parse(line)
        self.assertEqual(res["client_ip"], "2a02:6b8:b010:1:2:3:4:5")

    @patch('sys.stdout', new_callable=StringIO)
    def test_exclude_ping(self, mock_stdout):
        lines = (
            'tskv	tskv_format=hbf-access-log	timestamp=2022-07-18T09:34:55	timezone=+0300	status=304	protocol=HTTP/1.1	'
            'method=POST	request=/get/?output&debug	referer=-	cookies=-	user_agent=yandex-hbf-agent: 8602569	'
            'vhost=prestable.hbf.yandex.net	ip=2a02:6b8:c02:327:0:604:2d6e:28c0	x_forwarded_for=-	x_real_ip=-	'
            'request_id=27a0633fb2bb339454333fa135d21ff7	args=output&debug	scheme=https	port=443	ssl_handshake_time=0.003	'
            'upstream_cache_status=-	upstream_addr=127.0.0.1:9081	upstream_status=304	http_y_service=-	tcpinfo_rtt=215	'
            'tcpinfo_rttvar=67	tcpinfo_snd_cwnd=10	tcpinfo_rcv_space=13900	range=-	bytes_received=38642	bytes_sent=169	'
            'content_length=38353	upstream_response_time=0.012	request_time=0.012	last_modified=Mon, 18 Jul 2022 06:02:10 GMT\n'
            'tskv	tskv_format=hbf-access-log	timestamp=2022-07-18T10:02:12	timezone=+0300	status=200	protocol=HTTP/1.1	method=GET	'
            'request=/ping	referer=-	cookies=-	user_agent=curl/7.58.0	vhost=prestable.hbf.yandex.net	ip=::1	x_forwarded_for=-	'
            'x_real_ip=-	request_id=2649dc1b77adae4ff48a8cd55e00c4d8	args=-	scheme=http	port=80	ssl_handshake_time=-	upstream_cache_status=-	'
            'upstream_addr=127.0.0.1:9082	upstream_status=200	http_y_service=-	tcpinfo_rtt=24	tcpinfo_rttvar=10	'
            'tcpinfo_snd_cwnd=10	tcpinfo_rcv_space=43690	range=-	bytes_received=92	bytes_sent=263	content_length=-	'
            'upstream_response_time=0.060	request_time=0.060	last_modified=-\n'
        )

        logstat.load_schemes()
        logstat.loop(lines.splitlines(), logstat.SCHEMES["LOG_FORMAT_HBF"], logstat.JsonOutput())
        self.assertEqual(len(mock_stdout.getvalue().splitlines()), 1)
