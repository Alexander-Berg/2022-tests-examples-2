import metrika.admin.python.cms.lib.fsm.states as fsm_states


def test_unsupported_action(steps):
    walle_id = steps.input.create_walle_task_invalid_action("shady-sands")

    steps.output.wait_until_transition(walle_id, source_state=fsm_states.States.UNLOADING, target_state=fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION)

    steps.output.wait_until_audit(walle_id, message="Unsupported action")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)
