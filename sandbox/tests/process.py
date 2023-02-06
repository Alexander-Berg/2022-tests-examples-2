from __future__ import absolute_import, print_function

import os
import time
import errno
import socket
import signal
import random

from six.moves import queue as Queue

from sandbox.common import process
from sandbox.common import context


# noinspection PyMethodMayBeStatic
class TestInterProcessQueue(object):
    def test__simple(self):
        queue = process.InterProcessQueue()
        if not queue.fork():
            queue.put(queue.get() * 2)
            os._exit(0)
        data = 12345
        queue.start()
        queue.put(data)
        assert queue.get() == data * 2
        queue.stop()
        queue.join()

    def test__many_workers(self):
        queue = process.InterProcessQueue()
        workers_number = 10
        data_size = 1000
        with context.Timer() as timer:
            with timer["FORK"]:
                for i in range(workers_number):
                    if not queue.fork():
                        count = 0
                        while True:
                            data = queue.get()
                            if data is None:
                                print("Worker #{}: processed {} items".format(i, count))
                                os._exit(0)
                            count += 1
                            queue.put(data)
                input_data = set(range(data_size))

            print("\nProcessing {} item(s) by {} workers".format(data_size, workers_number))
            queue.start()
            with timer["PUT"]:
                for data in input_data:
                    queue.put(data)
            with timer["GET"]:
                output_data = [queue.get() for _ in range(len(input_data))]
            assert len(input_data) == len(output_data)
            assert input_data == set(output_data)
            elapsed = timer.secs
            with timer["STOP"]:
                queue.stop()
                queue.join()
            time.sleep(1)
        print("\nProcessed with speed {} rps in {}".format(data_size / elapsed, timer))

    def test__kill_some_workers(self):
        queue = process.InterProcessQueue()
        workers_number = 5
        data_size = 100
        for i in range(workers_number):
            if not queue.fork():
                while True:
                    try:
                        data = queue.get()
                        if data is None:
                            break
                        queue.put(data)
                        if i and random.random() < .5:
                            os.kill(os.getpid(), signal.SIGKILL)
                    except socket.error as ex:
                        if ex.errno in (errno.EPIPE, errno.ECONNRESET):
                            break
                        raise
                    os._exit(0)
        input_data = set(range(data_size))
        queue.start()
        for data in input_data:
            queue.put(data)
        try:
            data = queue.get(timeout=10)
        except Queue.Empty:
            data = None
        assert data is not None
        queue.stop()
        queue.join()
