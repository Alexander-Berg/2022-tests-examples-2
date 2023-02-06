import metrika.admin.python.cms.lib.agent.steps.state as agent_state
import metrika.admin.python.cms.lib.fsm.states as fsm_states


def test_unload_many_hosts(steps):
    walle_id = steps.input.create_walle_task_unload("shady-host", "cloudy-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.UNLOADING, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_too_old_task(steps):
    walle_id = steps.input.create_walle_task_unload_in_past("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.UNLOADING, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_drowned_host(steps):
    steps.input.setup_agent_api_mock(ping=False)

    walle_id = steps.input.create_walle_task_unload("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.UNLOADING, fsm_states.States.WAIT_FOR_APPROVAL_OK)
    steps.output.wait_until_audit(walle_id, success=False, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_unloading_success(steps):
    steps.input.setup_agent_api_mock(ping=True, unloading_status={"state": "Success"})

    walle_id = steps.input.create_walle_task_unload("shady-host")

    steps.output.wait_until_unloading_started()
    steps.output.wait_until_transition(walle_id, fsm_states.States.UNLOADING, fsm_states.States.WAIT_FOR_APPROVAL_OK)
    steps.output.wait_until_audit(walle_id, success=True, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_unloading_failed(steps):
    steps.input.setup_agent_api_mock(ping=True, unloading_status={"state": agent_state.State.FAIL})

    walle_id = steps.input.create_walle_task_unload("shady-host")

    steps.output.wait_until_unloading_started()
    steps.output.wait_until_transition(walle_id, fsm_states.States.UNLOADING, fsm_states.States.WAIT_FOR_APPROVAL_OK)
    steps.output.wait_until_audit(walle_id, success=False, reason="Unloading operation failed. Consider host is drowned.")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_unloading_timeout(steps):
    steps.input.setup_agent_api_mock(ping=True, unloading_status={"state": agent_state.State.IN_PROGRESS})

    walle_id = steps.input.create_walle_task_unload("shady-host")

    steps.output.wait_until_unloading_started()
    steps.output.wait_until_transition(walle_id, fsm_states.States.UNLOADING, fsm_states.States.WAIT_FOR_APPROVAL_OK)
    steps.output.wait_until_audit(walle_id, success=False, reason="Unloading operation timed out. Consider host is drowned.")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_unloading_walle_unexpectedly_deleted_task(steps):
    steps.input.setup_agent_api_mock(ping=True, unloading_status={"state": agent_state.State.SUCCESS})

    walle_id = steps.input.create_walle_task_and_delete_before_unload("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)
