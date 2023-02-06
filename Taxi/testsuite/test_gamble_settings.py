import pytest


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS={
        'gamble_settings.initialize_with_experiments': 'false',
        'test.value': 'default',
    },
)
async def test_gamble_settings_experiments_off(
        rt_robot_execute, logistic_dispatcher_client, testpoint,
):
    @testpoint('gamble_settings')
    def gamble_settings(data):
        experiments = data['experiments']
        settings = data['settings']
        assert experiments == []
        assert settings['test.value'] == 'default'

    await rt_robot_execute('p2p_allocation')


LOGISTIC_DISPATCHER_SETTINGS_EXPERIMENTS_ON = {
    'gamble_settings.initialize_with_experiments': 'true',
    'test.value': 'default',
}


@pytest.mark.config(
    LOGISTIC_DISPATCHER_SETTINGS=LOGISTIC_DISPATCHER_SETTINGS_EXPERIMENTS_ON,
)
@pytest.mark.parametrize(
    'is_experiment, expected_experiments, expected_additional_settings',
    [
        (False, [], {}),
        (
            True,
            ['exp1', 'exp2'],
            {
                'test.value': 'value_exp1',
                'test.other_value': 'other_value_exp2',
            },
        ),
    ],
)
async def test_gamble_settings_experiments_on(
        rt_robot_execute,
        logistic_dispatcher_client,
        testpoint,
        mockserver,
        is_experiment,
        expected_experiments,
        expected_additional_settings,
):
    @testpoint('gamble_settings')
    def gamble_settings(data):
        experiments = data['experiments']
        assert set(experiments) == set(expected_experiments)

        settings = data['settings']
        expected_settings = {}
        expected_settings.update(LOGISTIC_DISPATCHER_SETTINGS_EXPERIMENTS_ON)
        expected_settings.update(expected_additional_settings)
        assert settings == expected_settings

    @mockserver.json_handler('/v1/experiments')
    def experiments(request):
        # see https://wiki.yandex-team.ru/taxi/backend/architecture/experiments3/http/#primeryispolzovanija
        r = request.json
        if (
                not is_experiment
                or r['consumer'] != 'logistic-dispatcher/gamble_settings'
        ):
            return {'items': [], 'version': 0}

        return {
            'items': [
                {'name': 'exp1', 'value': {'test.value': 'value_exp1'}},
                {
                    'name': 'exp2',
                    'value': {'test.other_value': 'other_value_exp2'},
                },
            ],
            'version': 0,
        }

    await rt_robot_execute('p2p_allocation')
