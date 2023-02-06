import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

NAME = 'tech_groups'


@pytest.mark.parametrize(
    'is_tech_group,predicate,expected_clause,status',
    [
        (
            True,
            {'type': 'true'},
            {
                'title': 'title',
                'predicate': {'type': 'true'},
                'value': {},
                'is_tech_group': True,
            },
            200,
        ),
        (
            False,
            {'type': 'true'},
            {'title': 'title', 'predicate': {'type': 'true'}, 'value': {}},
            200,
        ),
        (
            False,
            experiment.mod_sha1_predicate(),
            {
                'title': 'title',
                'predicate': {
                    'type': 'mod_sha1_with_salt',
                    'init': {
                        'arg_name': 'phone_id',
                        'divisor': 100,
                        'range_from': 0,
                        'range_to': 100,
                        'salt': 'salt',
                    },
                },
                'value': {},
            },
            200,
        ),
        *(
            (True, predicate, {}, 400)
            for predicate in [
                experiment.mod_sha1_predicate(),
                experiment.allof_predicate([experiment.mod_sha1_predicate()]),
                experiment.anyof_predicate([experiment.mod_sha1_predicate()]),
                experiment.not_predicate(experiment.mod_sha1_predicate()),
            ]
        ),
    ],
)
@pytest.mark.pgsql('taxi_exp', queries=[db.INIT_QUERY])
async def test_tech_group(
        taxi_exp_client, is_tech_group, predicate, expected_clause, status,
):
    clause = experiment.make_clause('title', predicate=predicate)
    if is_tech_group:
        clause['is_tech_group'] = True
    body = experiment.generate(NAME, clauses=[clause])

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == status, await response.text()
    if response.status != 200:
        return

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == status, await response.text()
    body = await response.json()
    assert body['clauses'][0] == expected_clause
