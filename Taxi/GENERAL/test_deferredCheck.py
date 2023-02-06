from library.mocks.deferred_check import DEFERRED_CHECK_BODY
from library.deferred_check_request import deferred_check_request


def test_deferred_check_success():
    result = deferred_check_request(DEFERRED_CHECK_BODY)
    assert len(result) > 0


if __name__ == '__main__':
    test_deferred_check_success()
