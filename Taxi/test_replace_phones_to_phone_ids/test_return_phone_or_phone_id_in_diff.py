import pytest

from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'existed_experiment'


def _found_key(test_key, tested):
    for key in tested.keys():
        if key == test_key:
            return True

        if isinstance(tested[key], dict):
            result = _found_key(test_key, tested[key])
            if result:
                return result
        if isinstance(tested[key], list):
            result = any(
                _found_key(test_key, item)
                for item in tested[key]
                if isinstance(item, dict)
            )
            if result:
                return result

    return False


@pytest.mark.parametrize('is_return_phone_id', [True, False])
@pytest.mark.config(
    TVM_RULES=[{'src': 'taxi_exp', 'dst': 'personal'}],
    EXP3_ADMIN_CONFIG={
        'settings': {'common': {'in_set_max_elements_count': 100}},
        'features': {'common': {'enable_convert_phone_to_phone_id': True}},
    },
)
@pytest.mark.pgsql('taxi_exp', files=('default.sql', 'existed_experiment.sql'))
async def test_return_phone_or_phone_id_in_diff(
        is_return_phone_id, taxi_exp_client, patch_user_api, monkeypatch,
):
    patch_user_api.add('aaaabbbccc', '+79219201111')
    patch_user_api.add('aaaabbbcdd', '89219201234')

    monkeypatch.setattr(
        taxi_exp_client.app.config,
        'EXP_EXTENDED_DRAFTS',
        [
            {
                'DRAFT_NAME': '__default__',
                'NEED_CHECKING_FILES': True,
                'NEED_CHECKING_BODY': True,
                'ENABLE_REPLACE_PHONE_TO_PHONE_ID_IN_DIFF': is_return_phone_id,
            },
        ],
    )
    experiment_body = experiment.generate_default(
        match_predicate=experiment.inset_predicate(
            set_=['+79219201111'],
            transform='replace_phone_to_phone_id',
            phone_type='yandex',
        ),
    )
    params = {'name': EXPERIMENT_NAME, 'last_modified_at': 1}

    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=experiment_body,
    )
    assert response.status == 200

    body = await response.json()
    new = body['diff']['new']
    old = body['diff']['current']
    if is_return_phone_id:
        assert new['match']['predicate']['init']['set'] == ['aaaabbbccc']
        assert old['match']['predicate']['init']['set'] == ['aaaabbbcdd']
    else:
        assert new['match']['predicate']['init']['set'] == ['+79219201111']
        assert old['match']['predicate']['init']['set'] == ['89219201234']
    assert body['data']['experiment']['match']['predicate']['init']['set'] == [
        'aaaabbbccc',
    ]

    assert not _found_key('query', new)
    assert not _found_key('query', old)
