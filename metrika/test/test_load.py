import metrika.admin.python.cms.lib.agent.steps.state as agent_state
import metrika.admin.python.cms.lib.fsm.states as fsm_states


def test_load_bypass(steps):
    steps.input.setup_walle_host_status_ready()
    walle_id = steps.input.create_walle_task_load("shady-host", bypass=True)

    steps.output.wait_until_transition(walle_id, fsm_states.States.INITIATE_LOADING, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_load_many_hosts(steps):
    steps.input.setup_walle_host_status_ready()
    walle_id = steps.input.create_walle_task_load("shady-host", "cloudy-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.INITIATE_LOADING, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_too_old_task(steps):
    walle_id = steps.input.create_walle_task_load_in_past("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.INITIATE_LOADING, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_no_ping(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=False)

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=False, reason="Ping failed, but Wall-E returned host. Will try later.")

    steps.assert_that.task_is_not_processed(walle_id)


def test_loading_failed(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, host_status={"state": agent_state.State.FAIL}, loading_initiate_status={"state": agent_state.State.FAIL})

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_loading_started()
    steps.output.wait_until_audit(walle_id, success=False, reason="Initiate loading operation failed. Will try later.")

    steps.assert_that.task_is_not_processed(walle_id)


def test_loading_timeout(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, host_status={"state": agent_state.State.FAIL}, loading_initiate_status={"state": agent_state.State.IN_PROGRESS})

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_loading_started()
    steps.output.wait_until_audit(walle_id, success=False, reason="Initiate loading operation timed out. Will try later.")

    steps.assert_that.task_is_not_processed(walle_id)


def test_load_initiate_walle_not_ready(steps):
    steps.input.setup_walle_host_status_not_ready()
    steps.input.setup_agent_api_mock(ping=True)

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.INITIATE_LOADING, fsm_states.States.COMPLETED)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_load_initiate_walle_switching(steps):
    steps.input.setup_walle_host_status_not_ready_yet()

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=False, reason="Host status not final. Will try later.")

    steps.assert_that.task_is_not_processed(walle_id)


def test_load_initiate_wait(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, loading_initiate_status={"state": agent_state.State.SUCCESS})

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.INITIATE_LOADING, fsm_states.States.WAIT_FOR_LOADING_COMPLETE)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_load_initiate_retry_fail(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, loading_initiate_status={"state": agent_state.State.FAIL})

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=False, reason="Initiate loading operation failed. Will try later.")

    steps.assert_that.task_is_not_processed(walle_id)


def test_load_initiate_retry_fail_ping(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=False)

    walle_id = steps.input.create_walle_task_load("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=False, reason="Ping failed, but Wall-E returned host. Will try later.")

    steps.assert_that.task_is_not_processed(walle_id)


def test_wait_for_loading_loading_finalize(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, loading_status={"state": agent_state.State.SUCCESS})

    walle_id = steps.input.create_walle_task_load_wait("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.WAIT_FOR_LOADING_COMPLETE, fsm_states.States.FINALIZE_LOADING)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_wait_for_loading_retry(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, loading_status={"state": agent_state.State.IN_PROGRESS})

    walle_id = steps.input.create_walle_task_load_wait("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing")

    steps.assert_that.task_is_not_processed(walle_id)


def test_wait_for_loading_fail(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=False)

    walle_id = steps.input.create_walle_task_load_wait("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.WAIT_FOR_LOADING_COMPLETE, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_loading_finalize_failed(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, host_status={"state": agent_state.State.FAIL}, loading_finalize_status={"state": agent_state.State.SUCCESS})

    walle_id = steps.input.create_walle_task_load_finalize("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.FINALIZE_LOADING, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_loading_finalize_success(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, host_status={"state": agent_state.State.SUCCESS}, loading_finalize_status={"state": agent_state.State.SUCCESS})

    walle_id = steps.input.create_walle_task_load_finalize("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.FINALIZE_LOADING, fsm_states.States.COMPLETED)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_loading_finalize_retry(steps):
    steps.input.setup_walle_host_status_ready()
    steps.input.setup_agent_api_mock(ping=True, loading_finalize_status={"state": agent_state.State.FAIL})

    walle_id = steps.input.create_walle_task_load_finalize("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=False, reason="Finalize loading operation failed. Will try later.")

    steps.assert_that.task_is_not_processed(walle_id)
