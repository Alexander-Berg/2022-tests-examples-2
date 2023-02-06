from pytest import mark, raises

from rtnmgr_agent.decorator import retry


class TestRetry:
    @mark.asyncio
    async def test_retry(self):
        retry_counts = 3
        self.value = 0

        @retry(times=retry_counts)
        async def incr():
            self.value += 1
            raise ValueError("special exception")

        with raises(ValueError):
            await incr()

        assert self.value == 1 + retry_counts
