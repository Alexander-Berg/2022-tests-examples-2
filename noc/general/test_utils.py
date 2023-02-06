import os.path
import time

import asyncio
import logging
import queue
import socket
import ssl
import threading
import yatest
from typing import List, Union

from .streamer import Expr

_logger = logging.getLogger(__name__)


class Send:
    def __init__(self, data, sleep=0.0):
        self.data = data
        self.sleep = sleep

    def __repr__(self):
        return "Send(%r)" % self.data


class SendEcho(Send):
    pass


class StartTls:
    def __init__(self, protocol, options=None, verify_flags=None, verify_mode=None, check_hostname=None, ciphers=None):
        self.protocol = protocol
        self.options = options
        self.verify_flags = verify_flags
        self.verify_mode = verify_mode
        self.check_hostname = check_hostname
        self.ciphers = ciphers

    def make(self):
        context = ssl.SSLContext(self.protocol)
        test_data = yatest.common.source_path("noc/comocutor/tests")
        context.load_cert_chain(os.path.join(test_data, "cert.pem"), os.path.join(test_data, "key.pem"))
        for i in ["options", "verify_mode", "verify_flags", "check_hostname"]:
            if getattr(self, i) is not None:
                setattr(context, i, getattr(self, i))
        if self.ciphers:
            context.set_ciphers(self.ciphers)
        return context


class Expect:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return "Expect(%r)" % self.data


class CloseConn:
    pass


class ExpectCloseConn:
    pass


OK_MSG = "OK"
NO_MSG = "OK"


class Server:
    def __init__(self):
        self.port = None
        self.host = None
        self.server_pipe = None
        self.server_process = None
        self.sock = None

    def _socket_server(self, sock, server_up, server_q, client_q):
        _logger.debug("start server on %s", sock.getsockname())
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sock.bind((host, port))
        ans = OK_MSG
        socket.setdefaulttimeout(5)
        sock.listen(0)
        server_up.set()
        _logger.debug("wait for dialog")
        dialog = server_q.get()
        _logger.debug("wait for socket connection")
        conn, addr = sock.accept()
        for elem in dialog:
            _logger.debug("dialog: %s", elem)
            try:
                if isinstance(elem, Send):
                    if elem.sleep:
                        time.sleep(elem.sleep)
                    if isinstance(elem.data, str):
                        conn.send(elem.data.encode())
                    else:
                        conn.send(elem.data)
                elif isinstance(elem, Expect):
                    buf = b""
                    left_read = len(elem.data)
                    while True:
                        if len(buf) == len(elem.data):
                            break
                        result = conn.recv(max(left_read - 1, 1))
                        if len(result) == 0:
                            ans = "connection closed"
                            break
                        left_read -= len(result)
                        buf += result
                        if isinstance(elem.data, str):
                            result_comp = buf.decode()
                        else:
                            result_comp = buf
                        _logger.debug("expt:%r", elem.data)
                        _logger.debug("get:%r", result_comp)
                        if elem.data.startswith(result_comp):
                            continue

                        if result_comp != elem.data:
                            ans = Exception("Got answer: %r. Expected: %r" % (result_comp, elem.data))
                            break
                    if ans != OK_MSG:
                        _logger.debug("ans %s", ans)
                        break
                elif elem == ExpectCloseConn:
                    result = conn.recv(1024)
                    if len(result) > 0:
                        ans = "got data %s while expecting close" % result
                        break
                elif elem == CloseConn:
                    conn.close()
                elif isinstance(elem, StartTls):
                    ssl_context = elem.make()
                    _logger.debug("starttls with context %s", ssl_context)
                    ssl_sock = ssl_context.wrap_socket(conn, server_side=True)
                    conn = ssl_sock
                else:
                    ans = "unknown elem %s" % elem
                    # break
            except Exception as e:
                _logger.debug("exc %r", e)
                break
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except:
            pass

        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except socket.error:
                pass
        client_q.put(ans)
        _logger.debug("socket server is done")

    def start_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', 0))
        self.host, self.port = self.sock.getsockname()

        server_up = threading.Event()
        self.server_q = queue.Queue()
        self.client_q = queue.Queue()
        self.server_process = threading.Thread(target=self._socket_server,
                                               args=(self.sock, server_up, self.server_q, self.client_q))

        self.server_process.daemon = True
        self.server_process.start()
        counter = 0
        while not server_up.is_set():
            time.sleep(0.250)
            counter += 1
            if counter > (10 / 0.250):
                raise Exception("Could not start socket server")

    def force_close(self, msg):
        if self.server_q:
            self.server_q.put(msg)
        self.close()

    def close(self):
        # if self.server_process.is_alive():
        #     os.kill(self.server_process.pid, signal.SIGTERM)
        self.sock.close()
        self.server_process.join(timeout=1.0)


def _test_exprs(exprs: List[Expr], data: Union[str, bytes]) -> bool:
    for expr in exprs:
        if expr.check(data):
            return True
    return False


def do_async(fn, timeout=10):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(asyncio.wait_for(fn, timeout=timeout))
    return res
