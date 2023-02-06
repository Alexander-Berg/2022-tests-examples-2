import pytest

from test_taxi_exp.helpers import db

SAME_FIELDS = ['exp_name', 'exp_description']

REV = {
    'exp_with_pred_with_apps': 1,
    'exp_with_pred_no_apps': 2,
    'exp_no_pred_with_apps': 3,
    'exp_no_pred_no_apps': 4,
    'exp_no_clauses_with_pred_with_apps': 5,
    'exp_no_clauses_with_pred_no_apps': 6,
    'exp_no_clauses_no_pred_with_apps': 7,
    'exp_no_clauses_no_nothing': 8,
}

APPS_CLAUSE_TRUE = {
    'type': 'any_of',
    'init': {
        'predicates': [
            {
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'value': 'android',
                                'arg_name': 'application',
                                'arg_type': 'string',
                            },
                        },
                        {
                            'type': 'gte',
                            'init': {
                                'value': '1.1',
                                'arg_name': 'version',
                                'arg_type': 'version',
                            },
                        },
                        {
                            'type': 'lte',
                            'init': {
                                'value': '100.100',
                                'arg_name': 'version',
                                'arg_type': 'version',
                            },
                        },
                    ],
                },
                'type': 'all_of',
            },
        ],
    },
}


@pytest.mark.parametrize('modification', ['close', 'close_and_disable'])
@pytest.mark.parametrize(
    'name',
    [
        'exp_with_pred_with_apps',
        'exp_with_pred_no_apps',
        'exp_no_pred_with_apps',
        'exp_no_pred_no_apps',
        'exp_no_clauses_with_pred_with_apps',
        'exp_no_clauses_with_pred_no_apps',
        'exp_no_clauses_no_pred_with_apps',
        'exp_no_clauses_no_nothing',
    ],
)
@pytest.mark.pgsql('taxi_exp', files=['experiments_to_uplifting.sql'])
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'enable_uplift_experiment': True}},
    },
)
async def test_create_config_by_experiment(
        taxi_exp_client, modification, name,
):
    data = {
        'experiment_name': name,
        'last_updated_at': REV[name],
        'modification': modification,
    }
    response = await taxi_exp_client.post(
        '/v1/experiments/uplift-to-config/',
        headers={'YaTaxi-Api-Key': 'secret'},
        json=data,
    )

    assert response.status == 200
    json = await response.json()
    assert json == {}

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': name},
    )
    assert response.status == 200
    old_experiment = await response.json()
    need_enabled = modification == 'close'
    assert old_experiment['match']['enabled'] == need_enabled

    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': name},
    )
    assert response.status == 200
    response_body = await response.json()
    assert not response_body['is_technical']

    experiment = await db.get_experiment(taxi_exp_client.app, name)
    assert not experiment['exp_removed']

    config = await db.get_config(taxi_exp_client.app, name)
    for field in SAME_FIELDS:
        assert experiment[field] == config[field]

    # check configs count
    response = await taxi_exp_client.get(
        '/v1/configs/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    data = await response.json()
    assert len(data['configs']) == 1

    # check experiments count
    response = await taxi_exp_client.get(
        '/v1/experiments/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'show_closed': 'true'},
    )
    assert response.status == 200
    data = await response.json()
    assert len(data['experiments']) == 8

    response = await taxi_exp_client.get(
        '/v1/configs/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': name},
    )
    assert response.status == 200
    new_config = await response.json()
    assert new_config['match']['predicate'] == {'init': {}, 'type': 'true'}

    with_apps = 'with_apps' in name
    with_pred = 'with_pred' in name

    apps_offset: int = with_apps
    pred_offset: int = with_pred

    if 'no_clauses' not in name:
        if with_apps or with_pred:
            for i in range(
                    max(
                        len(old_experiment['clauses']),
                        len(new_config['clauses']),
                    ),
            ):
                current_clause_predicate = new_config['clauses'][i][
                    'predicate'
                ]
                current_clause_value = new_config['clauses'][i]['value']
                assert current_clause_predicate['type'] == 'all_of'
                if with_apps:
                    assert (
                        current_clause_predicate['init']['predicates'][0]
                        == APPS_CLAUSE_TRUE
                    )
                if with_pred:
                    assert (
                        current_clause_predicate['init']['predicates'][
                            apps_offset
                        ]
                        == old_experiment['match']['predicate']
                    )
                assert (
                    current_clause_predicate['init']['predicates'][
                        apps_offset + pred_offset
                    ]
                    == old_experiment['clauses'][i]['predicate']
                )
                assert (
                    current_clause_value
                    == old_experiment['clauses'][i]['value']
                )
        else:
            assert old_experiment['clauses'] == new_config['clauses']
    else:
        if with_apps or with_pred:
            assert len(new_config['clauses']) == 1
            main_predicate = new_config['clauses'][0]['predicate']
            main_value = new_config['clauses'][0]['value']
            assert main_value == old_experiment['default_value']
            if with_apps and with_pred:
                assert main_predicate['type'] == 'all_of'
                assert len(main_predicate['init']['predicates']) == 2
                apps_subclause = main_predicate['init']['predicates'][0]
                pred_subclause = main_predicate['init']['predicates'][1]
                assert apps_subclause == APPS_CLAUSE_TRUE
                assert pred_subclause == old_experiment['match']['predicate']
            elif with_pred:
                assert main_predicate == old_experiment['match']['predicate']
            elif with_apps:
                assert main_predicate == APPS_CLAUSE_TRUE
        else:
            assert new_config['clauses'] == []
