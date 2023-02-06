from enum import Enum


class TestStatuses(Enum):

    FAILED = (
        "FAILED", "BROKEN", "FAILURE", "NOTRUN", "CRASH"
    )
    PASSED = (
        "SUCCESS", "PASSED"
    )
    SKIPPED = (
        "CANCELED", "SKIPPED", "PENDING"
    )
    NOT_RUN = ("NOT_RUN")
    NOT_FOUND = ()
