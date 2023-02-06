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


class AllOfTestComplexInlineResponsePost:
    _EXPECTED_CONTENT_TYPES = [
        utils.ContentType('text/plain; charset=utf-8'),
    ]

    log_extra: dict
    middlewares: middlewares_module.Middlewares
    body: str
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
    async def create(cls, request: web.Request) -> 'AllOfTestComplexInlineResponsePost':
        use_py3_isoformat: bool = cls._use_py3_isoformat
        body = await request.text()
        if not body:
            raise utils.ValidationError(
                'body is required'
            )
        else:
            allow_extra: bool = True
            data = body
            request['raw_body'] = data
            if utils.ContentType(request.headers.get('Content-Type')) not in cls._EXPECTED_CONTENT_TYPES:
                raise utils.ValidationError(
                    'Invalid Content-Type: %s; expected one of %s' % (
                        request.headers.get('Content-Type'),
                        ['text/plain; charset=utf-8'],
                    ),
                )
            body_ = utils.check_string(
                data,
                field_name='body',
            )
            
        return cls(
            request['log_extra'],
            request['_middlewares'],
            body_,
        )
