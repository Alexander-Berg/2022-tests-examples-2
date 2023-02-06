# coding=utf-8

from sandbox import sdk2


def make_test_params():
    class TestParameters(sdk2.Parameters):
        with sdk2.parameters.Group("Дополнительные параметры тестов") as test_params:
            test_target_host = sdk2.parameters.String("Хост для запуска тестов", required=False)
            test_base_host = sdk2.parameters.String("Хост эталон", required=False)

            with sdk2.parameters.String("Окружение тестирования") as test_env:
                test_env.values['testing'] = test_env.Value('testing', default=True)
                test_env.values['prestable'] = test_env.Value('prestable')
                test_env.values['production'] = test_env.Value('production')

            test_testpalm = sdk2.parameters.Bool("Использовать тестпалм")

    return TestParameters
