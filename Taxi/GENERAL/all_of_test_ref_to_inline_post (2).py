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

import example_service.generated.service.swagger.models.api as api_module

from example_service.generated.web import middlewares_context as middlewares_module

logger = logging.getLogger(__name__)


class AllOfTestRefToInlinePost:
    log_extra: dict
    middlewares: middlewares_module.Middlewares
    body: 'api_module.InlineNameAgeObject'
    _use_py3_isoformat: bool = True

    def __init__(
        self,
        log_extra,
        middlewares,
        body,
    ) -> None:
        self.log_extra = log_extra
        self.middlewares = middlewares
        self.body = body

    @classmethod
    async def create(cls, request: web.Request) -> 'AllOfTestRefToInlinePost':
        use_py3_isoformat: bool = cls._use_py3_isoformat
        body = await request.read()
        if not body:
            raise utils.ValidationError(
                'body is required'
            )
        else:
            allow_extra: bool = True
            try:
                data = orjson.loads(body)
                request['raw_body'] = data

            except orjson.JSONDecodeError as exc:
                logger.warning(
                    'Failed to decode json: %s',
                    exc,
                    extra=request.get('log_extra'),
                )
                raise utils.ValidationError(
                    'Failed to decode json'
                ) from None
            else:
                body_ = api_module.InlineNameAgeObject.deserialize(
                    data,
                    allow_extra=allow_extra,
                    use_py3_isoformat=use_py3_isoformat,
                )
            
        return cls(
            request['log_extra'],
            request['_middlewares'],
            body_,
        )
