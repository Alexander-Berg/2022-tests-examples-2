from taxi_tests.plugins import experiments3 as exp3_cls

CONSUMER = 'docker_integration_tests/user_has'
CONSUMERS_LIST = [
    {'name': CONSUMER},
]
EXPERIMENT_NAME = 'select_user'

OTHER_PHONE_ID = '5714f45e98956f06baaae3d4'
YANDEX_PHONE_ID = '6d88f86917634f3ca2a4bcac'
TAXI_PHONE_ID = '67248fe852724412982f6668'


def test_experiment3_by_command(exp, experiments3_client):
    exp.add_tag('yandex_phone_id', YANDEX_PHONE_ID)
    exp.add_tag('taxi_phone_id', TAXI_PHONE_ID)

    exp.add_experiment(
        name=EXPERIMENT_NAME,
        consumers=CONSUMERS_LIST,
        default_value={'type': 'regular'},
        clauses=[
            {
                'title': 'taxi',
                'predicate': {
                    'type': 'user_has',
                    'init': {'tag': 'taxi_phone_id'},
                },
                'value': {'type': 'taxi'},
            },
            {
                'title': 'yandex',
                'predicate': {
                    'type': 'user_has',
                    'init': {'tag': 'yandex_phone_id'},
                },
                'value': {'type': 'yandex'},
            },
        ],
    )

    last_modified_at = exp.get_last_modified_at(EXPERIMENT_NAME)
    experiments3_client.waiting_roll_out(CONSUMER, last_modified_at)

    # check for taxi
    response = experiments3_client.get_values(
        consumer=CONSUMER,
        experiments_args=[
            exp3_cls.ExperimentsArg('phone_id', 'string', TAXI_PHONE_ID),
        ],
    )
    experiment_value = [
        item['value']['type']
        for item in response['items']
        if item['name'] == EXPERIMENT_NAME
    ]
    assert experiment_value
    assert experiment_value[0] == 'taxi'

    # check for yandex
    response = experiments3_client.get_values(
        consumer=CONSUMER,
        experiments_args=[
            exp3_cls.ExperimentsArg('phone_id', 'string', YANDEX_PHONE_ID),
        ],
    )
    experiment_value = [
        item['value']['type']
        for item in response['items']
        if item['name'] == EXPERIMENT_NAME
    ]
    assert experiment_value
    assert experiment_value[0] == 'yandex'

    # check for other
    response = experiments3_client.get_values(
        consumer=CONSUMER,
        experiments_args=[
            exp3_cls.ExperimentsArg('phone_id', 'string', OTHER_PHONE_ID),
        ],
    )
    experiment_value = [
        item['value']['type']
        for item in response['items']
        if item['name'] == EXPERIMENT_NAME
    ]
    assert experiment_value
    assert experiment_value[0] == 'regular'
