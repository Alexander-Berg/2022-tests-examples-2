import os
import signal
import subprocess

TEST_RETRIES_COUNT = 15


def get_pid(name: str) -> int:
    return int(subprocess.check_output(['pidof', name]))


def send_rotate_log_signal(pid: int) -> None:
    os.kill(pid, signal.SIGUSR1)


async def test_log_rotation(taxi_userver_ytlib_sample):
    pid = get_pid('yandex-taxi-userver-ytlib-sample')

    for _ in range(TEST_RETRIES_COUNT):
        send_rotate_log_signal(pid)
        response = await taxi_userver_ytlib_sample.get('ping')
        assert response.status_code == 200
