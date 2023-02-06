"""
Модуль с тестами, которые должны выполняться глобально для всех сервисов
разом (а не посервисно)
"""
import sources_root
from dmp_suite.replication.tasks import streaming
from dmp_suite.task import base as task_base


def test_replication_streaming_destinations_are_unique(
        all_services_pythonpath,
):
    """
    Каждый EXT destination репликации может использоваться только одним таском
    """
    seen_destinations = set()
    duplicates = set()
    with all_services_pythonpath():
        for service_name in sources_root.ETL_SERVICES:
            task_bounds = task_base.collect_tasks(service_name)

            for tb in task_bounds:
                task = tb.task

                if not isinstance(task, streaming.OdsStreamingTask):
                    continue

                destination = task._replication_destination.name

                if destination in seen_destinations:
                    duplicates.add(destination)
                else:
                    seen_destinations.add(destination)

    assert not duplicates, (
        f'All streaming tasks must have unique destinations. '
        f'Found multiple usages: {duplicates}'
    )
