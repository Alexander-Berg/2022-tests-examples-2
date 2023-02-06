import contextlib
import importlib
import inspect
import logging
import sys

logger = logging.getLogger(__name__)


class TaskPerformer:
    def __init__(self, queue, task_function_path, context):
        self._perform_func = _load_func(task_function_path)
        self._queue = queue
        self._context = context

    async def perform(self, task):
        succeeded = False
        exc_info = None
        try:
            await self._perform_func(
                self._context, *task['args'], **task['kwargs'],
            )
        # pylint: disable=W0703
        except BaseException as exc:
            exc_info = sys.exc_info()
            if not isinstance(exc, Exception):
                raise
        else:
            succeeded = True
        finally:
            if succeeded:
                level = logging.INFO
            else:
                level = logging.ERROR
            logger.log(
                level,
                '[%s] Task %s finished (%s, args %r, kwargs %r)',
                self._queue,
                self._perform_func.__name__,
                task['task_id'],
                task['args'],
                task['kwargs'],
                exc_info=exc_info,
            )
        return succeeded


class ContextSetup:
    def __init__(self, queue, coro):
        self.coro = coro
        self._queue = queue
        self._is_async_gen = inspect.isasyncgen(coro)

    async def __aenter__(self):
        try:
            if self._is_async_gen:
                return await self.coro.__anext__()

            return await self.coro
        except Exception as exc:  # pylint: disable=broad-except
            logger.critical(
                '[%s] cannot exec on run callback: %s; exit',
                self._queue,
                exc,
                exc_info=True,
            )

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._is_async_gen:
            try:
                await self.coro.__anext__()
            except StopAsyncIteration:
                return
            else:
                raise RuntimeError('Async generator didn\'t stop')


@contextlib.asynccontextmanager
async def task_performer(
        queue_name, proc_number, task_function_path, setup_function_path,
):
    async with ContextSetup(
            queue_name, _load_func(setup_function_path)(),
    ) as context:
        yield TaskPerformer(queue_name, task_function_path, context)


def _load_func(function_path):
    module_path, function_name = function_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, function_name)
