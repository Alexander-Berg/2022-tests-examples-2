import logging
from pathlib import Path
from pprint import pprint
import pytest
import shutil
import subprocess
import tempfile

from aiohttp import web
import asyncio
import json
import yaml


@pytest.fixture
async def mockserver(aiohttp_server):
    class Request:
        def __init__(self, handlers=dict(), body=None):
            self.handlers = handlers
            self.body = body

    class Response:
        def __init__(self, body=None, code=200):
            self.body = body
            self.code = code

    class Handler:
        def __init__(self):
            self.queue = asyncio.Queue()
            self.config_ts = 12345678
            self.failed_events_left = 10
            pass

        async def handle_post_event(self, request):
            try:
                content_type_value = request.headers.get('Content-Type', None)

                if not content_type_value:
                    exc = Exception(
                        f'in {request.path} handler: missing Content-Type header',
                    )
                    self.queue.put_nowait(exc)
                    raise exc

                if content_type_value.lower() != 'application/json':
                    exc = Exception(
                        f'in {request.path} handler: expected JSON content type',
                    )
                    self.queue.put_nowait(exc)
                    raise exc

                if not request.body_exists:
                    exc = Exception(f'in {request.path} handler: missing body')
                    self.queue.put_nowait(exc)
                    raise exc

                raw_content = await request.content.read()
                json_content = json.loads(raw_content)
                self.queue.put_nowait(Request(body=json_content))
                return web.Response(body='{}')
            except Exception as exc:
                print('ERROR: ' + str(exc))
                raise

        async def handle_get_config(self, request):
            try:
                config_ts = int(request.query['updated_ts'])
                if config_ts is None:
                    exc = Exception(
                        f'in {request.path} handler: missing updated_ts',
                    )
                    self.queue.put_nowait(exc)
                    raise exc
                if config_ts == self.config_ts:
                    response = json.loads('{}')
                    self.queue.put_nowait(Response(body=response, code=304))
                    return web.Response(body='{}', status=304)
                if config_ts > self.config_ts:
                    exc = Exception(
                        f'in {request.path} handler: config_ts too large',
                    )
                    self.queue.put_nowait(exc)
                    raise exc
                f = open('tests/data/config.json')
                response_json = json.load(f)
                self.queue.put_nowait(Response(body=response_json))
                response_str = json.dumps(response_json)
                return web.Response(body=response_str)
            except Exception as exc:
                print('ERROR: ' + str(exc))
                raise

        async def handle_post_event_buggy(self, request):
            try:
                content_type_value = request.headers.get('Content-Type', None)
                if self.failed_events_left > 0:
                    self.failed_events_left -= 1
                    self.queue.put_nowait(
                        Response(body=json.loads('{}'), code=500),
                    )
                    return web.Response(status=500, body='{}')

                if not content_type_value:
                    exc = Exception(
                        f'in {request.path} handler: missing Content-Type header',
                    )
                    self.queue.put_nowait(exc)
                    raise exc

                if content_type_value.lower() != 'application/json':
                    exc = Exception(
                        f'in {request.path} handler: expected JSON content type',
                    )
                    self.queue.put_nowait(exc)
                    raise exc

                if not request.body_exists:
                    exc = Exception(f'in {request.path} handler: missing body')
                    self.queue.put_nowait(exc)
                    raise exc

                raw_content = await request.content.read()
                json_content = json.loads(raw_content)
                self.queue.put_nowait(Request(body=json_content))
                return web.Response(body='{}')
            except Exception as exc:
                print('ERROR: ' + str(exc))
                raise

        async def wait_call(self, timeout=10.0):
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout)
                if isinstance(item, Exception):
                    raise item
                return item
            except asyncio.TimeoutError:
                logging.error(
                    'mockserver handler wait_call() timeout happened',
                )
                raise

        def has_calls(self):
            return not self.queue.empty()

        def calls_count(self):
            return self.queue.qsize()

    class MockServerImpl:
        def __init__(self):
            self.handler = Handler()
            self.app = web.Application()
            self.app.router.add_post(
                '/cctv-processor-api/v1/events',
                self.handler.handle_post_event,
            )
            self.app.router.add_get(
                '/cctv-processor-api/v1/configs',
                self.handler.handle_get_config,
            )
            self.app.router.add_post(
                '/cctv-processor-api/v1/events-buggy',
                self.handler.handle_post_event_buggy,
            )

        async def StartUp(self):
            self.server = await aiohttp_server(self.app, port=8080)

        async def TearDown(self):
            await self.server.close()

        def get_handler(self):
            return self.handler

    server = MockServerImpl()
    await server.StartUp()
    yield server
    await server.TearDown()


engine_types = ['cpu', 'cuda']


@pytest.fixture(params=engine_types)
def engine(request):
    return Processor(request.param)


class Processor:
    def __init__(self, engine_type):
        if engine_type == 'cuda':
            if not shutil.which('nvidia-smi'):
                pytest.skip('nvidia driver not found')
        self.engine_type = engine_type

    def run(self, config_path: Path):
        with tempfile.TemporaryDirectory() as tmpdir:
            if self.engine_type == 'cuda':
                # set cuda runtime in config handler
                with open(config_path, 'r') as original_config:
                    config_yaml = yaml.safe_load(original_config.read())

                for handler in config_yaml['handlers']:
                    if handler['type'] == 'find_signature':
                        handler['runtime'] = 'CUDA'
                config_path = Path(tmpdir) / config_path.name

                with open(config_path, 'w') as new_config:
                    yaml.dump(config_yaml, new_config)

            test_process = subprocess.Popen(
                [
                    'build/processor/yandex-cctv-processor',
                    '-c',
                    str(config_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return test_process
