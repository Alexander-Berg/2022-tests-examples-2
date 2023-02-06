import pytest

from taxi.tools.dorblu.dorblu_uploader.dorblu_retry import retry


class Exception1:
    pass


class Exception2:
    pass


class Functor:
    def __init__(self):
        self.counter = 0

    def __call__(self):
        self.counter += 1
        if self.counter == 1:
            raise Exception1()
        elif self.counter == 2:
            raise Exception2()
        else:
            return "Hello world!"


def test_retry():
    value = retry(Functor(), exceptions=(Exception1, Exception2), delay=1)
    assert value == "Hello world!"


def test_retry_failure():
    with pytest.raises(Exception1):
        retry(Functor(), exceptions=(Exception1, Exception2), retries=1, delay=1)


def test_retry_unknown_exception():
    with pytest.raises(Exception2):
        retry(Functor(), exceptions=Exception1, delay=1)
