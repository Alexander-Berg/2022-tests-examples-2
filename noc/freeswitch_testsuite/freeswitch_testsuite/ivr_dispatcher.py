from asyncio import Queue, AbstractEventLoop, AbstractServer, get_event_loop
from aiohttp.web_request import Request, StreamResponse
from aiohttp.web import (
    Application,
    Response,
    get,
    post,
    json_response
)
from aiohttp import ClientSession
from freeswitch_testsuite.environment_config import (
    WEB_BIND_ADDRESS, WEB_PORT, METRICS_PATH, ACTION_PATH, PROMPTS_PATH,
    MOD_IVRD_PORT
)
from freeswitch_testsuite.logs import log_debug, log_error
from socket import socket, AF_INET, SO_REUSEADDR, SOL_SOCKET
from termcolor import colored
from typing import Dict

__all__ = [
    'MockDispatcher',
]


class MockDispatcher:
    def __init__(self, loop: AbstractEventLoop):
        self.loop: AbstractEventLoop = loop
        self.testsuite: Queue = Queue(loop=loop)
        self.mailbox: Queue = Queue(loop=loop)
        self.app: Application = Application()
        self.app.add_routes([
            post(METRICS_PATH, self.handle_metrics),
            post(ACTION_PATH, self.handle_action),
            get(f'{PROMPTS_PATH}/{{fname}}', self.handle_prompts),
        ])
        self._app_handler = self.app.make_handler()
        self._socket = socket(AF_INET)
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._socket.bind((WEB_BIND_ADDRESS, WEB_PORT))
        self._server: AbstractServer = None
        self.session_id: str = None

    async def start(self):
        self._server = await self.loop.create_server(
            self._app_handler,
            sock=self._socket
        )
        return self

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        if self._socket:
            self._socket.close()

    async def reset(self):
        self.session_id = None
        for q in [self.testsuite, self.mailbox]:
            while not q.empty():
                await q.get()

    async def handle_metrics(self, request: Request) -> Response:
        return Response(status=200, reason='OK')

    async def handle_action(self, request: Request):
        req: Dict = await request.json()
        log_debug(f'REQ: {req}')
        self.session_id = req['session_id']
        self.to_testsuite(req)
        data = await self.mailbox.get()
        log_debug(f'RESP: {data}')
        if 'status' in data:
            return json_response(data=None, status=data['status'])
        return json_response(data=data, status=200, reason='OK')

    async def handle_prompts(self, request: Request):
        url = f'{request.scheme}://{request.host}{request.path}'
        response: StreamResponse = StreamResponse(
            status=200,
            reason='OK',
            headers={'Content-Type': 'audio/l16'},
        )
        response.enable_chunked_encoding()
        await response.prepare(request)

        for count in range(0, 1000):
            await response.write(bytes(url, 'utf-8'))
            log_debug(f'TTS: RTP-> <{url}>')

        await response.write_eof()
        return response

    def to_testsuite(self, msg: Dict[str, str]) -> None:
        self.testsuite.put_nowait(msg)
        # Dirty, but effective way to poke loop from another thread
        # instead of loop.run_coroutine_threadsafe()
        self.testsuite._loop._write_to_self()

    def respond(self, msg: Dict) -> None:
        self.mailbox.put_nowait(msg)
        # Dirty, but effective way to poke loop from another thread
        # instead of loop.run_coroutine_threadsafe()
        self.mailbox._loop._write_to_self()

    async def assert_module_request(self, action: Dict,
                                    session_id: str = None,
                                    action_id: str = None,
                                    checkpoints: bool = False):
        module_request = await self.testsuite.get()
        assert 'session_id' in module_request
        if session_id:
            assert module_request['session_id'] == session_id
        if action_id:
            assert module_request['action_id'] == action_id
        assert 'action_result' in module_request
        req_action = module_request['action_result']
        try:
            assert 'type' in req_action
            if req_action['type'] == 'playback':
                if checkpoints:
                    assert 'tts_checkpoints' in req_action
                assert action.items() <= req_action.items()
            elif req_action['type'] == 'ask':
                if checkpoints:
                    assert 'asr_checkpoints' in req_action
                assert action.items() <= req_action.items()
            else:
                assert req_action == action
        except AssertionError:
            log_error(
                f'{colored(f"{action} != {req_action}", "red")}')
            raise

    async def print_module_request(self):
        from json import dumps
        module_request = await self.testsuite.get()
        log_error(dumps(module_request, indent=4, ensure_ascii=False))

    async def send_interrupt(self):
        url: str = f'http://{WEB_BIND_ADDRESS}:{MOD_IVRD_PORT}/leg_command'
        headers: Dict = {'Content-Type': 'application/json'}
        data: Dict = {'session_id': self.session_id}
        async with ClientSession() as client:
            await client.post(url, headers=headers, json=data)


def main():
    loop: AbstractEventLoop = get_event_loop()
    server = MockDispatcher(loop)
    loop.run_until_complete(server.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(server.stop())
    loop.close()


if __name__ == '__main__':
    main()
