# pylint: disable=too-many-lines
# pylint: disable=invalid-string-quote
# pylint: disable=wildcard-import
# pylint: disable=ungrouped-imports
# pylint: disable=unused-wildcard-import
# pylint: disable=redefined-builtin
# pylint: disable=unused-variable
# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
# pylint: disable=unnecessary-lambda

# pylint: disable=bad-whitespace
# flake8: noqa

import datetime
import json
import orjson
import re
import typing
import uuid as uuid_module

from taxi.codegen import swaggen_serialization as utils
from taxi.util import dates as dates_utils
import logging

from aiohttp import web


from example_service.generated.web import middlewares_context as middlewares_module

logger = logging.getLogger(__name__)


class UseTestpoint:
    log_extra: dict
    middlewares: middlewares_module.Middlewares
    _use_py3_isoformat: bool = True

    def __init__(
        self,
        log_extra,
        middlewares,
    ) -> None:
        self.log_extra = log_extra
        self.middlewares = middlewares

    @classmethod
    async def create(cls, request: web.Request) -> 'UseTestpoint':
        use_py3_isoformat: bool = cls._use_py3_isoformat
        return cls(
            request['log_extra'],
            request['_middlewares'],
        )
