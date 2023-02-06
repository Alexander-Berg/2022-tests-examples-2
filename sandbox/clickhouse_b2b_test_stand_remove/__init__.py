# coding=utf-8
import logging
from sandbox.projects.metrika.java import metrika_java_test_stand_remove
from sandbox.projects.metrika.utils import base_metrika_task


@base_metrika_task.with_parents
class ClickHouseB2BTestStandRemove(metrika_java_test_stand_remove.MetrikaJavaTestStandRemove):
    """
    Удаление тестового стенда java демонов Метрики для приемки CH (то же самое + CaaS)
    """
    name = "CLICKHOUSE_B2B_TEST_STAND_REMOVE"

    class Parameters(metrika_java_test_stand_remove.MetrikaJavaTestStandRemove.Parameters):
        pass

    def on_execute(self):
        # тут нужно пройти по всем ДЦ и в каждом попробовать удалить
        for caas in self.maas_provider.get_caas_clients():
            try:
                caas.delete_all_instances_by_name(self.Parameters.stage_name)
            except:
                logging.exception("Ошибка при удалении инстанса в MaaS. Пропускаем.")
