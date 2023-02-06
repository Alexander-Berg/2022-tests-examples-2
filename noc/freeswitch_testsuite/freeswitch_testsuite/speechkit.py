import grpc
import yandex.cloud.ai.stt.v2.stt_service_pb2 as stt
import yandex.cloud.ai.stt.v2.stt_service_pb2_grpc as stt_grpc
from yandex.cloud.ai.tts.v3.tts_service_pb2 import \
    yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2 as tts
import yandex.cloud.ai.tts.v3.tts_service_pb2_grpc as tts_grpc

from aiohttp.web_request import Request
from aiohttp.web import (
    Application,
    StreamResponse,
    post,
)
from asyncio import (
    AbstractEventLoop, AbstractServer,
    Future, Task, create_task, get_event_loop)
from freeswitch_testsuite.environment_config import (
    GRPC_STT_PORT, GRPC_TTS_PORT,
    WEB_BIND_ADDRESS, HTTP_TTS_PORT, SYNTH_PATH)
from freeswitch_testsuite.logs import log_debug, log_error
from re import Pattern, compile
from socket import socket, AF_INET, SO_REUSEADDR, SOL_SOCKET

GRPC_PARTIAL_THRESH: int = 5
GRPC_FINAL_THRESH: int = 10

class MockSk:
    def __init__(self, loop: AbstractEventLoop):
        self.stt = MockSTT()
        self.tts = MockTTS()
        self.http_tts = MockHttpTTS(loop)

    def reset(self):
        self.stt.reset()

    async def start(self):
        await self.http_tts.start()
        self.stt.start()
        self.tts.start()
        return self

    async def stop(self):
        await self.http_tts.stop()


class MockHttpTTS:
    def __init__(self, loop: AbstractEventLoop):
        self.loop: AbstractEventLoop = loop
        self.app: Application = Application()
        self.app.add_routes([
            post(SYNTH_PATH, self.handle_synth),
        ])
        self._app_handler = self.app.make_handler()
        self._socket = socket(AF_INET)
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._socket.bind((WEB_BIND_ADDRESS, HTTP_TTS_PORT))
        self._server: AbstractServer = None

    async def start(self):
        log_debug(
            f'MockTTS server starting on {WEB_BIND_ADDRESS}:{HTTP_TTS_PORT}')
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
        log_debug(f'MockTTS server finished')

    async def handle_synth(self, request: Request) -> StreamResponse:
        req = await request.post()
        text = req['text']
        response: StreamResponse = StreamResponse(
            status=200,
            reason='OK',
            headers={'Content-Type': 'audio/l16'},
        )
        response.enable_chunked_encoding()
        await response.prepare(request)

        for count in range(0, 100):
            await response.write(bytes(text, 'utf-8'))
            log_debug(f'TTS: HTTP-> <{text}>')

        await response.write_eof()
        return response


