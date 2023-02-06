"""
    Describes statistics events
"""
# pylint: disable=import-only-modules
import datetime
import logging

from simulator.core import queue
from simulator.core.runner import Runner


LOG = logging.getLogger(__name__)


@queue.event_handler
async def pre_start(
        *, timestamp: datetime.datetime = datetime.datetime.now(), **_,
):
    """
    Pre start event
    """


@queue.event_handler
async def post_finish(
        *,
        timestamp: datetime.datetime = datetime.datetime.now(),
        runner: Runner,
        **_,
):
    """
    Post finish event
    """
    runner.stats.set_finish(timestamp)
