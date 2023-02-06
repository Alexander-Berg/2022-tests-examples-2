#!/usr/bin/python3
import unittest
import logging
import asyncio
import ssl
import os

from comocutor.streamer import ConsoleStream, extract_telnet
from comocutor.exceptions import ConsoleException
from comocutor.test_utils import Server, Send, Expect, ExpectCloseConn, CloseConn, StartTls

TTY = "ttyS0"


class Telnet(unittest.TestCase):
    def test_extract_telnet(self):
        res = extract_telnet(b'\xff\xfb\x01\xff\xfb\x03\xff\xfd\x18\xff\xfd\x1f')
        expected = b'', [b'\xff\xfb\x01', b'\xff\xfb\x03', b'\xff\xfd\x18', b'\xff\xfd\x1f']
        self.assertEqual(expected, res)
        # Subnegotiation
        res = extract_telnet(b'\xff\xfd\x01\xff\xfa\x18\x01\xff\xf0')
        expected = b'', [b'\xff\xfd\x01', b'\xff\xfa\x18\x01\xff\xf0']
        self.assertEqual(expected, res)


open_tty_dialog = [
    Send(b"ok\r\n"),
    Expect(b"ssl\r\n"),
    Send(b"ok\r\n"),
    StartTls(protocol=ssl.PROTOCOL_SSLv23, verify_mode=ssl.CERT_NONE, check_hostname=False,
             ciphers="ALL:!LOW:!EXP:!MD5:@STRENGTH"),
    Expect(b"login anonymous\r\n"),
    Send(b"ok\r\n"),
    Expect(b"call %s\r\n" % TTY.encode()),
    Send(b"[attached]\r\n"),
    Expect(b"\x05c="),
    Send(b"[up]\r\n"),
    Expect(b"\x05c;"),
    Send(b"[connected]\r\n"),
]


class Console(unittest.TestCase):
    def setUp(self):
        logging.debug("setUp %s", self)
        self.server = Server()
        self.server.start_server()
        self.loop = asyncio.get_event_loop()

    def do_async(self, fn):
        try:
            res = self.loop.run_until_complete(fn)
        except Exception as e:
            if self.server.server_pipe and self.server.server_pipe.poll():
                ans = self.server.server_pipe.recv()
                logging.debug("Uncaught exception", exc_info=e)
                self.fail("server answer: %s" % ans)
            else:
                raise e
        return res

    def test_console_msg_searcher(self):
        msg = b"\r\n[forced to `spy' mode by user@127.0.0.1]\r\n"
        self.assertTrue(ConsoleStream.CONSOLE_ERROR.match(msg))

    def test_bump(self):
        dialog = open_tty_dialog + [
            Send(b"F\r\n  gs43t43\r\n[forced to `spy'"),
            Send(b" mode by user@127.0.0.1]\r\nvrgt43tg34"),
            ExpectCloseConn,
            CloseConn,
        ]

        async def test():
            ret = None
            streamer = ConsoleStream(self.server.host, TTY, self.server.port)
            await streamer.spawn()
            try:
                await streamer.read()
                await streamer.read()
            except Exception as e:
                ret = e
            streamer.close()
            return ret

        self.server.server_q.put(dialog)
        res = self.do_async(test())
        self.assertTrue(isinstance(res, ConsoleException))
        self.assertEqual(res.args, ("exit because received \"[forced to `spy' mode by user@127.0.0.1]\"",))


if os.getenv("COMOCUTOR_DEBUG"):
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level,
                    format="%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s")

if __name__ == '__main__':
    unittest.main()