class MockSTT(stt_grpc.SttServiceServicer):
    def __init__(self):
        super(MockSTT, self).__init__()
        self.phrase: str = ''
        self.msg_recv: int = 0
        self.partial_results: bool = False
        self.initial_received: Future = Future()
        self.listen_addr: str = f'{WEB_BIND_ADDRESS}:{GRPC_STT_PORT}'
        self.server: grpc.aio.Server = grpc.aio.server()
        self.server_task: Task = None

    def start(self):
        try:
            self.server.add_secure_port(
                self.listen_addr, make_credentials())
        except Exception as err:
            log_error(f'Cannot start STT GRPC server: {err}')
            raise
        self.server_task = create_task(self.serve())

    def reset(self):
        self.initial_received = Future()
        self.phrase = ''
        self.msg_recv = 0

    async def StreamingRecognize(
            self, request: stt.StreamingRecognitionRequest,
            context: grpc.aio.ServicerContext) -> \
            stt.StreamingRecognitionResponse:
        log_debug('STT GRPC connection opened')
        exp: Pattern = compile("<([^>]*)>")
        while True:
            msg: stt.StreamingRecognitionRequest = await context.read()
            if msg is grpc.aio.EOF:
                break
            self.msg_recv += 1
            if msg.audio_content != b'':
                try:
                    phrase = exp.search(
                        msg.audio_content.decode('utf-8')).group(1)
                except (UnicodeError, TypeError):
                    continue
                if phrase:
                    self.phrase = phrase
                    if self.partial_results and \
                        (self.msg_recv == GRPC_PARTIAL_THRESH):
                        await context.write(
                            self.make_response(self.phrase))
                        log_debug('STT sent partial response')
                    if self.msg_recv >= GRPC_FINAL_THRESH:
                        await context.write(
                            self.make_response(self.phrase, True, True))
                        log_debug(f'STT recognized: {phrase}')
                        log_debug('STT sent final response')
            elif msg.config:
                self.initial_received.set_result(True)
                self.partial_results = msg.config.specification.partial_results
                log_debug(msg.config)
        log_debug('STT GRPC connection closed')

    async def serve(self) -> None:
        log_debug(f'MockSTT server starting on {self.listen_addr}')
        stt_grpc.add_SttServiceServicer_to_server(self, self.server)
        await self.server.start()
        await self.server.wait_for_termination()
        log_debug(f'MockSTT GRPC server finished')

    @staticmethod
    def make_response(text, is_eou=False, is_final=False) -> \
            stt.StreamingRecognitionResponse:
        resp: stt.StreamingRecognitionResponse = \
            stt.StreamingRecognitionResponse()
        chunk: stt.SpeechRecognitionChunk = stt.SpeechRecognitionChunk()
        chunk.end_of_utterance = is_eou
        chunk.final = is_final
        alt: stt.SpeechRecognitionAlternative = \
            stt.SpeechRecognitionAlternative()
        alt.text = text
        alt.confidence = 100
        chunk.alternatives.append(alt)
        resp.chunks.append(chunk)
        return resp


class MockTTS(tts_grpc.Synthesizer):
    def __init__(self):
        super(MockTTS, self).__init__()
        self.listen_addr: str = f'{WEB_BIND_ADDRESS}:{GRPC_TTS_PORT}'
        self.server: grpc.aio.Server = grpc.aio.server()
        self.server_task: Task = None

    def start(self):
        try:
            self.server.add_secure_port(
                self.listen_addr, make_credentials())
        except Exception as err:
            log_error(f'Cannot start TTS GRPC server: {err}')
            raise
        self.server_task = create_task(self.serve())

    async def serve(self) -> None:
        log_debug(f'MockTTS server starting on {self.listen_addr}')
        tts_grpc.add_SynthesizerServicer_to_server(self, self.server)
        await self.server.start()
        await self.server.wait_for_termination()
        log_debug(f'MockTTS GRPC server finished')

    async def UtteranceSynthesis(
            self,
            request: tts.UtteranceSynthesisRequest,
            context: grpc.aio.ServicerContext,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None) -> tts.UtteranceSynthesisResponse:
        log_debug(f'MockTTS received:\n{request}')
        text: str = request.text
        for a in range(0, 50):
            await context.write(MockTTS.make_response(text))
        await context.write(tts.UtteranceSynthesisResponse())

    @staticmethod
    def make_response(text) -> tts.UtteranceSynthesisResponse:
        resp: tts.UtteranceSynthesisResponse = \
            tts.UtteranceSynthesisResponse()
        resp.audio_chunk.data = bytes(f'{text}', 'utf-8') * 5
        log_debug(f'TTS: gRPC-> {resp.audio_chunk.data}')
        return resp


def make_credentials() -> grpc.ServerCredentials:
    with open('cert/server.key', 'rb') as f:
        key: bytes = f.read()
    with open('cert/server.crt', 'rb') as f:
        chain: bytes = f.read()
    return grpc.ssl_server_credentials(((key, chain,),))


def main():
    loop: AbstractEventLoop = get_event_loop()
    server = MockSk(loop)
    loop.run_until_complete(server.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(server.stop())
    loop.close()


if __name__ == '__main__':
    main()
