import random
import string
import typing

import pytest

from taxi import discovery

from test_taxi_exp import helpers
from test_taxi_exp.helpers import files


class Case(typing.NamedTuple):
    original_content: str
    binary_content: bytes
    expected_content: bytes
    file_size: int
    lines: int
    file_hash: str
    code: int
    is_bad: bool


def _gen_content():
    random.seed(1111)
    content = [
        '+7{random_string}'.format(
            random_string=(
                ''.join([random.choice(string.digits) for n in range(10)])
            ),
        )
        for _ in range(1000)
    ]
    o_content = ('\n'.join(content)) + '\n'
    rev_content = ('\n'.join(value[::-1] for value in content)) + '\n'
    return o_content, o_content.encode('utf-8'), rev_content.encode('utf-8')


ORIGINAL, BIN_ORIGINAL, EXPECTED = _gen_content()


@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        Case(
            original_content="""+79219998866\n+78211112233\n""",
            binary_content=b"""+79219998866\n+78211112233""",
            expected_content=b"""66889991297+\n33221111287+\n""",
            file_size=26,
            lines=2,
            file_hash=(
                '78e3e7833e680440697af0840f75c4bd'
                'eb5e0a68a0726d6ba1223977a89d4cc9'
            ),
            code=200,
            is_bad=False,
        ),
        Case(
            original_content=ORIGINAL,
            binary_content=BIN_ORIGINAL,
            expected_content=EXPECTED,
            file_size=13000,
            lines=1000,
            file_hash=(
                '816d291178fb89032c1a116268d35467'
                '7ff941658eefe4e462a0af9880c8c88b'
            ),
            code=200,
            is_bad=False,
        ),
        Case(
            original_content="""+79219998866\n+78211112233\nAAAABBBB""",
            binary_content=b"""+79219998866\n+78211112233\nAAAABBBB""",
            expected_content=b'',
            file_size=26,
            lines=2,
            file_hash=(
                '78e3e7833e680440697af0840f75c4bd'
                'eb5e0a68a0726d6ba1223977a89d4cc9'
            ),
            code=400,
            is_bad=True,
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'src': 'taxi_exp', 'dst': 'personal'}])
async def test_upload_file_with_transform(
        original_content,
        binary_content,
        expected_content,
        file_size,
        lines,
        file_hash,
        code,
        is_bad,
        taxi_exp_client,
        patch_aiohttp_session,
        response_mock,
        mockserver,
):
    @patch_aiohttp_session(
        '{}v1/countries/list'.format(
            discovery.find_service('territories').url,
        ),
    )
    def _countries_from_territories(method, url, **kwargs):
        return response_mock(
            json={
                'countries': [
                    {
                        '_id': 'aaaaa',
                        'phone_code': '7',
                        'phone_min_length': 11,
                        'phone_max_length': 11,
                        'national_access_code': '7',
                    },
                ],
            },
        )

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    async def _phone_ids_from_personal(request):
        request_json = request.json

        return {
            'items': [
                {'id': item['value'][::-1], 'value': item['value'] + 'xxx'}
                for item in request_json['items']
            ],
        }

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _phones_from_personal(request):
        request_json = request.json

        return {
            'items': [
                {'id': item['id'], 'value': item['id'][::-1]}
                for item in request_json['items']
            ],
        }

    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', binary_content, enable_transform=True,
    )
    assert response.status == code
    if is_bad:
        return

    data = await response.json()
    text = await files.get_file_body(taxi_exp_client, data['id'])
    assert text == expected_content

    # get file with original data
    response = await files.get_original_file_by_mds_id(
        taxi_exp_client, data['id'],
    )
    responsed_text = await response.text()
    assert responsed_text == original_content

    # check metadata
    response = await files.search_file(taxi_exp_client, id=data['id'], limit=1)
    assert response.status == 200
    result = await response.json()
    assert result['files'][0]['metadata'] == {
        'file_format': 'string',
        'file_size': file_size,
        'lines': lines,
        'sha256': file_hash,
    }
