import typing

import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import experiment as exp_generator

EXPERIMENT_NAME = 'test_experiment_name'


class Case(typing.NamedTuple):
    comment: str
    applications: typing.Optional[list]
    expected: typing.Optional[list]
    is_bad: bool = False

    def __str__(self):
        return self.comment


@pytest.mark.parametrize(
    helpers.get_args(Case),
    [
        Case(comment='Full empty', applications=None, expected=None),
        Case(
            comment='Fill from, empty to',
            applications=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1.0', 'to': None},
                },
            ],
            expected=[{'name': 'android', 'version_range': {'from': '1.1.0'}}],
        ),
        Case(
            comment='Full filled',
            applications=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1.0', 'to': '10.10.0'},
                },
            ],
            expected=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1.0', 'to': '10.10.0'},
                },
            ],
        ),
        Case(
            comment='Two apps',
            applications=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1.0', 'to': '10.10.0'},
                },
                {
                    'name': 'ios',
                    'version_range': {'from': '1.1.1', 'to': '10.10.2'},
                },
            ],
            expected=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1.0', 'to': '10.10.0'},
                },
                {
                    'name': 'ios',
                    'version_range': {'from': '1.1.1', 'to': '10.10.2'},
                },
            ],
        ),
        Case(
            comment='Wrong version - less',
            applications=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1', 'to': '10.10.0'},
                },
            ],
            expected=None,
            is_bad=True,
        ),
        Case(
            comment='Wrong version - greater',
            applications=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1.1.1', 'to': '10.10.0'},
                },
            ],
            expected=None,
            is_bad=True,
        ),
        Case(
            comment='Wrong version - another symbols',
            applications=[
                {
                    'name': 'android',
                    'version_range': {'from': '1.1.1-abcd', 'to': '10.10.0'},
                },
            ],
            expected=None,
            is_bad=True,
        ),
        pytest.param(
            *Case(
                comment='Send and return version_ranges',
                applications=[
                    {
                        'name': 'android',
                        'version_ranges': [
                            {'from': '1.1.1', 'to': '10.10.0'},
                            {'from': '11.1.1', 'to': '20.10.0'},
                        ],
                    },
                ],
                expected=[
                    {
                        'name': 'android',
                        'version_ranges': [
                            {'from': '1.1.1', 'to': '10.10.0'},
                            {'from': '11.1.1', 'to': '20.10.0'},
                        ],
                    },
                ],
                is_bad=False,
            ),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_join_versions': True}},
                },
            ),
        ),
        pytest.param(
            *Case(
                comment='Send and return without versions',
                applications=[{'name': 'android'}],
                expected=[{'name': 'android', 'version_ranges': [{}]}],
                is_bad=False,
            ),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_join_versions': True}},
                },
            ),
        ),
        pytest.param(
            *Case(
                comment='Send and return without versions',
                applications=[{'name': 'android'}],
                expected=[{'name': 'android', 'version_range': {}}],
                is_bad=False,
            ),
            marks=pytest.mark.config(
                EXP3_ADMIN_CONFIG={
                    'features': {'common': {'enable_join_versions': False}},
                },
            ),
        ),
    ],
    ids=helpers.idfn,
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_applications(
        applications, expected, comment, is_bad, taxi_exp_client,
):
    experiment = exp_generator.generate()
    if applications is not None:
        experiment['match']['applications'] = applications

    # create experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
        json=experiment,
    )
    if is_bad:
        assert response.status == 400
        return

    assert response.status == 200

    # obtaining updates
    result = await helpers.get_updates(taxi_exp_client)
    assert result['experiments'][0]['match'].get('applications') == expected

    # get experiment
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': EXPERIMENT_NAME},
    )
    assert response.status == 200
    result = await response.json()
    assert result['match'].get('applications') == expected

    # experiment exists in db
    assert await helpers.db.get_experiment(
        taxi_exp_client.app, EXPERIMENT_NAME,
    )

    # get link from experiment to any application
    db_response = await helpers.db.get_applications(
        taxi_exp_client.app, EXPERIMENT_NAME,
    )

    if applications is None:
        assert not db_response
        return

    expected_apps_count = 0
    for app in expected:
        if 'version_range' in app:
            expected_apps_count += 1
        else:
            expected_apps_count += len(app.get('version_ranges', []))

    if not expected_apps_count:
        expected_apps_count = 1
    assert expected_apps_count == len(db_response)
