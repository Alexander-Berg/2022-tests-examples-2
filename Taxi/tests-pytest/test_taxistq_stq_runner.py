import bson
import pytest
import socket
import struct
import subprocess


class Channel:
    def __init__(self, sock):
        self._sock = sock

    def send(self, data):
        bson_data = bson.BSON.encode(data)
        self._sock.send(struct.pack('<i', len(bson_data)))
        self._sock.send(bson_data)

    def recv(self):
        bson_size_binary = self._sock.recv(4, socket.MSG_WAITALL)
        bson_size = struct.unpack('<i', bson_size_binary)[0]
        bson_data = self._sock.recv(bson_size, socket.MSG_WAITALL)
        return bson.BSON(bson_data).decode()


def launch_worker(queue='blocking_queue'):
    sock, sock2 = socket.socketpair(socket.AF_UNIX)
    p = subprocess.Popen([
        'python2', 'taxi_stq/stq_runner/worker_launcher.py',
        '--socket-fd', str(sock2.fileno()),
        '--queue', queue,
        '--proc-number', '0',
        '--worker-config',
        'tests-pytest/static/test_taxistq_stq_runner/test_worker_config.yaml'
    ], stderr=subprocess.STDOUT)

    return Channel(sock), p


@pytest.mark.asyncenv('blocking')
def test_start_worker():
    channel, p = launch_worker()
    cmd = channel.recv()
    assert cmd == {'cmd': 'ready'}
    stats = channel.recv()
    assert stats['cmd'] == 'stats'
    assert stats['cpu_used'] > 0
    channel.send({'cmd': 'stop'})
    p.wait()


@pytest.mark.parametrize('queue', ['blocking_queue', 'async_queue'])
@pytest.mark.parametrize('success', [True, False])
@pytest.mark.asyncenv('blocking')
def test_task_execution(queue, success):
    channel, p = launch_worker(queue)
    cmd = channel.recv()
    assert cmd == {'cmd': 'ready'}
    channel.send({
        'cmd': 'exec',
        'task_id': 'task',
        'args': [],
        'kwargs': {'failure': not success}
    })
    result = channel.recv()
    # there is sleep in the task for 0.1 second
    assert result.pop('exec_time') >= 100
    assert result == {'task_id': 'task', 'cmd': 'mark', 'success': success}
    channel.send({'cmd': 'stop'})
    p.wait()
