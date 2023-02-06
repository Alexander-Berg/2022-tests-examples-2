import asyncio
import inspect


class BaseError(Exception):
    """Base exception class for this module."""


class CallQueueError(BaseError):
    pass


class CallQueueEmptyError(CallQueueError):
    pass


class CallQueueTimeoutError(CallQueueError):
    pass


class AsyncCallQueue:
    def __init__(self, func):
        self._func = func
        self._name = func.__name__
        self._queue = asyncio.Queue()
        self._get_callinfo = callinfo(func)
        self._is_coro = inspect.iscoroutinefunction(func)

    async def __call__(self, *args, **kwargs):
        try:
            if self._is_coro:
                return await self._func(*args, **kwargs)
            return self._func(*args, **kwargs)
        finally:
            await self._queue.put((args, kwargs))

    def flush(self):
        self._queue = asyncio.Queue()

    @property
    def has_calls(self):
        return self.times_called > 0

    @property
    def times_called(self):
        return self._queue.qsize()

    def next_call(self):
        try:
            return self._get_callinfo(*self._queue.get_nowait())
        except asyncio.queues.QueueEmpty:
            raise CallQueueEmptyError(
                'No calls for %s() left in the queue' % (self._name,),
            )

    async def wait_call(self, timeout=10.0):
        try:
            item = await asyncio.wait_for(self._queue.get(), timeout=timeout)
            return self._get_callinfo(*item)
        except asyncio.TimeoutError:
            raise CallQueueTimeoutError(
                'Timeout while waiting for %s() to be called' % (self._name,),
            )


class CallsInfoWrapper:
    """Function wrapper that adds information about function calls.

    Wrapped function `__dict__` is extended with two public attributes:

        `call`  - pops information about first call
        `calls` - pops all calls information

    """

    def __init__(self, func):
        self._func = func
        self._calls = []
        self.__dict__.update(func.__dict__)

    @property
    def call(self):
        return self._calls.pop(0) if self._calls else None

    @property
    def calls(self):
        calls = self._calls
        self._calls = []
        return calls

    def __call__(self, *args, **kwargs):
        dct = callinfo(self._func)(args, kwargs)
        self._calls.append(dct)
        return self._func(*args, **kwargs)


def callinfo(func):
    func_spec = inspect.getfullargspec(func)
    func_varkw = func_spec.varkw
    func_kwonlyargs = func_spec.kwonlyargs
    func_kwonlydefaults = func_spec.kwonlydefaults

    func_args = func_spec.args
    func_varargs = func_spec.varargs
    defaults = func_spec.defaults or ()
    func_defaults = dict(zip(func_args[-len(defaults) :], defaults))

    def callinfo_getter(args, kwargs):
        dct = dict(zip(func_args, args))
        for argname in func_args[len(args) :]:
            if argname in kwargs:
                dct[argname] = kwargs[argname]
            else:
                dct[argname] = func_defaults.get(argname)
        if func_varargs is not None:
            dct[func_varargs] = args[len(dct) :]
        for argname in func_kwonlyargs:
            if argname in kwargs:
                dct[argname] = kwargs[argname]
            else:
                dct[argname] = func_kwonlydefaults[argname]
        if func_varkw is not None:
            dct[func_varkw] = {k: v for k, v in kwargs.items() if k not in dct}
        return dct

    return callinfo_getter


def acallqueue(func):
    if isinstance(func, AsyncCallQueue):
        return func
    return AsyncCallQueue(func)
