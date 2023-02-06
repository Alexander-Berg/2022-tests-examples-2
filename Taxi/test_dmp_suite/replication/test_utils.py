import copy
import io
import json

import mock
import pytest
import requests
import gzip
import typing as tp

from dmp_suite.replication.api import api_utils, entities
from dmp_suite.replication.api.entities import (
    queue_read as queue_read_entities
)
from dmp_suite.replication.api.entities.queue_read import REPLICATION_FORMAT_HEADER
from urllib3.response import HTTPResponse


def make_response(data: dict, *, output_format, compressed=True) -> requests.Response:
    resp = requests.Response()
    resp.status_code = 200

    content = json.dumps(data)
    encoded_content = content.encode('utf-8')

    if compressed:
        compressed_content = gzip.compress(encoded_content)
        content_stream = io.BytesIO(compressed_content)
    else:
        content_stream = io.BytesIO(encoded_content)

    # Одинаковые заголовки важно передать и в Request от requests,
    # и во внутренний ответ из urllib, иначе не будет работать
    # декодирование сжатых данных урллибом:
    headers = {
        REPLICATION_FORMAT_HEADER: output_format
    }
    if compressed:
        headers['Content-Encoding'] = 'gzip'

    resp.headers.update(headers)

    raw_response = HTTPResponse(
        body=content_stream,
        preload_content=False,
        headers=headers,
    )
    resp.raw = raw_response
    return resp


@pytest.mark.parametrize(
    'doc,key_fields,sep,expected_key',
    [
        ({'a': 1}, ('a',), '_', '31'),
        ({'a': 1, 'b': 2}, ('a', 'b'), '_', '31_32'),
        ({'a': 1, 'b': 2, 'c': 3}, ('a', 'b', 'c'), '_', '31_32_33'),
        (
                {'a': 'йцуббб!"№;%:?*()_+-'},
                ('a',),
                '_',
                'd0b9d186d183d0b1d0b1d0b12122e284963b253a3f2a28295f2b2d'
        ),
        (
                {'a': 1, 'b': '2%#&(@)@ЩйЪъ'},
                ('a', 'b'),
                '_',
                '31_3225232628402940d0a9d0b9d0aad18a'
        ),
    ],
)
def test_key_creation(doc, key_fields, sep, expected_key):
    key = api_utils.make_key(doc, key_fields, sep)
    print(key)
    assert key == expected_key
    assert key.count(sep) == len(key_fields) - 1
    assert (
            tuple(str(doc[k]) for k in key_fields)
            == api_utils.parse_key(key, sep)
    )


class PicklableMock(mock.MagicMock):
    def __init__(self, return_value=None, side_effect=None, *args, **kwargs):
        super().__init__(
            return_value=return_value,
            side_effect=side_effect,
            *args,
            **kwargs,
        )
        self.__args = return_value, side_effect

    def __reduce__(self):
        return PicklableMock, self.__args


class ApiMock(mock.MagicMock):

    def __init__(
            self,
            partitions,
            replication_data,
            output_format='json',
            compressed=True,
            errors: tp.Optional[tp.List[Exception]]=None,
            *args,
            **kwargs,
    ):
        """

        :param partitions:
        :param replication_data:
        :param output_format:
        :param compressed:
        :param errors: Этот параметр может содержать список ошибок, которые будут райзиться методом
                       queue_read, пока не закончатся, после чего метод возвратить нормальный результат.
                       Исключения будут райзиться по списку, слева-направо.
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)

        self.__args = partitions, replication_data, output_format
        self.__errors = errors

        self.retrieve_partitions = PicklableMock(
            return_value=entities.RetrievePartitionsResponse.from_dict({
                'queue_partitions': partitions,
            })
        )

        data = copy.deepcopy(replication_data)

        for r in data:
            r['data'] = json.dumps(r['data'])

        def return_response(*args, **kwargs):
            if self.__errors:
                error = self.__errors[0]
                self.__errors = self.__errors[1:]
                raise error

            response = make_response(
                {
                    'confirm_id': '123',
                    'count': len(replication_data),
                    'last_upload_ts': None,  # DUMMY
                    'items': data,
                    'try_next_read_after': 1,
                    'output_format': output_format,
                },
                output_format=output_format,
                compressed=compressed,
            )
            return queue_read_entities.ReadResponse.subclass_from_response(response)

        # Этот мок вызывается несколько раз за время теста.
        # Раньше с этим не было проблем, так как из ReadResponse
        # можно было читать сколько угодно раз.
        # Теперь же прочитать можно лишь единожды. Поэтому правильнее,
        # чтобы каждый вызов queue_read возвращал новый объект ReadResponse.
        self.queue_read = mock.MagicMock(
            side_effect=return_response
        )

        self.confirm = PicklableMock(None)

    def __reduce__(self):
        return ApiMock, self.__args
