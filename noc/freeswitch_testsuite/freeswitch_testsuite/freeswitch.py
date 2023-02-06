from aiohttp import ClientSession
from asyncio import (
    create_subprocess_exec, ensure_future, shield,
    sleep, wait_for, TimeoutError, CancelledError)
from asyncio.subprocess import PIPE
from freeswitch_testsuite.environment_config import (
    LOG_DIR, CONF_DIR, DB_DIR, SOUNDS_DIR,
    RUN_DIR, WEB_BIND_ADDRESS, MOD_IVRD_PORT)
from freeswitch_testsuite.logs import log_debug, log_info, log_error
from typing import Dict
from socket import socket, AF_INET, SOCK_STREAM
from uuid import UUID


def is_valid_uuid(val: str):
    try:
        UUID(val)
        return True
    except ValueError:
        return False


async def create_leg_and_assert(session_id: str = None):
    async with ClientSession() as session:
        data: Dict = dict()
        if session_id:
            data = dict(session_id=session_id)
        async with session.post(f'http://{WEB_BIND_ADDRESS}:{MOD_IVRD_PORT}'
                                f'/create_leg', json=data) as resp:
            assert resp.status == 200
            reply = await resp.json()
            assert 'session_id' in reply
            if session_id:
                assert reply['session_id'] == session_id
            else:
                assert is_valid_uuid(reply['session_id'])


async def bad_create_leg_and_assert():
    async with ClientSession() as session:
        headers: Dict = {'Content-Type': 'application/json'}
        async with session.post(f'http://{WEB_BIND_ADDRESS}:{MOD_IVRD_PORT}'
                                f'/create_leg', data='BADBADDATA',
                                headers=headers) as resp:
            assert resp.status == 500


class FreeSwitch:
    def __init__(self, binary):
        self.running = False
        self.binary_path = binary
        self.os_process = None
        self.complete = None
        self.sman = None
        self.outfile = open('/dev/null', 'w')
        self.errfile = open(f'{LOG_DIR}/freeswitch-stderr.log', 'w')
        self.fs_pipe = PIPE
        log_debug('Freeswitch created')

    def __del__(self):
        log_debug('Freeswitch disposed')

    async def start(self):
        self.complete = ensure_future(self._start_fs_process())
        # TODO check Freeswitch startup more elegantly
        try:
            await wait_for(self.complete, timeout=2)
        except TimeoutError:
            log_debug('Freeswitch is starting')
            ivrd_socket = socket(AF_INET, SOCK_STREAM)
            while ivrd_socket.connect_ex((WEB_BIND_ADDRESS, MOD_IVRD_PORT)):
                await sleep(0.5)
            self.running = True
            log_info('Freeswitch started')
            return self
        else:
            raise FreeSwitchError(
                'FreeSwitch process {} exited with {}'.format(
                    self.os_process.pid, self.os_process.returncode))

    async def stop(self):
        self.os_process.terminate()
        try:
            await self.complete
        except CancelledError:
            pass
        log_info('Freeswitch stopped')

    async def _start_fs_process(self):
        args = [
            self.binary_path,
            '-nonat',
            '-log', LOG_DIR,
            '-conf', CONF_DIR,
            '-db', DB_DIR,
            '-run', RUN_DIR,
            '-sounds', SOUNDS_DIR
        ]
        self.os_process = await create_subprocess_exec(
            *args,
            stdin=self.fs_pipe,
            stdout=self.outfile,
            stderr=self.outfile
        )
        log_info(f'Freeswitch is starting. PID:{self.os_process.pid}')
        await shield(self.os_process.wait())
        self.running = False
        log_error(f'Freeswitch exit code {self.os_process.returncode}')
        if self.outfile:
            self.outfile.close()
        if self.errfile:
            self.errfile.close()
        if self.fs_pipe:
            self.fs_pipe = None


class FreeSwitchError(Exception):
    pass
