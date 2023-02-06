import metrika.admin.python.cms.lib.agent.steps.state as agent_state
import metrika.admin.python.cms.lib.fsm.states as fsm_states


def test_max_allowed_hosts(steps):
    steps.input.setup_cluster_api_for_mtcalclog()
    steps.input.setup_not_loaded_host("mtcalclog02kt", fsm_states.States.WAIT_FOR_LOADING_COMPLETE)
    steps.config.decider.max_unloaded_hosts = 1

    walle_id = steps.input.create_walle_task("mtcalclog01kt")

    steps.output.wait_until_audit(walle_id, success=False, reason="Maximum number of unloaded hosts reached")

    steps.assert_that.task_is_not_processed(walle_id)


def test_max_allowed_hosts_per_cluster(steps):
    steps.input.setup_cluster_api_for_mtcalclog()
    steps.input.setup_not_loaded_host("mtcalclog02kt", fsm_states.States.WAIT_FOR_LOADING_COMPLETE)
    steps.config.decider.max_unloaded_hosts = 2
    steps.config.decider.mtcalclog.testing.max_unloaded_hosts = 1

    walle_id = steps.input.create_walle_task("mtcalclog01kt")

    steps.output.wait_until_audit(walle_id, success=False, reason="Maximum number of unloaded hosts in cluster reached")

    steps.assert_that.task_is_not_processed(walle_id)


def test_disabled(steps):
    steps.input.setup_cluster_api_for_mtcalclog()
    steps.config.decider.mtcalclog.testing.enabled = False

    walle_id = steps.input.create_walle_task("mtcalclog01kt")

    steps.output.wait_until_transition(walle_id, fsm_states.States.MAKING_DECISION, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION)
    steps.output.wait_until_audit(walle_id, message="Decider disabled")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_ok_decision(steps):
    steps.input.setup_cluster_api_for_mtcalclog()
    steps.input.setup_not_loaded_host("mtcalclog02kt", fsm_states.States.WAIT_FOR_LOADING_COMPLETE)
    steps.config.decider.max_unloaded_hosts = 2
    steps.config.decider.mtcalclog.testing.max_unloaded_hosts = 2

    walle_id = steps.input.create_walle_task("mtcalclog01kt")

    steps.output.wait_until_audit(walle_id, message="Positive decision was made")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_max_allowed_hosts_per_cluster_duty(steps):
    steps.input.setup_cluster_api_for_mtcalclog()
    steps.input.setup_not_loaded_host("mtcalclog02kt", fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD)
    steps.config.decider.max_unloaded_hosts = 2
    steps.config.decider.mtcalclog.testing.max_unloaded_hosts = 1
    steps.input.setup_agent_api_mock(ping=True, host_status={"state": agent_state.State.SUCCESS, "reason": "Host is finally ready"})

    walle_id = steps.input.create_walle_task("mtcalclog02kt")

    steps.output.wait_until_audit(walle_id, success=False, reason="Maximum number of unloaded hosts in cluster reached")

    steps.assert_that.task_is_not_processed(walle_id)


def test_max_allowed_tasks_per_host_wait_for_loading(steps):
    steps.input.setup_cluster_api_for_mtcalclog()
    steps.input.setup_not_loaded_host("mtcalclog02kt", fsm_states.States.WAIT_FOR_LOADING_COMPLETE)
    steps.config.decider.max_unloaded_hosts = 1
    steps.config.decider.mtcmsstand.testing.max_unloaded_hosts = 1
    steps.config.decider.mtcmsstand.testing.max_active_tasks_per_host = 1

    walle_id = steps.input.create_walle_task("mtcalclog02kt")

    steps.output.wait_until_audit(walle_id, success=False, reason="Maximum number of unloaded tasks per host reached")

    steps.assert_that.task_is_not_processed(walle_id)
