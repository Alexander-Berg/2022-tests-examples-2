from taxi_tests.plugins import experiments3 as exp3_cls


CONSUMER = 'docker_integration_tests/file_upload'

CONSUMERS = [
    {'name': CONSUMER},
]

CONTENT = (
    b"""000
0001
+79031520359"""
)
CONTENT_V2 = (
    b"""000
0001
+79031520359
+79031520355"""
)

ALWAYS_PASS_CLAUSE_1 = {
    'title': 'default', 'predicate': {'type': 'true'}, 'value': 1,
}
ALWAYS_PASS_CLAUSE_2 = {
    'title': 'default', 'predicate': {'type': 'true'}, 'value': 2,
}
ALWAYS_PASS_CLAUSE_3 = {
    'title': 'default', 'predicate': {'type': 'true'}, 'value': 3,
}

PASS_PHONE_NUMBER = '+79031520355'
FAIL_PHONE_NUMBER = '+11111'


def test_adding_file_in_experiment3(exp, experiments3_client):
    # create experiment without files
    exp.add_consumer(CONSUMER)
    experiment_name = exp.add_experiment(
        consumers=CONSUMERS,
        clauses=[ALWAYS_PASS_CLAUSE_1],
    )
    last_modified_at = exp.get_last_modified_at(experiment_name)

    # checking that the rolled-out experiment is works
    data = experiments3_client.waiting_roll_out(
        CONSUMER, last_modified_at,
    )
    expected_pass_answer = {
        'name': experiment_name, 'value': ALWAYS_PASS_CLAUSE_1['value'],
    }
    assert any((
        item == expected_pass_answer
        for item in data['items']
    ))

    # upload file
    file_id = exp.add_or_update_file(CONTENT, experiment=experiment_name)

    # update experiment
    exp.update_experiment(
        experiment_name,
        last_modified_at,
        consumers=CONSUMERS,
        match_predicate={
            'type': 'in_file',
            'init': {
                'file': file_id,
                'arg_name': 'phone_number',
                'set_elem_type': 'string',
            },
        },
        clauses=[ALWAYS_PASS_CLAUSE_2],
    )
    last_modified_at = exp.get_last_modified_at(experiment_name)

    # checking that the rolled-out experiment don't works for +79031520355
    data = experiments3_client.waiting_roll_out(
        CONSUMER, last_modified_at,
        experiments_args=[
            exp3_cls.ExperimentsArg(
                'phone_number',
                'string',
                PASS_PHONE_NUMBER,
            ),
        ],
    )
    assert not any((
        item['name'] == experiment_name
        for item in data['items']
    ))

    # upload new file version
    file_id_v2 = exp.add_or_update_file(CONTENT_V2, experiment=experiment_name)

    # update experiment with new file version
    exp.update_experiment(
        experiment_name,
        last_modified_at,
        consumers=CONSUMERS,
        match_predicate={
            'type': 'in_file',
            'init': {
                'file': file_id_v2,
                'arg_name': 'phone_number',
                'set_elem_type': 'string',
            },
        },
        clauses=[ALWAYS_PASS_CLAUSE_3],
    )
    last_modified_at = exp.get_last_modified_at(experiment_name)

    # checking that the rolled-out experiment is works for +79031520355
    data = experiments3_client.waiting_roll_out(
        CONSUMER, last_modified_at,
        experiments_args=[
            exp3_cls.ExperimentsArg(
                'phone_number',
                'string',
                PASS_PHONE_NUMBER,
            ),
        ],
    )
    expected_pass_answer = {
        'name': experiment_name, 'value': ALWAYS_PASS_CLAUSE_3['value'],
    }
    assert any((
        item == expected_pass_answer
        for item in data['items']
    ))

    # checking that the rolled-out experiment is don't works for other user
    data = experiments3_client.get_values(
        consumer=CONSUMER,
        experiments_args=[
            exp3_cls.ExperimentsArg(
                'phone_number',
                'string',
                FAIL_PHONE_NUMBER,
            ),
        ],
    )
    assert all((
        item != expected_pass_answer
        for item in data['items']
    ))
