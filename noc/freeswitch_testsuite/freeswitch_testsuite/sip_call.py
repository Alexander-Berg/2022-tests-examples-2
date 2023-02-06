import pjsua2 as pj
from asyncio import AbstractEventLoop, Queue, Task, CancelledError
from freeswitch_testsuite.logs import log_debug, log_error
from freeswitch_testsuite.ua_status import *
from typing import Dict, Optional

__all__ = [
    'SipCall',
]


# An abstraction over PJSIP Call
# Listens for commands and executes  them.
# Passes PJSIP Call events from a particular
# call in pjlib to queues. Subscribers will be notified.
# Provides buffer with call media payload stored
# Provides various methods for call handling
class SipCall(pj.Call):
    def __init__(self,
                 ua_id: str,
                 loop: AbstractEventLoop,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ua_id: str = ua_id
        self.is_running: bool = True
        self.media_active: bool = False
        self.peer_media_idx = 0
        self.loop: AbstractEventLoop = loop
        self.state_events: Queue = Queue(loop=self.loop)
        self.media_events: Queue = Queue(loop=self.loop)
        self.command_inbox: Queue = Queue(loop=self.loop)
        self.audio_buffer: CBPort = None
        self.audio_player: Player = None
        self.inbox_listener: Task = self.loop.create_task(self.listen_inbox())

    def __del__(self):
        log_debug(f'{self.ua_id} deleted')

    def stop(self):
        self.inbox_listener.cancel()
        if self.audio_buffer:
            self.audio_buffer.reset(self)
            del self.audio_buffer
        if self.audio_player:
            del self.audio_player
        self.loop = None
        self.state_events = None
        self.media_events = None
        self.command_inbox = None
        self.inbox_listener = None

    async def reset(self):
        # Flush queues
        for q in [self.state_events, self.media_events, self.command_inbox]:
            while not q.empty():
                await q.get()
        self.do_hangup()

    # Wait for a command and execute it.
    async def listen_inbox(self) -> None:
        log_debug(f'{self.ua_id} Command Listener is running')
        try:
            while self.is_running:
                msg: Dict = await self.command_inbox.get()
                log_debug(f'GET: {msg}')
                command: str = msg['command']
                params: Dict = msg['parameters']
                if command == 'originate':
                    self.originate(**params)
                elif command == 'answer':
                    self.do_answer(**params)
                elif command == 'ringing':
                    self.do_ringing()
                elif command == 'hangup':
                    self.do_hangup(**params)
        except CancelledError:
            log_debug(f'{self.ua_id} Command Listener cancelled')
        log_debug(f'{self.ua_id} Command Listener is done')

    @staticmethod
    def set_headers(
            call_opts: pj.CallOpParam, headers: Dict[str, str] = None) -> None:
        for k, v in headers.items():
            header: pj.SipHeader = pj.SipHeader()
            header.hName = k
            header.hValue = v
            call_opts.txOption.headers.push_back(header)

    def originate(
            self,
            uri: str,
            headers: Optional[Dict[str, str]] = None) -> None:
        call_opts: pj.CallOpParam = pj.CallOpParam(True)
        if headers:
            self.set_headers(call_opts, headers=headers)
        self.makeCall(uri, call_opts)

    def do_hangup(self, cause: Optional[int] = None) -> None:
        call_opts: pj.CallOpParam = pj.CallOpParam(True)  # Defaults
        if cause:
            call_opts.statusCode = cause
        if self.isActive():
            self.hangup(call_opts)

    def do_answer(self, cause: Optional[int] = 200) -> None:
        call_opts: pj.CallOpParam = pj.CallOpParam(True)  # Defaults
        call_opts.statusCode = cause
        self.answer(call_opts)

    def do_ringing(self) -> None:
        call_opts: pj.CallOpParam = pj.CallOpParam(True)  # Defaults
        call_opts.statusCode = 180
        self.answer(call_opts)

    def send_dtmf(self, digits: str):
        if not self.media_active:
            raise "Media not active"
        self.dialDtmf(digits)

    def report_call_state(self, msg: Dict[str, str]) -> None:
        log_debug(f'{self.ua_id} CS: {msg}')
        self.state_events.put_nowait(msg)
        # Dirty, but effective way to poke loop from another thread
        # instead of loop.run_coroutine_threadsafe()
        self.state_events._loop._write_to_self()

    def report_media_state(self, msg: Dict[str, str]) -> None:
        self.media_events.put_nowait(msg)
        self.media_events._loop._write_to_self()

    def push_command(self, msg: Dict[str, str]) -> None:
        self.command_inbox.put_nowait(msg)
        self.command_inbox._loop._write_to_self()
        log_debug(f'PUT {self.ua_id} {msg}')

    # Send a command to inbox and asserts call state
    async def send_and_assert(self, command: Dict, state: int,
                              code: Optional[int] = 0):
        self.push_command(command)
        await self.assert_call_state(state, code=code)

    async def assert_call_state(self, state: int,
                                code: Optional[int] = 0):
        current_status = await self.state_events.get()
        try:
            assert current_status['state'] == state
        except AssertionError:
            log_error(f'Current state {current_status["state"]} != {state}')
            raise
        if code:
            try:
                assert current_status['status_code'] == code
            except AssertionError:
                log_error(
                    f'Current code {current_status["status_code"]} != {code}')
                raise

    async def assert_media_state(self, state: int):
        status = await self.media_events.get()
        try:
            assert status['state'] == state
        except AssertionError:
            log_error(
                f'Current media state {status["state"]} != {state}')
            raise

    # Assert audio payload corresponds given command
    # resets to zero audio buffer after that
    def assert_audio_and_reset(self, cmd: Dict):
        if self.audio_buffer:
            self.audio_buffer.assert_payload_and_reset(self, cmd)

    # Assert audio payload corresponds given command
    def assert_audio(self, cmd: Dict):
        if self.audio_buffer:
            self.audio_buffer.assert_payload(cmd)

    # Capture and store payload from a given conference bridge port
    def dump_audio(self):
        if not self.media_active:
            raise "Media not active"
        if not self.audio_buffer:
            self.audio_buffer = CBPort()
            self.audio_buffer.createPort(self.ua_id)
        self.audio_buffer.dump_payload(self)

    def play_audio(self):
        if not self.media_active:
            raise "Media not active"
        if not self.audio_player:
            self.audio_player = Player()
        self.audio_player.play(self)

    def speak(self, pattern: str):
        if not self.media_active:
            raise "Media not active"
        if not self.audio_buffer:
            self.audio_buffer = CBPort()
        self.audio_buffer.transmit_payload(self, pattern)

    def stop_speak(self):
        if self.audio_buffer:
            self.audio_buffer.transmit_stop(self)

    # Callbacks are called by underlying pjlib, so
    # handling must be as fast as possible: just
    # put an event to the queue
    def onCallState(self, prm: pj.OnCallStateParam) -> None:
        call_info: pj.CallInfo = self.getInfo()
        self.report_call_state(dict(
            status_code=call_info.lastStatusCode,
            state=call_info.state))
        if call_info.state == 6:
            self.media_active = False
            # Disconnect buffer from conference bridge
            if self.audio_buffer:
                self.audio_buffer.source = None

    def onCallMediaState(self, prm: pj.OnCallMediaStateParam) -> None:
        call_info: pj.CallInfo = self.getInfo()
        for mi in call_info.media:
            if mi.type == pj.PJMEDIA_TYPE_AUDIO:
                log_debug(f'CI: {call_info.stateText}, AUDIO: {mi.status}')
                if mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                    self.report_media_state(dict(state=MEDIA_STATE_ACTIVE))
                    self.media_active = True
                    self.peer_media_idx = mi.index
                    # Connect buffer to conference bridge
                    self.dump_audio()


# Callback media port. When connected to conference bridge,
# port calls onRx callback for each received audio frame.
# Received frames are collected in internal buffer
# Custom feature, available only in
class CBPort(pj.AudioMediaCBPort):
    def __init__(self):
        super(CBPort, self).__init__()
        self.source: int = None
        self.sink: int = None
        self.rx_buffer: bytearray = bytearray()
        self.tx_pattern: str = None

    def onRx(self, buf):
        try:
            chunk: bytes = bytes(buf, 'utf-8')
        except (UnicodeError, TypeError):
            return
        self.rx_buffer.extend(chunk)
        log_debug(f'CBPort: RTP<- {chunk}')

    def onTx(self) -> str:
        if self.tx_pattern:
            log_debug(f'CBPort: RTP-> {self.tx_pattern}')
            return self.tx_pattern

    def reset(self, call: SipCall):
        if self.source:
            call.getAudioMedia(self.source).stopTransmit(self)
            self.source = None
        if self.sink:
            self.stopTransmit(call.getAudioMedia(self.sink))
            self.sink = None
        self.rx_buffer.clear()
        self.tx_pattern = None
        log_debug('CBPort buffers cleared')

    def dump_payload(self, call: SipCall):
        if self.source:
            call.getAudioMedia(self.source).stopTransmit(self)
        self.source = call.peer_media_idx
        media: pj.AudioMedia = call.getAudioMedia(call.peer_media_idx)
        media.startTransmit(self)

    def transmit_payload(self, call: SipCall, payload: str):
        if self.sink is not None:
            self.stopTransmit(call.getAudioMedia(self.sink))
        self.sink = call.peer_media_idx
        media: pj.AudioMedia = call.getAudioMedia(call.peer_media_idx)
        self.tx_pattern = f'<{payload}>'
        self.startTransmit(media)

    def transmit_stop(self, call: SipCall):
        if self.sink is not None:
            self.stopTransmit(call.getAudioMedia(self.sink))
        self.tx_pattern = None

    def assert_payload_and_reset(self, call: SipCall, cmd: Dict):
        self.assert_payload(cmd)
        self.reset(call)

    def assert_payload(self, cmd: Dict):
        cmd = cmd['action']
        cmd_type: str = cmd['type']
        if cmd_type == 'playback':
            if 'play' in cmd['params']:
                payload: str = cmd['params']['play']['prompt_url']
            elif 'speak' in cmd['params']:
                payload: str = cmd['params']['speak']['text']
            else:
                assert False
        elif cmd_type == 'hold':
            payload: str = 'MOHMOH'
        elif cmd_type == 'wait':
            assert len(self.rx_buffer) == 0
            return
        elif cmd_type == 'ask':
            if 'play' in cmd['params']:
                payload: str = cmd['params']['play']['prompt_url']
            elif 'speak' in cmd['params']:
                payload: str = cmd['params']['speak']['text']
            else:
                assert False
        else:
            assert False
        assert bytes(payload, 'utf-8') in self.rx_buffer


class Player(pj.AudioMediaPlayer):
    def __init__(self):
        super(Player, self).__init__()
        self.sink: int = None

    def play(self, call: SipCall):
        self.createPlayer('/var/cache/ivr-dispatcher/tw/check.wav', pj.PJMEDIA_FILE_NO_LOOP)
        self.sink = call.peer_media_idx
        media: pj.AudioMedia = call.getAudioMedia(self.sink)
        self.startTransmit(media)
