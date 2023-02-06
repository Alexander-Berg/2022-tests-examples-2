import logging
import math
import threading
import time
import typing
from contextlib import closing, ContextDecorator
from functools import wraps
from unittest.mock import patch

import celery
from celery import shared_task, signals
from celery.contrib.testing.worker import TestWorkController, start_worker
from django import db
from django.db import DEFAULT_DB_ALIAS, transaction
from django.dispatch import Signal
from django.test import TransactionTestCase, TestCase, utils
from kombu import Exchange, Queue

logger = logging.getLogger(__name__)


def _collapse_name(queue_id: str, target: int) -> str:
    to_remove = math.ceil((len(queue_id) - target) / 2)
    mid = len(queue_id) // 2
    queue_id = queue_id[0 : mid - to_remove - 1] + ".." + queue_id[mid + to_remove :]
    return queue_id


class _WorkController(TestWorkController):
    timeout = 5
    terminated_event = threading.Event()

    def setup_instance(
        self,
        queues=None,
        ready_callback=None,
        pidfile=None,
        include=None,
        use_eventloop=None,
        exclude_queues=None,
        **kwargs,
    ) -> None:

        app = self.app
        signals.celeryd_after_setup.send(
            sender=self.hostname,
            instance=self,
            conf=app.conf,
        )

        super().setup_instance(queues, ready_callback, pidfile, include, use_eventloop, exclude_queues, **kwargs)

    def ensure_started(self) -> None:
        self._on_started.wait(self.timeout)

    def close(self) -> None:
        self.stop()
        self.terminate()
        self.blueprint.join(self.timeout)
        if not self.terminated_event.wait(self.timeout):
            raise AssertionError("Failed to wait worker to terminate")
        db.connections.close_all()

    def start(self) -> None:
        try:
            super().start()
        finally:
            db.connections.close_all()
            self.terminated_event.set()

    def on_start(self) -> None:
        super().on_start()
        self.purge_messages()

    def purge_messages(self) -> None:
        with self.app.connection_for_write() as connection:
            count = self.app.control.purge(connection=connection)
            if count:
                logger.info(
                    "purge: Erased %s %s from the queue.",
                    count,
                    "message" if count == 1 else "messages",
                )


def override_defaults(method_to_decorate, **overrides):
    @wraps(method_to_decorate)
    def wrapper(*args, **kwargs):
        kw_copy = kwargs.copy()
        for k, v in overrides.items():
            if k not in kwargs:
                kw_copy[k] = v
        return method_to_decorate(*args, **kw_copy)

    return wrapper


def with_worker(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        assert isinstance(args[0], TransactionTestCase) and not isinstance(
            args[0], TestCase
        ), """
Worker will be run in separate thread. To see changes in db all transactions should be committed"""

        from l3.celery import app

        # import test tasks as worker expect ping task to be registered
        # noinspection PyUnresolvedReferences
        from celery.contrib.testing.tasks import ping  # noqa
        from amqp.abstract_channel import AbstractChannel
        from time import monotonic

        # let's use channel for each test individually
        queue_id = f"{int(monotonic())}|{f.__qualname__}"

        # trunk use postgresql which allows only 64 channel name length
        if len(queue_id) > 62:
            queue_id = _collapse_name(queue_id, 62)

        wait = override_defaults(AbstractChannel.wait, timeout=_WorkController.timeout)
        with patch.object(AbstractChannel, "wait", wait):
            with override_celery_settings(
                broker_url="memory://",
                result_backend="memory://",
                broker_transport_options={"polling_interval": 0.001},
                task_default_queue=queue_id,
                queues=[Queue(queue_id, Exchange(queue_id, delivery_mode=1), routing_key=queue_id, durable=False)],
            ), start_worker(
                app, WorkController=_WorkController, loglevel=logging.DEBUG, queues=[queue_id]
            ) as worker, closing(
                worker
            ):
                return f(*args, **kwargs)

    return wrapper


def shared_callback_task(*args, **kwargs):
    def create_task(*targs, **tkwargs):
        def inner(f):
            task_called_signal = Signal()
            e = threading.Event()

            def callback(*args, **kwargs):
                e.set()

            setattr(e, "callback", callback)

            task_called_signal.connect(e.callback)

            @wraps(f)
            def wrapper(*args, **kwargs):
                try:
                    f(*args, **kwargs)
                finally:
                    task_called_signal.send(sender=f.__name__)

            task = (shared_task(*targs, **tkwargs))(wrapper)
            setattr(task, "task_called_signal", task_called_signal)
            setattr(task, "completion_event", e)

            return task

        return inner

    if len(args) == 1 and callable(args[0]):
        return create_task(**kwargs)(args[0])
    return create_task(*args, **kwargs)


# noinspection PyPep8Naming
class patching(utils.TestContextDecorator):
    def __init__(self, *args):
        self.patchers = args
        super().__init__()

    def enable(self) -> None:
        for idx, patcher in enumerate(self.patchers):
            try:
                patcher.start()
            except:
                for p in reversed(self.patchers[:idx]):
                    p.stop()
                raise

    def disable(self) -> None:
        for patcher in reversed(self.patchers):
            patcher.stop()


# noinspection PyPep8Naming
class override_celery_settings(utils.TestContextDecorator):
    def __init__(self, **kwargs):
        self.options = kwargs
        super().__init__()

    def enable(self):
        conf = self._get_default_app().conf
        for key, new_value in self.options.items():
            conf[key] = new_value

    def disable(self) -> None:
        self._get_default_app().conf.clear()

    @staticmethod
    def _get_default_app() -> celery.Celery:
        # noinspection PyProtectedMember
        from celery._state import get_current_app

        return get_current_app()  # omit proxy


class _VerboseQueriesContext(utils.CaptureQueriesContext, ContextDecorator):
    def __init__(self, using: typing.Optional[str] = None, detailed: bool = False) -> None:
        connection = transaction.get_connection(using)
        self.detailed = detailed
        super().__init__(connection)

    def __enter__(self) -> utils.CaptureQueriesContext:
        self.started = time.perf_counter()
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        super().__exit__(exc_type, exc_value, traceback)
        if exc_type is not None:
            return
        finished = time.perf_counter()
        executed = len(self)

        details = (":\n" + self.format_captured_queries()) if self.detailed else ""
        logger.info(f"{(finished - self.started):.2f}sec - {executed} queries executed{details}")

    def format_captured_queries(self) -> str:
        offset = 0
        indent = ""
        lines = []
        width = len(str(len(self.captured_queries)))
        for i, query in enumerate(self.captured_queries, start=1):
            sql = query["sql"] or "--"
            if sql.startswith("SAVEPOINT "):
                offset += 1
            elif sql.startswith("RELEASE SAVEPOINT "):
                offset -= 1
                indent = "  " * offset
            lines.append(f"/* {i:>{width}} */ {indent}{sql};")
            indent = "  " * offset
        return "\n".join(lines)


def verbose_queries(using: typing.Optional[str] = None, detailed: bool = False) -> utils.CaptureQueriesContext:
    # Bare decorator: @verbose_queries -- although the first argument is called `using`, it's actually the function being decorated.
    if callable(using):
        return _VerboseQueriesContext(DEFAULT_DB_ALIAS, detailed)(using)
    # Decorator: @verbose_queries(...) or context manager: with verbose_queries(...): ...
    return _VerboseQueriesContext(using, detailed)
