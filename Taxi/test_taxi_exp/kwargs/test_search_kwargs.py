import jsondiff
import pytest


@pytest.mark.parametrize(
    'request_body,code,answer',
    [
        pytest.param(
            {'consumers': ['filled_consumer']},
            200,
            {
                'kwargs_info': [
                    {
                        'consumer': 'filled_consumer',
                        'kwargs': [
                            {
                                'name': 'app_version',
                                'type': 'application_version',
                            },
                            {'name': 'phone_id', 'type': 'string'},
                        ],
                        'metadata': {'library_version': '1.1.1'},
                        'library_version': '1.1.1',
                    },
                ],
            },
            id='filled_consumer',
        ),
        pytest.param(
            {'consumers': ['non_filled_consumer']},
            200,
            {
                'kwargs_info': [
                    {
                        'consumer': 'non_filled_consumer',
                        'kwargs': [],
                        'library_version': None,
                    },
                ],
            },
            id='non_filled_but_existed_consumer',
        ),
        pytest.param(
            {'consumers': ['unknown_consumer']},
            200,
            {
                'kwargs_info': [
                    {
                        'consumer': 'unknown_consumer',
                        'kwargs': [],
                        'metadata': {'status': 'not_found'},
                        'library_version': None,
                    },
                ],
            },
            id='unknown_consumer',
        ),
        pytest.param(
            {'consumers': []},
            404,
            {
                'message': 'Not filled consumers',
                'code': 'EMPTY_CONSUMERS_LIST',
            },
            id='empty_consumer_list',
        ),
        pytest.param(
            {'consumers': ['a_consumer', 'filled_consumer']},
            200,
            {
                'kwargs_info': [
                    {
                        'consumer': 'a_consumer',
                        'kwargs': [{'name': 'zone', 'type': 'string'}],
                        'library_version': None,
                    },
                    {
                        'consumer': 'filled_consumer',
                        'kwargs': [
                            {
                                'name': 'app_version',
                                'type': 'application_version',
                            },
                            {'name': 'phone_id', 'type': 'string'},
                        ],
                        'metadata': {'library_version': '1.1.1'},
                        'library_version': '1.1.1',
                    },
                ],
            },
            id='multiple_consumers',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('filled_kwargs.sql',))
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {'deprecated_kwargs': ['application.store_country']},
        },
    },
)
async def test_search_kwargs(request_body, code, answer, taxi_exp_client):
    response = await taxi_exp_client.post(
        '/v1/consumers/kwargs/search/',
        headers={'X-Ya-Service-Ticket': '123'},
        json=request_body,
    )
    assert response.status == code
    response_body = await response.json()
    diff = jsondiff.diff(response_body, answer)
    assert not diff
