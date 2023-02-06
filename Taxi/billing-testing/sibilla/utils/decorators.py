# coding: utf8

import asyncio
import time

from sibilla.test import _base


def retry(wrapper_fn):
    async def wrap(cls: _base.BaseTest, *args, **kwargs):
        # pylint: disable=broad-except
        attempt = 0
        current_time = time.time()
        wait = cls.wait
        retry_attempt = wait.attempts
        wait_time = wait.wait_time
        backoff_time = wait.backoff_time
        if wait_time <= 0 and retry_attempt <= 0:
            raise Exception('You should setup wait_time or retry_attempt')
        while True:
            if 0 < retry_attempt <= attempt:
                break
            if 0 < wait_time <= time.time() - current_time:
                break
            if backoff_time > 0:
                await asyncio.sleep(backoff_time)
            try:
                res = await wrapper_fn(cls, *args, **kwargs)
                if res:
                    return res
            except Exception:
                pass
            attempt += 1
        return False

    return wrap
