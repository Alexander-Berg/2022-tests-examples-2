#!/usr/bin/python3
import time

import asyncio
import logging
import re
import unittest
from functools import partialmethod
from typing import List

from comocutor.devices import drop_escape, eval_cr
from comocutor.exceptions import StreamException
from comocutor.streamer import Stream, Expr, PIPES, ExpectResult


class StreamBlock:
    pass


class ReadBlock(StreamBlock):
    def __init__(self, wait=float("inf")):
        self.wait = wait
        # self.left = self.wait_total
        # till проствавляем после
        self.till = None

    def __repr__(self):
        if self.till:
            return "%s(wait=%s) till %s" % (self.__class__.__name__, self.wait, self.till)
        else:
            return "%s(wait=%s)" % (self.__class__.__name__, self.wait)

    def get_remainder(self):
        if self.till is None:
            self.till = time.time() + self.wait
        remainder = self.till - time.time()
        if remainder > 0:
            return remainder
        else:
            return 0


class EndBlock(StreamBlock):
    pass


class FakeStreamer(Stream):
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
        self.written = []
        self.current_read_phase = None

    async def read(self):
        while True:
            if self.current_read_phase is None:
                if self.dialog:
                    elem = self.dialog.pop(0)
                else:
                    elem = None
                self.current_read_phase = elem
            else:
                elem = self.current_read_phase

            if elem is None:
                break

            logging.debug("elem=%r", elem)
            if isinstance(elem, ReadBlock):
                await asyncio.sleep(elem.get_remainder())
            self.current_read_phase = None
            if not isinstance(elem, ReadBlock):
                break
        if elem is None or elem is EndBlock:
            raise StreamException()

        out = elem.encode()
        return {PIPES.STDOUT: out, PIPES.STDERR: b""}

    async def write(self, text):
        self.written += text


class TestDevice(unittest.TestCase):
    def setUp(self):
        logging.debug("setup")
        self.maxDiff = None
        self.loop = asyncio.get_event_loop()
        self.read_timeout = 0.1
        self.old_stream_expect = Stream.expect
        Stream.expect = partialmethod(Stream.expect, read_timeout=self.read_timeout * 5)

    def tearDown(self):
        Stream.expect = self.old_stream_expect

    def do_async(self, fn):
        res = self.loop.run_until_complete(fn)
        return res

    def do_async_read_exprs(self, streamer, exprs):
        async def fn():
            res = await streamer.expect(exprs)
            return res

        res = self.loop.run_until_complete(fn())
        return res

    def assert_expr_res(self, res: ExpectResult, expected: List):
        self.assertIsNotNone(res)
        self.assertEqual(res.pos, expected[0])
        self.assertEqual(res.match_group, expected[1], "match_group is not equals")
        self.assertEqual(res.before, expected[2])
        self.assertEqual(res.after, expected[3])
        self.assertEqual(res.match_content, expected[4])
        self.assertEqual(res.match_pipe, expected[5])

    def test_base_re(self):
        expr = [Expr("123")]
        res = Stream().check_expression(expr, b"123")
        self.assertIsNotNone(res)
        self.assert_expr_res(res, [0, {}, b"", b"", b"123", PIPES.STDOUT])

    def test_re_type(self):
        msg = b"test <host> olo"
        res = Stream().check_expression(Expr(r'<(?P<host>\w+)>'), msg)
        self.assert_expr_res(res, [0, {"host": b"host"}, b"test ", b" olo", b"<host>", PIPES.STDOUT])
        res = Stream().check_expression(Expr(r'.+<(?P<host>\w+)>', re_type="match"), msg)
        self.assert_expr_res(res, [0, {"host": b"host"}, b"", b" olo", b"test <host>", PIPES.STDOUT])
        res = Stream().check_expression(Expr(r'.+<(?P<host>\w+)>.+', re_type="fullmatch"), msg)
        self.assert_expr_res(res, [0, {"host": b"host"}, b"", b"", b"test <host> olo", PIPES.STDOUT])

    def test_stderr_re(self):
        stdout = b"some qwerty test message"
        stderr = b"some ololo test error"
        expr = [Expr("ololo", pipe=PIPES.STDERR)]
        res = Stream().check_expression(expr, {PIPES.STDOUT: stdout, PIPES.STDERR: stderr})
        self.assert_expr_res(res, [0, {}, b"some ", b" test error", b"ololo", PIPES.STDERR])

    def test_re1(self):
        expr = [Expr(r'(^|\n|\r\n)<(?P<hostname>\w+)>')]
        res = Stream().check_expression(expr, b"some text\r\n<test>")
        self.assert_expr_res(res, [0, {"hostname": b"test"}, b"some text", b"", b"\r\n<test>", PIPES.STDOUT])

    def test_re2(self):
        txt = b"""undo snmp-agent target-host trap address udp-domain 1.1.1.1 params securityname cipher %@%@t8p(B`T%+B&GCp$<g'{Sz!WY%@%@"""
        expr = [Expr(re.escape(txt) + b'(\n|\r\n)', re_type="match")]
        res = Stream().check_expression(expr, txt + b"\r\n<test>")
        self.assert_expr_res(res, [0, {}, b"", b"<test>", txt + b"\r\n", PIPES.STDOUT])

    def test_timeout_re(self):
        dialog = [ReadBlock(self.read_timeout * 2),
                  "Input the bits in the modulus [default = 2048]:",
                  ReadBlock(self.read_timeout * 100)]
        streamer = FakeStreamer(dialog)
        exprs = [Expr("non match"),
                 Expr(r"\[default = 2048\]:$")]
        res = self.do_async_read_exprs(streamer, exprs)
        self.assertIsNotNone(res)
        self.assert_expr_res(res, [1, {}, b"Input the bits in the modulus ", b"", b"[default = 2048]:", PIPES.STDOUT])

    def test_normal_timeout_re(self):
        # тут воспроизводится ситуация когда получаем сначало что-то подходяшее под timeout регулярку,
        # а потом под нормальную. В такой ситуации должна сработать только нормальная регулярка.
        dialog = [ReadBlock(self.read_timeout * 2),
                  "Input the bits in the modulus [default = 2048]:",
                  "\r\n<test>",
                  ReadBlock(self.read_timeout * 100)]
        streamer = FakeStreamer(dialog)
        exprs = [Expr(r"<\w+>"),
                 Expr(r" \[default = 2048\]:", re_type="fullmatch")]

        res = self.do_async_read_exprs(streamer, exprs)
        self.assertIsNotNone(res)
        self.assert_expr_res(res, [0, {}, b"Input the bits in the modulus [default = 2048]:\r\n", b"", b"<test>",
                                   PIPES.STDOUT])

    def test_streamer_partial(self):
        # Тут после первой проверки часть данных должны быть сохранена в буфер, а следующая проверка должна сделать
        # проверку буфера перед чтением новых данных
        dialog = [ReadBlock(self.read_timeout * 2),
                  "input:<test>",
                  ReadBlock(self.read_timeout * 100)]
        streamer = FakeStreamer(dialog)
        exprs = [Expr("input:", re_type="match"),
                 Expr("<test>", re_type="match"),
                 ]

        res = self.do_async_read_exprs(streamer, exprs)
        self.assert_expr_res(res, [0, {}, b"", b"<test>", b"input:", PIPES.STDOUT])
        res = self.do_async_read_exprs(streamer, exprs)
        self.assert_expr_res(res, [1, {}, b"", b"", b"<test>", PIPES.STDOUT])
        # self.assert_expr_res(res, [0, {}, b"Input the bits in the modulus [default = 2048]:\r\n", b"", b"<test>"])


