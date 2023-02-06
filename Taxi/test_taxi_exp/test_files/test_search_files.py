import typing

import pytest

from test_taxi_exp.helpers import files


def get_args(typename: typing.Any) -> str:
    return ','.join(typename.__annotations__.keys())


class SearchCase(typing.NamedTuple):
    query: dict  # noqa
    expected_response: typing.Optional[dict]  # noqa


@pytest.mark.parametrize(
    get_args(SearchCase),
    [
        SearchCase(
            query={'id': '1aaabbb'},
            expected_response={
                'files': [
                    {
                        'id': '1aaabbb',
                        'name': 'f11',
                        'namespace': None,
                        'version': 1,
                        'experiment_name': None,
                        'file_type': 'string',
                        'removed': False,
                    },
                ],
            },
        ),
        SearchCase(
            query={'name': 'f11'},
            expected_response={
                'files': [
                    {
                        'name': 'f11',
                        'namespace': None,
                        'version': 1,
                        'id': '1aaabbb',
                        'experiment_name': None,
                        'file_type': 'string',
                        'removed': False,
                    },
                    {
                        'name': 'f11',
                        'namespace': None,
                        'version': 2,
                        'id': '2cccccc',
                        'experiment_name': None,
                        'file_type': 'string',
                        'removed': False,
                    },
                    {
                        'name': 'f11',
                        'namespace': None,
                        'version': 3,
                        'id': '3dddddd',
                        'experiment_name': None,
                        'file_type': 'string',
                        'removed': False,
                    },
                ],
            },
        ),
        SearchCase(
            query={'experiment': '_by_user'},
            expected_response={
                'files': [
                    {
                        'id': 'b0070d7d47e04af8abcd83f154421741',
                        'name': 'with_experiment_name',
                        'namespace': None,
                        'version': 1,
                        'experiment_name': 'experiment_by_user',
                        'file_type': 'string',
                        'removed': False,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('fill.sql',))
async def test_search_files(query, expected_response, taxi_exp_client):
    response = await files.search_file(
        taxi_exp_client, namespace=None, **query,
    )
    assert response.status == 200
    assert await response.json() == expected_response
