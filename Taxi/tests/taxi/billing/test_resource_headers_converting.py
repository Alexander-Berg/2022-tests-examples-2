from typing import List
from typing import Optional

import multidict
import pytest

from taxi.billing import resource_limiter

_SPENT_RESOURCES_HEADER = 'X-YaTaxi-SpentResources'


def _make_headers_dict(
        header_name: Optional[str], resources_str_list: Optional[List[str]],
) -> multidict.CIMultiDict:
    if not header_name or not resources_str_list:
        return multidict.CIMultiDict()
    headers = [
        (header_name, resources_str) for resources_str in resources_str_list
    ]
    return multidict.CIMultiDict(headers)


@pytest.mark.parametrize(
    'resources, header_name, expected_headers',
    [
        ([], _SPENT_RESOURCES_HEADER, multidict.CIMultiDict()),
        (
            [
                resource_limiter.Resource(
                    name='/v1/balances/select:yt:balances', amount=5,
                ),
                resource_limiter.Resource(
                    name='/v1/balances/select:pg:balances', amount=10,
                ),
            ],
            '',  # no header name
            _make_headers_dict(None, None),
        ),
        (
            [
                resource_limiter.Resource(
                    name='/v1/balances/select:yt:balances', amount=5,
                ),
                resource_limiter.Resource(
                    name='/v1/balances/select:pg:balances', amount=10,
                ),
            ],
            _SPENT_RESOURCES_HEADER,
            _make_headers_dict(
                _SPENT_RESOURCES_HEADER,
                [
                    '/v1/balances/select:yt:balances,5',
                    '/v1/balances/select:pg:balances,10',
                ],
            ),
        ),
        (
            [
                resource_limiter.Resource(name='same_resource', amount=5),
                resource_limiter.Resource(name='same_resource', amount=10),
            ],
            _SPENT_RESOURCES_HEADER,
            _make_headers_dict(
                _SPENT_RESOURCES_HEADER,
                ['same_resource,5', 'same_resource,10'],
            ),
        ),
        (
            [resource_limiter.Resource(name='only_one_resource', amount=7)],
            'new_header',
            _make_headers_dict('new_header', ['only_one_resource,7']),
        ),
    ],
)
def test_convert_resources_to_headers(
        resources, header_name, expected_headers,
):
    headers = resource_limiter.convert_resources_to_headers(
        header_name=header_name, resources=resources,
    )
    assert headers == expected_headers


@pytest.mark.parametrize(
    'headers, header_name, expected_resources',
    [
        (_make_headers_dict(None, None), _SPENT_RESOURCES_HEADER, []),
        (
            _make_headers_dict('another_header', ['some info']),
            _SPENT_RESOURCES_HEADER,
            [],
        ),
        (
            _make_headers_dict(
                _SPENT_RESOURCES_HEADER,
                [
                    '/v1/balances/select:yt:balances,5',
                    '/v1/balances/select:pg:balances,10',
                ],
            ),
            _SPENT_RESOURCES_HEADER,
            [
                resource_limiter.Resource(
                    name='/v1/balances/select:yt:balances', amount=5,
                ),
                resource_limiter.Resource(
                    name='/v1/balances/select:pg:balances', amount=10,
                ),
            ],
        ),
        (
            _make_headers_dict(
                _SPENT_RESOURCES_HEADER,
                ['same_resource,5', 'same_resource,10'],
            ),
            _SPENT_RESOURCES_HEADER,
            [
                resource_limiter.Resource(name='same_resource', amount=5),
                resource_limiter.Resource(name='same_resource', amount=10),
            ],
        ),
        (
            _make_headers_dict(
                _SPENT_RESOURCES_HEADER, ['only_one_resource,11'],
            ),
            _SPENT_RESOURCES_HEADER,
            [resource_limiter.Resource(name='only_one_resource', amount=11)],
        ),
    ],
)
def test_get_resources_from_headers(headers, header_name, expected_resources):
    resources = resource_limiter.resources_from_headers(
        headers=headers, header_name=header_name,
    )
    assert resources == expected_resources
