import jsonpath
import pytest

from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

CONFIG_NAME = 'superscreen_conf'
EXPERIMENT_NAME = 'superscreen_exp'
CREATE_CONFIG_PATH = 'data.config.clauses.0.predicate.init.set'
CREATE_EXP_PATH = 'data.experiment.clauses.0.predicate.init.set'
UPDATE_CONFIG_PATH = 'data.config.clauses.0.predicate.init.set'
UPDATE_EXP_PATH = 'data.experiment.clauses.0.predicate.init.set'


def _gen_clauses(phones):
    return [
        experiment.make_clause(
            'First',
            predicate=experiment.inset_predicate(
                phones,
                transform='replace_phone_to_phone_id',
                phone_type='yandex',
            ),
        ),
    ]


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
        'features': {'common': {'enable_convert_phone_to_phone_id': True}},
    },
)
async def test_return_phone_ids_to_apply(taxi_exp_client, patch_user_api):
    patch_user_api.add('aaaabbbccc', '+79112377865')
    patch_user_api.add('aaaabbbcdd', '+74955554433')
    patch_user_api.add('fffabbbccc', '+79219377865')
    patch_user_api.add('fffabbbcdd', '+78125554433')

    # create config
    config_body = experiment.generate_config(
        clauses=_gen_clauses(['+74955554433', '+79112377865']),
    )

    params = {'name': CONFIG_NAME}
    response = await taxi_exp_client.post(
        '/v1/configs/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=config_body,
    )
    assert response.status == 200
    body = await response.json()
    assert jsonpath.jsonpath(body, CREATE_CONFIG_PATH)[0] == [
        'aaaabbbccc',
        'aaaabbbcdd',
    ], body

    response = await taxi_exp_client.post(
        '/v1/configs/drafts/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200

    # update config
    config_body = experiment.generate_config(
        clauses=_gen_clauses(['+79219377865', '+78125554433']),
    )
    params = {'name': CONFIG_NAME, 'last_modified_at': 1}
    response = await taxi_exp_client.put(
        '/v1/configs/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=config_body,
    )
    assert response.status == 200
    body = await response.json()
    assert jsonpath.jsonpath(body, UPDATE_CONFIG_PATH)[0] == [
        'fffabbbccc',
        'fffabbbcdd',
    ]
    response = await taxi_exp_client.put(
        '/v1/configs/drafts/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200

    # create experiment
    experiment_body = experiment.generate_default(
        clauses=_gen_clauses(['+74955554433', '+79112377865']),
    )
    params = {'name': EXPERIMENT_NAME}
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == 200
    body = await response.json()
    assert jsonpath.jsonpath(body, CREATE_EXP_PATH)[0] == [
        'aaaabbbccc',
        'aaaabbbcdd',
    ]
    response = await taxi_exp_client.post(
        '/v1/experiments/drafts/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200

    # update experiment
    experiment_body = experiment.generate_default(
        clauses=_gen_clauses(['+79219377865', '+74955554433']),
    )
    params = {'name': EXPERIMENT_NAME, 'last_modified_at': 3}
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == 200
    body = await response.json()
    assert jsonpath.jsonpath(body, UPDATE_EXP_PATH)[0] == [
        'aaaabbbcdd',
        'fffabbbccc',
    ]
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200

    # close experiment
    await db.close_experiment(taxi_exp_client.app, EXPERIMENT_NAME)

    # update closed experiment
    experiment_body = experiment.generate_default(
        clauses=_gen_clauses(
            ['+79219377865', '+79112377865', '+74955554433', '+78125554433'],
        ),
    )
    params = {'name': EXPERIMENT_NAME, 'last_modified_at': 5}
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == 200
    body = await response.json()
    assert jsonpath.jsonpath(body, UPDATE_EXP_PATH)[0] == [
        'aaaabbbccc',
        'aaaabbbcdd',
        'fffabbbccc',
        'fffabbbcdd',
    ]
    response = await taxi_exp_client.post(
        '/v1/closed-experiments/apply/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body['data'],
    )
    assert response.status == 200