class TestExpr(unittest.TestCase):
    def test(self):
        e = Expr(re.compile(r"^ +\^\n% Invalid input detected at '\^' marker\.$", re.M))
        self.assertTrue(e.check("           ^\n% Invalid input detected at '^' marker."))
        e = Expr("^Info: .+?(\n|$)", M=1)
        m = e.check("Info: No patch exists.\nThe state of the patch state file is: Idle\nThe current state is: Idle")
        self.assertEqual(m.group(0), "Info: No patch exists.\n")
        m = list(e.checkall("Info: 123.\nInfo: 456\nThe current state is: Idle"))
        self.assertEqual(m[0].group(0), "Info: 123.\n")
        self.assertEqual(m[1].group(0), "Info: 456\n")
        e = Expr("test", re_type="endswith")
        m = e.check("testtesttest")
        self.assertEqual(m.group(0), "test")


class TestDropEsc(unittest.TestCase):
    def test(self):
        e = b'params  \x1b[1Dsecurityname'
        self.assertEqual(drop_escape(e), b"params securityname")
        e = b'\n\x1b[11D                \x1b[16D40GE1/0/23:4'
        self.assertEqual(drop_escape(e), b"\n40GE1/0/23:4")
        e = b'no buffer\r\n\x1b[7m--More--\x1b[m'
        self.assertEqual(drop_escape(e), b"no buffer\r\n--More--")
        # \x1b[ - CSI
        e = b'\x1b[1;1H\x1b[2J\r\n****************************\r\n*    Slot 1'
        self.assertEqual(drop_escape(e), b"\r\n****************************\r\n*    Slot 1")
        e = b'1\r2'
        self.assertEqual(eval_cr(e), b"2")
        # e = b'134\r5'
        # self.assertEqual(eval_cr(e), b"534")
        e = b'123456\r      \rx'
        self.assertEqual(eval_cr(e), b"x")
        e = b'12\r      \r321 '
        self.assertEqual(eval_cr(e), b"321 ")
        e = b"enabled\r\ntrue"
        self.assertEqual(eval_cr(e), b"enabled\ntrue")

        e = b'\x1b[1A\x1b[2Kadministrator@dwdm-std-iva-1> uptime\n684 days,  7:02\n[ ne ]\nadministrator@dwdm-std-iva-1> '
        self.assertEqual(drop_escape(e), b'administrator@dwdm-std-iva-1> uptime\n684 days,  7:02\n[ ne ]\nadministrator@dwdm-std-iva-1> ')

logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s() - %(levelname)s - %(message)s")

if __name__ == '__main__':
    unittest.main()
