import attr


DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_BACKOFF_TIME = 5
DEFAULT_WAIT_TIME = 0


@attr.s
class WaitSettings:
    """Wait settings for test"""

    backoff_time: int = attr.ib(default=DEFAULT_BACKOFF_TIME)
    attempts: int = attr.ib(default=DEFAULT_RETRY_ATTEMPTS)
    wait_time: int = attr.ib(default=DEFAULT_WAIT_TIME)
