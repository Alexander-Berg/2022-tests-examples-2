import pytest


@pytest.mark.parametrize(
    ('request_body', 'expected_response'),
    [
        pytest.param('some_user', 'hello', id='no_match'),
        pytest.param('matching_user', 'hi', id='match'),
    ],
)
@pytest.mark.experiments3(filename='experiments.json')
async def test_experiment_handler(
        taxi_arcadia_userver_test, request_body, expected_response,
):
    response = await taxi_arcadia_userver_test.post(
        '/experiments/try', data=request_body,
    )

    assert response.status_code == 200, response.text

    result = response.json()['value']
    assert result == expected_response


async def test_experiment_handler_defaults(taxi_arcadia_userver_test):
    response = await taxi_arcadia_userver_test.post(
        '/experiments/try', data='some_user',
    )

    assert response.status_code == 200, response.text

    result = response.json()['value']
    assert result == 'hello'
