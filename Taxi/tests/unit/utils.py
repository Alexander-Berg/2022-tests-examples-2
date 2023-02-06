from pahtest.base import BaseTest
from pahtest.fake import FakeResult
from pahtest.results import TestResult



def get_test_result(message: str, test: BaseTest, success=True) -> TestResult:
    return TestResult(
        test=test, name='sleep', message=message, success=success
    )


def get_fake_result(message: str, test: BaseTest, success=True) -> FakeResult:
    return FakeResult(
        name='sleep', success=success, message=message, test=test
    )
