# coding: utf8
# pylint: disable=bare-except

import asyncio
import importlib
import itertools
import logging
import sys
import time
import traceback

from sibilla import processing
from sibilla import utils
from sibilla.test import event
from sibilla.test import request

from . import _base


logger = logging.getLogger(__name__)


def grouper(number, iterable):
    iterator = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(iterator, number))
        if not chunk:
            return
        yield chunk


def call_decorator(raw_function_name, *args, **kwargs):
    modname, fn_name = raw_function_name.rsplit('.', 1)
    module = importlib.import_module(modname)
    if not hasattr(module, fn_name):
        raise Exception('Could not find test decorator')
    callable_object = getattr(module, fn_name)
    return callable_object(*args, **kwargs)


class Test(_base.BaseTest):
    async def exec(self) -> bool:
        """
        Execute test with actual context
        :return:
        """
        await self._context.logger.log(
            event.EVENT_TEST_START, name=self.name, dump=self.dump,
        )
        actual_result = True
        headers: dict = {}
        tvm_headers: dict = {}
        if self._context.tvm_client and self._context.config.TVM_ENABLED:
            tvm_headers = await self._context.tvm_client.get_auth_headers(
                self.tvm_name,
            )
        try:
            for header in processing.Source(
                    self.headers, storage=self._context.container,
            ):
                headers.update(header)
            headers.update(tvm_headers)
            logger.debug('Prepare base headers %s', str(headers))
            for chunk in grouper(50, self.queries()):
                tasks = [
                    asyncio.ensure_future(self.get_result(headers, query_data))
                    for query_data in chunk
                ]
                results = await asyncio.gather(*tasks)
                if False in results:
                    actual_result = False
        # pylint: disable=broad-except
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_text = ''.join(traceback.format_tb(exc_traceback))
            text = (
                'tescase-wide exception {exc_type}: {exc_value}\n'
                'traceback:\n{exc_traceback}'.format(
                    exc_type=exc_type.__name__ if exc_type else 'None',
                    exc_value=str(exc_value),
                    exc_traceback=tb_text,
                )
            )
            await self._context.logger.log(
                event.EVENT_TEST_RESULT_FAIL,
                name=self.name,
                query=request.Query(),
                error=text,
            )
        await self._context.logger.log(
            event.EVENT_TEST_COMPLETE, name=self.name,
        )
        return actual_result

    # pylint: disable=too-many-branches
    async def get_result(self, headers: dict, query_data: request.Query):
        if self.before:  # prepare data before request if need
            await call_decorator(self.before, query=query_data)
        # repeatable check for query
        attempt = 0
        startup_time = time.time()
        deadline = startup_time + self.wait.wait_time
        retry_attempts = self.wait.attempts
        expected_data = utils.build(
            query_data.expected
            if query_data.expected is not None
            else self.result,
            query_data,
        )
        while True:
            attempt += 1
            try:  # try to perform request to inspecting service
                # await for some time if need
                if self.wait.backoff_time > 0 and attempt != 1:
                    await asyncio.sleep(self.wait.backoff_time)
                response = await self._context.session.request(
                    self.method, self.url, **query_data, headers=headers,
                )
                data = {
                    'status': response.status,
                    'data': await response.text(),
                }
                if response.content_type.lower() == 'application/json':
                    data['json'] = await response.json()
                if utils.contains(expected_data, data):
                    # good news: we got what's we expected!
                    await self._context.logger.log(
                        event.EVENT_TEST_RESULT_SUCCESS,
                        name=self.name,
                        query=query_data,
                        expected=expected_data,
                        result=data,
                    )
                    if self.after:  # clean up the data
                        await call_decorator(
                            self.after, response=response, query=query_data,
                        )
                    if self.alias:  # store good results for posterity
                        self._context.container.put(self.alias, data)
                    return True  # good news for everyone
            # pylint: disable=unused-variable, broad-except
            except Exception as error_info:
                data = {}
                # something went wrong when we've perform the request
                logger.error('exception caught: %s', str(error_info))
                await self._context.logger.log(
                    event.EVENT_TEST_RESULT_FAIL,
                    name=self.name,
                    query=query_data,
                    error=str(error_info),
                )
            # unexpected result. check if we can try again
            finish_him = False
            now = time.time()
            if self.wait.wait_time and deadline <= now:
                logger.warning(
                    'time limit exceed (%d sec)\n', self.wait.wait_time,
                )
                finish_him = True
            elif not self.wait.wait_time and retry_attempts <= attempt:
                logger.warning(
                    'attempts limit exceed (%d <= %d)\n',
                    retry_attempts,
                    attempt,
                )
                finish_him = True

            if finish_him:  # Nothing personal, it's just business
                await self._context.logger.log(
                    event.EVENT_TEST_RESULT_ERROR,
                    name=self.name,
                    query=query_data,
                    expected=expected_data,
                    result=data,
                )
                return False  # return with bad news
            if retry_attempts:
                logger.warning(
                    '... try again (attempt %d of %d) ...',
                    attempt + 1,
                    retry_attempts,
                )
            else:
                logger.warning(
                    '... try again (%d sec to deadline) ...', deadline - now,
                )
