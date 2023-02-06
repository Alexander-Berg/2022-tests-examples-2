import pytest
import uuid

from dmp_suite.maintenance.process_killer.queue.storage import KillQueueManager
from dmp_suite.maintenance.process_killer.queue.model import KillQueue, KillStatus


class TestKillQueueManager:
    @pytest.mark.slow
    def test_manager_base_flow(self):
        # в связи с тем, что сейчас таблица тестов одна для всех запускам, проверим все функции менеджера
        # на одной новой записи, последовательно проводя операции на ней

        run_info = str(uuid.uuid4())  # фейковый taxidwh_run_id
        etl_service = 'dmp_suite'
        # проверим, что  корректно создается запись в БД
        self._assert_create_item(etl_service, run_info)

        # проверим, что созданная запись присутствует в списке со статусом создана
        self._assert_created_items(etl_service, run_info)

        # проверим что изменяется статус записи на "performed"
        self._assert_update_status(etl_service, run_info, KillStatus.performed)

        # проверим, что созданная запись присутствует в списке со статусом "performed"
        self._assert_performed_items(etl_service, run_info)

        # переведем в статус success
        self._assert_update_status(etl_service, run_info, KillStatus.success)

    @staticmethod
    def _assert_create_item(etl_service, run_info):
        with KillQueueManager() as manager:
            manager.create(task_info=run_info, etl_service=etl_service)
            item = manager.get_by_task_info(etl_service, run_info)
            assert item
            assert item.status == KillStatus.created
            assert item.utc_created_dttm
            assert item.utc_updated_dttm
            assert item.etl_service == etl_service

    @staticmethod
    def _assert_created_items(etl_service, run_info):
        with KillQueueManager() as manager:
            item = manager.get_by_task_info(etl_service, run_info)
            items = list(manager.created_items(etl_service))
            assert item in items

    @staticmethod
    def _assert_update_status(etl_service, run_info, status):
        with KillQueueManager() as manager:
            item = manager.get_by_task_info(etl_service, run_info)
            assert item.status != status
            prev_upd = item.utc_updated_dttm
            manager.update_status(item, status)
            assert item.status == status
            assert item.utc_updated_dttm != prev_upd

    @staticmethod
    def _assert_performed_items(etl_service, run_info):
        with KillQueueManager() as manager:
            item = manager.get_by_task_info(etl_service, run_info)
            items = list(manager.performed_items(etl_service))
            assert item in items
