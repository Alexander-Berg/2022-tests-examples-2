import http
import typing

import pytest

from test_chatterbox_admin import constants as const


@pytest.mark.pgsql('chatterbox_admin', files=['init_db_data.sql'])
@pytest.mark.parametrize(
    'search_parameters, expected_result',
    (
        (
            {'name': 'awesome name'},
            {
                'logics': [
                    {
                        'id': const.LOGIC_UUID_1,
                        'name': 'awesome name',
                        'url': 'awesome url',
                    },
                ],
            },
        ),
        (
            {'name': 'Awesome '},
            {
                'logics': [
                    {
                        'id': const.LOGIC_UUID_1,
                        'name': 'awesome name',
                        'url': 'awesome url',
                    },
                ],
            },
        ),
        (
            {'theme': 'awesome theme'},
            {
                'logics': [
                    {
                        'id': const.LOGIC_UUID_1,
                        'name': 'awesome name',
                        'url': 'awesome url',
                    },
                    {
                        'id': const.LOGIC_UUID_2,
                        'name': 'not my name',
                        'url': 'not my url',
                    },
                ],
            },
        ),
        (
            {'theme': 'not my theme'},
            {
                'logics': [
                    {
                        'id': const.LOGIC_UUID_1,
                        'name': 'awesome name',
                        'url': 'awesome url',
                    },
                ],
            },
        ),
        (
            {'name': 'awesome name', 'theme': 'awesome theme'},
            {
                'logics': [
                    {
                        'id': const.LOGIC_UUID_1,
                        'name': 'awesome name',
                        'url': 'awesome url',
                    },
                ],
            },
        ),
        ({'name': 'not my name', 'theme': 'not my theme'}, {'logics': []}),
        ({'name': 'awesome something'}, {'logics': []}),
        ({'theme': 'not_exists_theme'}, {'logics': []}),
    ),
)
async def test_search_logics(
        taxi_chatterbox_admin_web,
        search_parameters: typing.Dict[str, str],
        expected_result: dict,
):
    response = await taxi_chatterbox_admin_web.post(
        '/v1/logics/search', json=search_parameters,
    )

    assert response.status == http.HTTPStatus.OK

    content = await response.json()
    expected_result['logics'].sort(key=lambda x: x['id'])
    content['logics'].sort(key=lambda x: x['id'])
    assert content == expected_result


@pytest.mark.parametrize(
    'search_parameters, expected_status', (({}, http.HTTPStatus.BAD_REQUEST),),
)
async def test_search_with_unspecified_parameters(
        taxi_chatterbox_admin_web,
        search_parameters: typing.Dict[str, str],
        expected_status: str,
):
    response = await taxi_chatterbox_admin_web.post(
        '/v1/logics/search', json=search_parameters,
    )
    assert response.status == expected_status
