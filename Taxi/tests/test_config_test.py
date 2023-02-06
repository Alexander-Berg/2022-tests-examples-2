import pytest
import requests
from pytest_socket import SocketBlockedError


def test_fail_socket():
    with pytest.raises(SocketBlockedError):
        requests.head('https://ya.ru')


@pytest.mark.slow
def test_no_fail_socket():
    requests.head('https://ya.ru')
