import random
import string
import typing

import pytest

from taxi import discovery

from test_taxi_exp.helpers import files


class Case(typing.NamedTuple):
    original_content: str
    binary_content: bytes
    expected_content: bytes
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
    'original_content,binary_content,expected_content,code,is_bad',
    [
        Case(
            original_content="""+79219998866\n+78211112233\n""",
            binary_content=b"""+79219998866\n+78211112233""",
            expected_content=b"""66889991297+\n33221111287+\n""",
            code=200,
            is_bad=False,
        ),
        Case(
            original_content=ORIGINAL,
            binary_content=BIN_ORIGINAL,
            expected_content=EXPECTED,
            code=200,
            is_bad=False,
        ),
        Case(
            original_content="""+79219998866\n+78211112233\nAAAABBBB""",
            binary_content=b"""+79219998866\n+78211112233\nAAAABBBB""",
            expected_content=b'',
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
                {'id': item['value'][::-1], 'value': item['value']}
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

    # update file
    updated_response = await files.post_file(
        taxi_exp_client, 'file_1.txt', binary_content, enable_transform=True,
    )
    assert updated_response.status == 200
    # get file with original data
    data = await updated_response.json()
    response = await files.get_original_file_by_mds_id(
        taxi_exp_client, data['id'],
    )
    responsed_text = await response.text()
    assert responsed_text == original_content
