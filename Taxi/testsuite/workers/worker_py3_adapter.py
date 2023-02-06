import argparse
import asyncio
import dataclasses
import importlib
import socket
import sys
import time

import bson
import yaml


@dataclasses.dataclass(frozen=True)
class WorkerConfig:
    setup_function: str
    get_performer_function: str
    task_function: str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket-fd', required=True, type=int)
    parser.add_argument('--worker-config', required=True, type=str)
    parser.add_argument('--queue', required=True, type=str)
    parser.add_argument('--proc-number', required=True, type=int)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_handler(loop, args))
    loop.close()


async def _handler(loop, args):
    worker_config = _load_config(args.worker_config, args.queue)
    sock = socket.socket(family=socket.AF_UNIX, fileno=args.socket_fd)
    extra = {}
    if sys.version_info < (3, 10):
        extra['loop'] = loop
    reader, writer = await asyncio.open_connection(sock=sock, **extra)

    get_performer_func = _load_func(worker_config.get_performer_function)
    async with get_performer_func(
            args.queue,
            args.proc_number,
            worker_config.task_function,
            worker_config.setup_function,
    ) as performer:
        writer_lock = asyncio.Lock()
        await _send_data(writer, writer_lock, {'cmd': 'ready'})

        while True:
            request = await _recv_data(reader)
            if request['cmd'] == 'stop':
                break
            elif request['cmd'] == 'exec':
                asyncio.create_task(
                    _perform_task(writer, writer_lock, performer, request),
                )
                await _send_data(
                    writer, writer_lock, {'cmd': 'stats', 'cpu_used': 1},
                )
            else:
                raise RuntimeError('unexpected command: %s' % request['cmd'])

    sock.close()


async def _perform_task(writer, writer_lock, performer, request):
    start_time = time.time()
    success = False
    try:
        success = await performer.perform(request)
    except BaseException as exc:
        success = False
        if not isinstance(exc, Exception):
            raise
    finally:
        total_time = time.time() - start_time
        await _send_data(
            writer,
            writer_lock,
            {
                'cmd': 'mark',
                'task_id': request['task_id'],
                'success': success,
                'exec_time': int(total_time * 1000),
            },
        )


async def _send_data(writer, writer_lock, data):
    bson_data = bson.BSON.encode(data)
    async with writer_lock:
        writer.write(len(bson_data).to_bytes(4, byteorder='little'))
        writer.write(bson_data)
        await writer.drain()


async def _recv_data(reader):
    bson_size_binary = await reader.readexactly(4)
    bson_size = int.from_bytes(bson_size_binary, byteorder='little')
    bson_data = await reader.readexactly(bson_size)
    return bson.BSON(bson_data).decode()


def _load_func(function_path):
    module_path, function_name = function_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, function_name)


def _load_config(config_path, queue_name):
    with open(config_path) as in_file:
        data = yaml.load(in_file, Loader=getattr(yaml, 'CLoader', yaml.Loader))

    for queue_data in data['queues']:
        if queue_data['name'] == queue_name:
            setup_function = queue_data.get(
                'setup_function', data.get('setup_function'),
            )
            get_performer_function = queue_data.get(
                'get_performer_function', data.get('get_performer_function'),
            )
            task_function = queue_data.get('task_function')
            return WorkerConfig(
                setup_function, get_performer_function, task_function,
            )
    raise RuntimeError('Undefined queue')


if __name__ == '__main__':
    main()
