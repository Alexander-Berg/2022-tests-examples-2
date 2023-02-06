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

from aiohttp import web
import multidict





class AllOfTestAdditionalPropertiesLeakPost200:
    _use_py3_isoformat: bool = True

    @property
    def status(self):
        return 200

    def __init__(
        self,
        data: str,
    ) -> None:
        super().__init__()
        self._data = data
        self._json: typing.Union[None, typing.List, typing.Dict] = None
        self._dumped_data: typing.Union[None, str, bytes, bytearray] = None
        self._content_type = 'text/plain; charset=utf-8'

    def serialize(self) -> web.Response:
        use_py3_isoformat: bool = self._use_py3_isoformat
        serialized_data_ = self.data
        if not isinstance(serialized_data_, str):
            raise utils.ValidationError(
                'Invalid value for body: '
                '%.1024r is not instance of str' % serialized_data_,
            )


        serialized_data = serialized_data_
        self._dumped_data = str(serialized_data)
        formatted_headers: multidict.CIMultiDict = multidict.CIMultiDict({
            'Content-Type': self._content_type,
        })
        return web.Response(
            status=self.status,
            headers=formatted_headers,
            text=self._dumped_data,
        )


    @property
    def json_data(self):
        return self._json


    @property
    def dumped_data(self):
        return self._dumped_data


    @property
    def data(self):
        return self._data


    @property
    def content_type(self):
        return self._content_type
