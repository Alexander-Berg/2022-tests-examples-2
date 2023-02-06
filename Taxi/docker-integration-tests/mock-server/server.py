#!/usr/bin/env python3
import asyncio
import logging
import os
import socket

from aiohttp import web
import uvloop

from mock_server import application

PORTS = [80, 8018, 8025, 8031, 8038, 17000]
ACCESS_LOG_FORMAT = (
    '%{Host}i %a %l %u %t "%r" %s %b "%{Referrer}i" "%{User-Agent}i'
)
LOG_FILE_TPL = '/taxi/logs/application-%s.log'


def init_loggers():
    program_name = os.getenv('program_name')
    logger = logging.getLogger()
    handler = logging.FileHandler(LOG_FILE_TPL % program_name)
    handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


def run():
    init_loggers()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    app = application.get_application()
    sockets = []
    for port in PORTS:
        sock = socket.socket(socket.AF_INET6)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind(('::', port))
        sockets.append(sock)
    web.run_app(app, sock=sockets, access_log_format=ACCESS_LOG_FORMAT)


if __name__ == '__main__':
    run()
