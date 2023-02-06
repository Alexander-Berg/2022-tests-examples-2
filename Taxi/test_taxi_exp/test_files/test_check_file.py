import typing
from typing import Dict
from typing import Optional

import pytest

from test_taxi_exp.helpers import files

CONTENT = b"""aaaaaaaaa
bbbbbbbb
cccccccc
dddddddd
eeeeeeee"""

DIGITS = b"""12345
44444
55555
77777"""


class Case(typing.NamedTuple):
    body: bytes
    file_type: Optional[str]
    check: Optional[str]
    status: int
    expected_response: Dict


@pytest.mark.parametrize(
    'body, file_type, check, status, expected_response',
    [
        pytest.param(
            *Case(
                body=CONTENT,
                file_type=None,
                check=None,
                status=200,
                expected_response={
                    'hash': (
                        '39a2c29f73c953841bbb79fa5dc8e6d0'
                        '7bf179b40cf55027ea87682435dbcac2'
                    ),
                    'lines': 5,
                },
            ),
            id='default',
        ),
        pytest.param(
            *Case(
                body=b'a' * 140000,
                file_type=None,
                check=None,
                status=400,
                expected_response={
                    'code': 'BAD_FILE_FORMAT',
                    'message': 'Line is too long',
                },
            ),
            id='one long line',
        ),
        (
            CONTENT,
            'integer',
            None,
            400,
            {'code': 'BAD_VALUE', 'message': 'aaaaaaaaa is not integer'},
        ),
        (
            DIGITS,
            'integer',
            None,
            200,
            {
                'hash': (
                    'e44073a6d4f051332f38d59bba3e983a'
                    '0838e48dbc5085a26eb570807d70a0ea'
                ),
                'lines': 4,
            },
        ),
        (
            DIGITS,
            'int',
            None,
            200,
            {
                'hash': (
                    'e44073a6d4f051332f38d59bba3e983a'
                    '0838e48dbc5085a26eb570807d70a0ea'
                ),
                'lines': 4,
            },
        ),
        (
            DIGITS,
            'integer',
            'range_integer:10:20',
            400,
            {'code': 'BAD_VALUE', 'message': '12345 is not in range: 10 - 20'},
        ),
        (
            CONTENT,
            'string',
            'len:2',
            400,
            {
                'code': 'BAD_VALUE',
                'message': 'String must length less than 2 and more than 0',
            },
        ),
        (
            DIGITS,
            'string',
            'regexp:\\d+',
            200,
            {
                'hash': (
                    'e44073a6d4f051332f38d59bba3e983a'
                    '0838e48dbc5085a26eb570807d70a0ea'
                ),
                'lines': 4,
            },
        ),
        (
            DIGITS,
            'string',
            'regexp:\\d+;range_integer:10:20',
            400,
            {
                'code': 'INCORRECT_FILETYPE',
                'message': (
                    'Bad format. Use "file_type;check" or "file_type". '
                    'Allowed file_type: "integer", "string". '
                    'Example checks: "len:10", "range_integer:101:257", '
                    '"regexp:\\d+"'
                ),
            },
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp')
async def test_files(
        body, file_type, check, status, expected_response, taxi_exp_client,
):
    response = await files.post_file(
        taxi_exp_client, 'file.txt', body, file_type=file_type, check=check,
    )
    assert response.status == status
    body = await response.json()
    body.pop('id', None)  # id always new
    assert body == expected_response
