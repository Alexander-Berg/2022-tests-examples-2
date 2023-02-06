#!/usr/bin/env python

import logging

import robot.library.yuppie as yp

import unittest


class TestYtCl(unittest.TestCase):
    def test_yt_cl(self):
        yt = yp.Yt.up()
        o = yp.YtClPipe(["find", "//sys"]) | yp.CmdPipe(["cut", "-f", "3", "-d", "/"]) | yp.PipeEnd()
        logging.info("Got %s", o.stdout())

        (   # noqa
            yp.CmdPipe(["echo", "key\tvalue"]) |
            yp.YtClPipe(["write", "//home/test", "--format", "yamr"]) |
            yp.PipeEnd()
        )
        o = yp.YtCl(["read", "//home/test", "--format", "yamr"])

        logging.info("Got %s", o.stdout())
        self.assertEqual(o.stdout(), "key\tvalue\n")
        yt.down()


if __name__ == '__main__':
    unittest.main()
