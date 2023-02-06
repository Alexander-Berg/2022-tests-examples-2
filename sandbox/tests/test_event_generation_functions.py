import pytest
import mock
import datetime

from release_machine.common_proto import events_pb2
from sandbox.projects.release_machine import events as release_machine_events


class SandboxTaskMock:

    server = mock.MagicMock()
    _sdk_server = mock.MagicMock()
    current = mock.MagicMock()
    log_resource = mock.MagicMock()

    class Context:
        pass

    class Parameters:
        component_name = "test_component"

    def __init__(self, *args, **kwargs):
        pass

    @property
    def id(self):
        return 1234567890

    @property
    def type(self):
        return "TEST_TASK_TYPE"

    @property
    def author(self):
        return "tester"

    @property
    def owner(self):
        return "TEST"

    @property
    def status(self):
        return "SUCCESS"

    @property
    def host(self):
        return "a.b.c.de"

    @property
    def created(self):
        return datetime.datetime(2021, 4, 30, 13, 32, 9, 521416, tzinfo=datetime.timezone.utc)

    @property
    def updated(self):
        return datetime.datetime(2021, 4, 30, 14, 32, 9, 521416, tzinfo=datetime.timezone.utc)

    @property
    def info(self):
        return "info"


@pytest.fixture(scope="module")
def sandbox_task_obj():
    return SandboxTaskMock()


@pytest.fixture
def event_time_utc_iso():
    return "2021-04-30T14:32:09.521416Z"


def test_get_task_event_general_data(sandbox_task_obj):

    gd = release_machine_events.get_task_event_general_data(
        task_obj=sandbox_task_obj,
        hash_items=("bun", "burger", "cheese", "tomato", "bun"),
    )

    assert gd.hash
    assert gd.component_name == sandbox_task_obj.Parameters.component_name
    assert gd.referrer


def test_get_task_event_task_data(sandbox_task_obj, event_time_utc_iso):

    td = release_machine_events.get_task_event_task_data(
        task_obj=sandbox_task_obj,
        event_time_utc_iso=event_time_utc_iso,
    )

    assert td.task_id == sandbox_task_obj.id
    assert td.status == getattr(events_pb2.EventSandboxTaskData.TaskStatus, sandbox_task_obj.status)
    assert td.created_at == sandbox_task_obj.created.isoformat()
    assert td.updated_at == event_time_utc_iso


def test_get_task_event_task_data__custom_status(sandbox_task_obj, event_time_utc_iso):
    custom_status = "FAILURE"

    td = release_machine_events.get_task_event_task_data(
        task_obj=sandbox_task_obj,
        event_time_utc_iso=event_time_utc_iso,
        status=custom_status,
    )

    assert td.task_id == sandbox_task_obj.id
    assert td.status == getattr(events_pb2.EventSandboxTaskData.TaskStatus, custom_status)
    assert td.created_at == sandbox_task_obj.created.isoformat()
    assert td.updated_at == event_time_utc_iso
