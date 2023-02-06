# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import contextlib
import os
import random
import signal
import sys
import time
from unittest import TestCase

from flask import Flask
import gevent
from passport.backend.social.common.gunicorn import Application


MIN_DYN_PORT = 49152
MAX_DYN_PORT = 65535
STDERR = 2
app = Flask(__name__)


class TestGunicornWorker(TestCase):
    TIMEOUT = 5

    def test_monkeys_patch_workers(self):
        port = random.randrange(MIN_DYN_PORT, MAX_DYN_PORT + 1)
        app = Application(
            dict(
                app_uri='tests.test_gunicorn:app',
                bind='127.0.0.1:%d' % port,
                worker_class='passport.backend.social.common.gunicorn.GeventWorker',
                workers=2,
            ),
        )
        monkeys_job_count = 0
        with self.start_gunicorn_app(app) as app_stderr:
            reader = FileReader(app_stderr)
            started_at = time.time()
            while time.time() - started_at <= self.TIMEOUT:
                line = reader.readline(timeout=0.05)
                if line is not None:
                    sys.stdout.write(line)
                    if b'Monkeys are patching environment' in line:
                        monkeys_job_count += 1
                    if monkeys_job_count >= 2:
                        # Если немного не подождать, gunicorn будет долго выключаться
                        time.sleep(1)
                        break
        self.assertEqual(monkeys_job_count, 2)

    @contextlib.contextmanager
    def start_gunicorn_app(self, app):
        pipe, child_pipe = os.pipe()

        child_pid = os.fork()
        if child_pid != 0:
            try:
                os.close(child_pipe)
                yield pipe
            finally:
                os.kill(child_pid, signal.SIGINT)
                os.waitpid(child_pid, 0)
            return

        status = 1
        try:
            os.close(pipe)
            os.dup2(child_pipe, STDERR)
            app.run()
        except SystemExit as e:
            status = e.code
        finally:
            os._exit(status)


class FileReader(object):
    READ_LENGTH = 10240

    def __init__(self, fd):
        gevent.os.make_nonblocking(fd)
        self.fd = fd
        self.buf = b''

    def readline(self, timeout):
        line, self.buf = self._split_first_line(self.buf)
        if line is not None:
            return line
        with gevent.Timeout(timeout, False):
            self.buf += gevent.os.nb_read(self.fd, self.READ_LENGTH)
        line, self.buf = self._split_first_line(self.buf)
        if line is not None:
            return line

    def _split_first_line(self, s):
        bits = self.buf.split(b'\n', 1)
        if len(bits) == 1:
            first, tail = None, bits[0]
        else:
            first, tail = bits
            first += '\n'
        return first, tail
