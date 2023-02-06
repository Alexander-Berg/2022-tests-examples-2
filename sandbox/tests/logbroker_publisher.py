import mock

from sandbox.services.modules import logbroker_publisher
from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.controller import task as task_controller
import sandbox.common.types.task as ctt


class TestLogbrokerPublisher(object):
    def test__success(self, mongo_uri):
        mapping.ensure_connection(mongo_uri)

        task = self.__create_task()
        assert mapping.Task.objects().with_id(task.id)

        task = self.__change_status(task, ctt.Status.ASSIGNED)
        task = self.__change_status(task, ctt.Status.SUCCESS)
        events = mapping.TaskStatusEvent.objects(task_id=task.id)
        assert len(events) == 2
        assert events[0].status == ctt.Status.ASSIGNED
        assert events[1].status == ctt.Status.SUCCESS

        sender_mock = mock.MagicMock()
        publisher = logbroker_publisher.LogbrokerPublisher(sender_mock)
        publisher.tick()
        cnt = mapping.TaskStatusEvent.objects().count()
        assert cnt == 0

    def test__sending_failed(self, mongo_uri):
        mapping.ensure_connection(mongo_uri)

        task = self.__create_task()
        assert mapping.Task.objects().with_id(task.id)

        task = self.__change_status(task, ctt.Status.ASSIGNED)
        task = self.__change_status(task, ctt.Status.SUCCESS)
        events = mapping.TaskStatusEvent.objects(task_id=task.id)
        assert len(events) == 2

        sender_mock = mock.MagicMock()
        sender_mock.send_async = mock.MagicMock(side_effect=ValueError)

        publisher = logbroker_publisher.LogbrokerPublisher(sender_mock)
        publisher.tick()
        # assert events are still in the DB
        events = mapping.TaskStatusEvent.objects(task_id=task.id)
        assert len(events) == 2

    @staticmethod
    def __create_task():
        task = mapping.Task()
        task.host = "host"
        task.author = task.owner = "unspecified-author"
        task.type = "TEST_TASK_2"
        wrapper = task_controller.TaskWrapper(task)
        wrapper.create()
        return task

    @staticmethod
    def __change_status(task, status):
        task_controller.Task.set_status(task, status, force=True)
        task = mapping.Task.objects.with_id(task.id)
        return task
