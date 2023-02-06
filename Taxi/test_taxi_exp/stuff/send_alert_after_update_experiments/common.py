from test_taxi_exp.helpers import experiment


PHONES = ['+79998886655', '+79998886644', '+76668886643']
USER_API_PHONE_IDS = [
    '5d68ee201ef4755d66d55faf',
    '5d68ee221ef4755d66d55fb0',
    '5d68ee221ef4755d66d55fb1',
]
PREDICATE_WITH_PHONES = {
    'type': 'in_set',
    'init': {
        'set': PHONES,
        'set_elem_type': 'string',
        'arg_name': 'phone_id',
        'phone_type': 'yandex',
        'transform': 'replace_phone_to_phone_id',
    },
}
UPDATED_PREDICATE_WITH_PHONES = {
    'type': 'in_set',
    'init': {
        'set': PHONES[1:],
        'set_elem_type': 'string',
        'arg_name': 'phone_id',
        'phone_type': 'yandex',
        'transform': 'replace_phone_to_phone_id',
    },
}


async def fill_experiments(taxi_exp_client, experiment_name):
    data = experiment.generate(
        experiment_name,
        match_predicate=(
            experiment.allof_predicate(
                [
                    experiment.inset_predicate([1, 2, 3], set_elem_type='int'),
                    experiment.inset_predicate(
                        ['msk', 'spb'],
                        set_elem_type='string',
                        arg_name='city_id',
                    ),
                    experiment.gt_predicate(
                        '1.1.1',
                        arg_name='app_version',
                        arg_type='application_version',
                    ),
                    PREDICATE_WITH_PHONES,
                ],
            )
        ),
        applications=[
            {
                'name': 'android',
                'version_range': {'from': '3.14.0', 'to': '3.20.0'},
            },
        ],
        consumers=[{'name': 'test_consumer'}],
        owners=[],
        watchers=['another_login', 'first-login'],
        trait_tags=['test_1', 'test_2'],
        st_tickets=['TAXIEXP-228'],
    )

    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': experiment_name},
        json=data,
    )
    assert response.status == 200, await response.text()

    # update experiment
    data['description'] = 'Привет, Мир'
    data['match']['predicate'] = experiment.allof_predicate(
        [
            experiment.inset_predicate([1, 2, 3], set_elem_type='int'),
            experiment.inset_predicate(
                ['msk', 'spb'], set_elem_type='string', arg_name='city_id',
            ),
            experiment.gt_predicate(
                '1.1.1',
                arg_name='app_version',
                arg_type='application_version',
            ),
            UPDATED_PREDICATE_WITH_PHONES,
        ],
    )
    data['trait_tags'] = ['test_2']
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': experiment_name, 'last_modified_at': 1},
        json=data,
    )
    assert response.status == 200, await response.text()

    # get experiment
    response = await taxi_exp_client.get(
        'v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': experiment_name},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    assert body['watchers'] == ['another_login', 'first-login']
