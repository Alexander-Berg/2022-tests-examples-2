import multiprocessing as mp
import os
import time
import typing

from django import test

from l3mgr.utils import open_and_lock, AcquireLockTimoutExceedError

TEMP_FILE: str = f"/tmp/tmp_{time.monotonic()}"
PS1_DATA: str = "ps1"
PS2_DATA: str = "ps2"


class ProcessParams(typing.NamedTuple):
    run: callable
    data: str
    event_start: mp.Event
    event_stop: mp.Event


# Fallback for deadlock (which should never happen)
DEFAULT_TIMEOUT: int = 5


class Unsync:
    @staticmethod
    def master(process_params):
        with open_and_lock(TEMP_FILE, quiet_retry=False) as f:
            f.write(process_params.data)
            process_params.event_start.set()
            process_params.event_stop.wait(timeout=DEFAULT_TIMEOUT)

    @staticmethod
    def slave(process_params):
        process_params.event_start.wait(timeout=DEFAULT_TIMEOUT)

        try:
            with open_and_lock(TEMP_FILE, wait_lock_timeout=0.00001, quiet_retry=False) as f:
                f.write(process_params.data)
        finally:
            process_params.event_stop.set()


class Sync:
    @staticmethod
    def master(process_params):
        with open_and_lock(TEMP_FILE, quiet_retry=False) as f:
            f.write(process_params.data)

        process_params.event_start.set()

    @staticmethod
    def slave(process_params):
        process_params.event_start.wait(timeout=DEFAULT_TIMEOUT)
        with open_and_lock(TEMP_FILE, wait_lock_timeout=10, quiet_retry=False) as f:
            f.write(process_params.data)

        process_params.event_stop.set()


def run_process(process_params):
    process_params.run(process_params)


def write_to_file_concurrently(process_params1, process_params2):
    with mp.Pool(2) as p:
        p.map(run_process, [process_params1, process_params2])


class FileLockingTest(test.SimpleTestCase):
    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(TEMP_FILE)
        except OSError:
            pass
        finally:
            super().tearDownClass()

    def test_lock_not_acquired(self):
        """
        Second process will not be able to acquire lock
        """
        with mp.Manager() as m:
            event_start, event_stop = m.Event(), m.Event()

            with self.assertRaises(AcquireLockTimoutExceedError):
                write_to_file_concurrently(
                    ProcessParams(Unsync.master, PS1_DATA, event_start, event_stop),
                    ProcessParams(Unsync.slave, PS2_DATA, event_start, event_stop),
                )

        with open(TEMP_FILE) as tmp:
            self.assertEqual(tmp.read(), PS1_DATA)

    def test_lock_acquired(self):
        """
        Both processes should be able to write to file in order
        """
        with mp.Manager() as m:
            event_start, event_stop = m.Event(), m.Event()

            write_to_file_concurrently(
                ProcessParams(Sync.master, PS1_DATA, event_start, event_stop),
                ProcessParams(Sync.slave, PS2_DATA, event_start, event_stop),
            )

            event_stop.wait(timeout=DEFAULT_TIMEOUT)

        with open(TEMP_FILE) as tmp:
            self.assertEqual(tmp.read(), PS2_DATA)
