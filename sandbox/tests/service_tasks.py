from __future__ import absolute_import

from sandbox import sdk2

from sandbox.projects.sandbox import remote_copy_resource


def _is_service_task(task_cls):
    return (
        issubclass(task_cls, sdk2.ServiceTask) or
        not issubclass(task_cls, sdk2.Task) and getattr(task_cls, "SERVICE", None)
    )


def test__service_tasks(project_types):
    for task_type, task_location in project_types.iteritems():
        service = _is_service_task(task_location.cls) and \
            not issubclass(task_location.cls, remote_copy_resource.RemoteCopyResource)
        assert not service or task_type in _ALLOWED_SERVICE_TASKS, (
            "Task class {} cannot be service. Use `sdk2.Task` as base task class. "
            "All service tasks should be approved by sandbox team.".format(task_type)
        )


_ALLOWED_SERVICE_TASKS = [
    "BACKUP_RESOURCE_2",
    "BACKUP_STORAGE_METADATA",
    "BUILD_SANDBOX",
    "BUILD_SANDBOX_DOCS",
    "BUILD_SANDBOX_TASKS",
    "BUNDLE_ARCADIA_HG_REPOSITORY",
    "ENSURE_RESOURCES_REDUNDANCY",
    "PARSE_SANDBOX_API_LOGS",
    "PARSE_SANDBOX_XMLRPC_LOGS",
    "REMOTE_COPY_RESOURCE_2",
    "SERVICE_CLEANUP_PUBLIC_MONGO",
    "SERVICE_MONGO_BACKUP",
    "SERVICE_MONGO_BACKUPER",
    "SERVICE_MONGO_RESTORE",
    "SERVICE_MONGO_SHARD_BACKUPER",
    "SERVICE_SANDBOX_OUTDATED_TASKS",
    "TASK_SCHEDULE_CHECK",
    "TEST_TASK",
    "TEST_TASK_2",
    "UNIT_TEST",
]
