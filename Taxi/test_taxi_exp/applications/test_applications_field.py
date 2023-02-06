import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment


EXPERIMENT_NAME = 'superapp'


@pytest.mark.parametrize(
    'applications, expected_status, expected_response',
    [
        pytest.param(
            [{'name': 'ios', 'version_range': {'from': None, 'to': None}}],
            200,
            None,
            id='success_empty_version_range',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_range': {'from': '0.0.0', 'to': '99.99.99'},
                },
            ],
            200,
            None,
            id='success_version_range',
        ),
        pytest.param(
            [{'name': 'ios', 'version_range': {'from': '0.0.0', 'to': None}}],
            200,
            None,
            id='success_version_range_with_none',
        ),
        pytest.param(
            [{'name': 'ios', 'version_range': {'from': '0.0.0'}}],
            200,
            None,
            id='success_version_range_with_non_existed',
        ),
        pytest.param(
            [{'name': 'ios'}],
            200,
            None,
            id='success_version_range_with_non_existed_version',
        ),
        pytest.param(
            [{'name': 'ios'}, {'name': 'android'}],
            200,
            None,
            id='success_version_range_with_non_existed_version',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_ranges': [
                        {'from': '0.0.0', 'to': '9.99.99'},
                        {'from': '10.0.0', 'to': '99.99.99'},
                    ],
                },
            ],
            200,
            None,
            id='success_version_ranges',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_ranges': [
                        {'from': '0.0.0', 'to': '9.99.99'},
                        {'from': '10.0.0', 'to': '99.99.99'},
                    ],
                },
                {
                    'name': 'android',
                    'version_range': {'from': '0.0.0', 'to': '99.99.99'},
                },
            ],
            200,
            None,
            id='success_version_ranges_and_version',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_ranges': [{'from': '0.0.0', 'to': '9.99.99'}],
                },
            ],
            200,
            None,
            id='success_version_ranges_with_one_element',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_range': {'from': '0.0.0', 'to': '99.99.99'},
                },
                {
                    'name': 'ios',
                    'version_range': {'from': '10.0.0', 'to': '99.99.99'},
                },
            ],
            400,
            {
                'message': (
                    'Application name must be unique in applications, '
                    'if need use version_ranges instead of multiple usage'
                ),
                'code': 'CHECK_SCHEMA_ERROR',
            },
            id='fail_if_app_name_duplicate',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_range': {'from': '10.0.0', 'to': '99.99.99'},
                    'version_ranges': [
                        {'from': '0.0.0', 'to': '9.99.99'},
                        {'from': '10.0.0', 'to': '99.99.99'},
                    ],
                },
            ],
            400,
            {
                'code': 'CHECK_SCHEMA_ERROR',
                'message': (
                    'Application must have only version_range (deprecated) '
                    'or version_ranges, do not use both'
                ),
            },
            id='fail_if_has_version_range_and_version_ranges_into_one_app',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_ranges': [
                        {'from': '0.0.0', 'to': '9.99.99'},
                        {'from': '9.0.0', 'to': '99.99.99'},
                    ],
                },
            ],
            400,
            {
                'code': 'CHECK_SCHEMA_ERROR',
                'message': 'Ranges must not overlap',
            },
            id='fail_if_version_ranges_intersected',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_ranges': [
                        {},
                        {'from': '9.0.0', 'to': '99.99.99'},
                    ],
                },
            ],
            400,
            {
                'code': 'CHECK_SCHEMA_ERROR',
                'message': 'Ranges must not overlap',
            },
            id='fail_if_version_ranges_intersected',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_ranges': [
                        {'from': '9.0.0', 'to': '99.99.99'},
                        {},
                    ],
                },
            ],
            400,
            {
                'code': 'CHECK_SCHEMA_ERROR',
                'message': 'Ranges must not overlap',
            },
            id='fail_if_version_ranges_intersected',
        ),
        pytest.param(
            [
                {
                    'name': 'ios',
                    'version_range': {'from': '9.99.99', 'to': '0.0.0'},
                },
            ],
            400,
            {
                'code': 'CHECK_SCHEMA_ERROR',
                'message': (
                    '"from" field must be lower version than "to" field'
                ),
            },
            id='fail_if_from_greatest_to',
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_applications_field(
        taxi_exp_client, applications, expected_status, expected_response,
):
    experiment_body = experiment.generate(
        EXPERIMENT_NAME, applications=applications,
    )

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=experiment_body,
    )
    assert response.status == expected_status, await response.text()

    if expected_status != 200:
        assert await response.json() == expected_response
        return

    # smoke tests
    await helpers.experiment_smoke_tests(taxi_exp_client, EXPERIMENT_NAME)
