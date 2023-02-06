import unittest
import unittest.mock
import socket

from unittest.mock import call

import hbf.lib as lib
from hbf.lib import Statsd, GlobalStatsd, escape_curly_brace_format

call = call.__enter__()


class StatsdTest(unittest.TestCase):
    def setUp(self):
        self.statsd_sock = unittest.mock.MagicMock()

        GlobalStatsd.clear_instances()
        self.sock = unittest.mock.patch("socket.socket", return_value=self.statsd_sock).start()

    def tearDown(self):
        unittest.mock.patch.stopall()

    def test_statsd(self):
        Statsd().count("value", tag1="tagvalue")
        self.sock.assert_called_with(socket.AF_INET, socket.SOCK_DGRAM)
        kall = call.sendto(b'hbf.value:1|c|#tag1:tagvalue', ('127.0.0.1', 8125))
        self.statsd_sock.assert_has_calls([kall])

    def test_statsd_locked(self):
        with Statsd() as statsd:
            statsd.count("value1", tag1="tagvalue")
            statsd.count("value2", 1, tag1="tagvalue")
            statsd.count("value2", 2, tag1="tagvalue")
        self.sock.assert_called_with(socket.AF_INET, socket.SOCK_DGRAM)
        kall = call.sendto(b'hbf.value1:1|c|#tag1:tagvalue\n'
                           b'hbf.value2:3|c|#tag1:tagvalue',
                           ('127.0.0.1', 8125))
        self.statsd_sock.assert_has_calls([kall])

    def test_statsd_global_tags(self):
        with unittest.mock.patch("hbf.lib.Statsd.TAGS", {"service":"stable", "tag": "default"}):
            Statsd().count("value", tag="value")
            kall = call.sendto(b'hbf.value:1|c|#service:stable,tag:value',
                               ('127.0.0.1', 8125))
            self.statsd_sock.assert_has_calls([kall])

    def test_statsd_multitags(self):
        with unittest.mock.patch("hbf.lib.Statsd.TAGS", {"service":"stable"}):
            with Statsd() as statsd:
                statsd.count("value", tag3="value")
                statsd.count("value", tag3="value2")
                statsd.count("value", tag3="value", tag4="value2")

            kall = call.sendto(b'hbf.value:1|c|#service:stable,tag3:value\n'
                               b'hbf.value:1|c|#service:stable,tag3:value2\n'
                               b'hbf.value:1|c|#service:stable,tag3:value,tag4:value2',
                               ('127.0.0.1', 8125))
            self.statsd_sock.assert_has_calls([kall])

    def test_global_statsd_multitags(self):
        with unittest.mock.patch("hbf.lib.Statsd.TAGS", {"service":"stable"}):
            with GlobalStatsd():
                GlobalStatsd().count("value", tag3="value")
                GlobalStatsd().count("value", tag3="value2")
                GlobalStatsd().count("value", tag3="value", tag4="value2")
                GlobalStatsd().count("value", 10, tag3="value")

            kall = call.sendto(b'hbf.value:11|c|#service:stable,tag3:value\n'
                               b'hbf.value:1|c|#service:stable,tag3:value2\n'
                               b'hbf.value:1|c|#service:stable,tag3:value,tag4:value2',
                               ('127.0.0.1', 8125))
            self.statsd_sock.assert_has_calls([kall])

    def test_statsd_multitags(self):
        with unittest.mock.patch("hbf.lib.Statsd.TAGS", {"service":"stable"}):
            with Statsd():
                Statsd().count("value", 1)
                Statsd().count("value", 2)
                Statsd().count("value", 3)

            dest = ('127.0.0.1', 8125)
            self.statsd_sock.assert_has_calls([call.sendto(b'hbf.value:1|c|#service:stable', dest)])
            self.statsd_sock.assert_has_calls([call.sendto(b'hbf.value:2|c|#service:stable', dest)])
            self.statsd_sock.assert_has_calls([call.sendto(b'hbf.value:3|c|#service:stable', dest)])


class TestOther(unittest.TestCase):
    def test_escape_curly_brace_format(self):
        self.assertEqual(escape_curly_brace_format("{test}"), "{{test}}")
        self.assertEqual(escape_curly_brace_format("{{{{ _PRESENTATIONSHOWNETS_ }}"), "{{{{ _PRESENTATIONSHOWNETS_ }}")
