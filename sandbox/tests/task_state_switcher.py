import pytest

import sdk2
import common.log
import common.rest
import common.types.task as ctt

import yasandbox.controller
from yasandbox.database import mapping


class TestTaskStateSwitcher(object):
    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__check_output_triggers(
        self, task_state_switcher, rest_session, rest_session_login, test_task_2, task_session, serviceq
    ):
        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
        }

        task_source = test_task_2(None, **task_params)
        task_target = test_task_2(None, **task_params)

        task_session(rest_session, task_source.id, login=rest_session_login)
        task_source.current = task_source
        with common.rest.DispatchedClient as dispatch:
            dispatch(lambda *_, **__: rest_session)
            sdk2.WaitOutput({task_target.id: ['result']}, False, 10800)(task_source)

        mapping.Task.objects(id=task_source.id).update(set__execution__status=ctt.Status.WAIT_OUT)
        for trigger_type in (mapping.TaskOutputTrigger, mapping.TimeTrigger):
            assert trigger_type.objects(source=task_source.id).count() == 1

        message, _ = task_state_switcher.check_wait_output()
        assert message == task_state_switcher._result_message(1, 0)

        task_session(rest_session, task_target.id, login=rest_session_login)
        task_target.current = task_target

        with common.rest.DispatchedClient as dispatch:
            dispatch(lambda *_, **__: rest_session)
            task_target.Parameters.result = 42

        message, _ = task_state_switcher.check_wait_output()
        assert message == task_state_switcher._result_message(1, 1)
        for trigger_type in (mapping.TaskOutputTrigger, mapping.TimeTrigger):
            assert trigger_type.objects(source=task_source.id).count() == 0

    def test__activate_task_trigger(
        self, task_state_switcher, rest_session, rest_session_login, test_task_2, task_session, serviceq
    ):
        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
        }

        with common.rest.DispatchedClient as dispatch:
            dispatch(lambda *_, **__: rest_session)
            task_source = test_task_2(None, **task_params)
            task_target = test_task_2(None, **task_params)

        task_session(rest_session, task_source.id, login=rest_session_login)
        task_source.current = task_source
        with common.rest.DispatchedClient as dispatch:
            dispatch(lambda *_, **__: rest_session)
            sdk2.WaitTask(task_target.id, [ctt.Status.SUCCESS], timeout=10800)(task_source)

        for trigger_type in (mapping.TaskStatusTrigger, mapping.TimeTrigger):
            assert trigger_type.objects(source=task_source.id).count() == 1
        mapping.Task.objects(id=task_source.id).update(set__execution__status=ctt.Status.STOPPING)

        message = task_state_switcher.check_wait_task()
        assert message == task_state_switcher._result_message(0, 0)

        tw = yasandbox.controller.TaskWrapper(yasandbox.controller.Task.get(task_source.id))
        tw.set_status(ctt.Status.WAIT_TASK, force=True)
        mapping.TaskStatusTrigger.objects(source=task_source.id).update(set__activated=True)

        mapping.Task.objects(id=task_target.id).update(set__execution__status=ctt.Status.SUCCESS)
        mapping.Audit(task_id=task_target.id, status=ctt.Status.SUCCESS).save()

        message = task_state_switcher.check_wait_task()
        assert message == task_state_switcher._result_message(1, 1)

        for trigger_type in (mapping.TaskStatusTrigger, mapping.TimeTrigger):
            assert trigger_type.objects(source=task_source.id).count() == 0

        # test that trigger must be activated before enqueuing the task
        with common.rest.DispatchedClient as dispatch:
            dispatch(lambda *_, **__: rest_session)
            task_target_2 = test_task_2(None, **task_params)
            sdk2.WaitTask(task_target_2.id, [ctt.Status.SUCCESS])(task_source)

        assert mapping.TaskStatusTrigger.objects(source=task_source.id).count() == 1

        mapping.Task.objects(id=task_target_2.id).update(set__execution__status=ctt.Status.SUCCESS)
        mapping.Audit(task_id=task_target_2.id, status=ctt.Status.SUCCESS).save()
        mapping.Task.objects(id=task_source.id).update(set__execution__status=ctt.Status.STOPPING)

        message = task_state_switcher.check_wait_task()
        assert message == task_state_switcher._result_message(0, 0)

        tw = yasandbox.controller.TaskWrapper(yasandbox.controller.Task.get(task_source.id))
        tw.set_status(ctt.Status.WAIT_TASK, force=True)
        mapping.TaskStatusTrigger.objects(source=task_source.id).update(set__activated=True)
        assert tw.status == ctt.Status.WAIT_TASK

        task_state_switcher._check_fired_wait_task_triggers()

        tw = yasandbox.controller.TaskWrapper(yasandbox.controller.Task.get(task_source.id))
        assert tw.status in (ctt.Status.ENQUEUING, ctt.Status.ENQUEUED)
