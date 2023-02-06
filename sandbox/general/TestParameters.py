# coding=utf-8
from sandbox import sdk2


class TestParameters(sdk2.Task.Parameters):
    """
    Общие для launcher'а и runner'а параметры, в основном те, что пробрасываются из первого во второй
    """
    with sdk2.parameters.Group("Test parameters") as test_parameters_group:
        tests_pattern = sdk2.parameters.String("Шаблон тестов",
                                               description="Шаблон запуска JUnit-тестов (--tests)")
        output_dir_param_name = sdk2.parameters.String(
            "Параметр с выходным каталогом",
            description="Параметр, в который передаётся каталог,"
                        "в который должны быть записаны результаты тестов и прочие артефакты",
            default="junit.reports.dir")
        reports = sdk2.parameters.Dict(
            "Публикуемые отчёты",
            default={"Gradle Report": "reports/html/index.html"},
            description="ключ - название отчёта, значение - относительный путь к html-файлу отчёта."
                        "Путь отсчитывается относительно каталога, переданного в предыдущем параметре.")
        build_target = sdk2.parameters.List("Сборка",
                                            description="gradle задачи для сборки проекта с тестами",
                                            default=[])
        get_config_target = sdk2.parameters.List("Конфигурация",
                                                 description="gradle задачи для получения конфигурации",
                                                 default=[])
        run_target = sdk2.parameters.List("Запуск",
                                          description="gradle задачи для запуска тестов",
                                          default=[])
        report_target = sdk2.parameters.List("Отчёт",
                                             description="gradle задачи для генерации отчётов",
                                             default=[])
        execute_if_failed = sdk2.parameters.Bool("Execute all run steps", default=False)
        report_duration = sdk2.parameters.Integer("Report stage duration in seconds", required=True,
                                                  default_value=600)

    @staticmethod
    def get(task):
        return {
            TestParameters.tests_pattern.name: task.Parameters.tests_pattern,
            TestParameters.output_dir_param_name.name: task.Parameters.output_dir_param_name,
            TestParameters.reports.name: task.Parameters.reports,
            TestParameters.build_target.name: task.Parameters.build_target,
            TestParameters.get_config_target.name: task.Parameters.get_config_target,
            TestParameters.run_target.name: task.Parameters.run_target,
            TestParameters.report_target.name: task.Parameters.report_target,
            TestParameters.execute_if_failed.name: task.Parameters.execute_if_failed,
            TestParameters.report_duration.name: task.Parameters.report_duration,
        }
