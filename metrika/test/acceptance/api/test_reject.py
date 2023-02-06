import metrika.admin.python.cms.lib.fsm.states as fsm_states


def test_reject(steps):
    steps.setup_manual()

    steps.ping_all()

    walle_id = steps.walle_create_task()

    steps.input.wait_for_status(walle_id, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION)

    steps.operator_reject_walle_task(walle_id)

    steps.input.wait_for_status(walle_id, fsm_states.States.REJECT_WAIT_FOR_WALLE_DELETE)

    steps.walle_delete_task(walle_id)

    steps.input.wait_for_status(walle_id, fsm_states.States.COMPLETED)

    steps.verify_audit(
        walle_id,
        [
            {'message': 'Task created by Wall-E', 'source_state': fsm_states.States.INITIAL, 'target_state': fsm_states.States.MAKING_DECISION, 'success': True},
            {'message': 'Task for judge has been enqueued', 'subject': 'cms frontend hook', 'success': True},
            {'message': 'Unable to make decision', 'source_state': fsm_states.States.MAKING_DECISION, 'target_state': fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, 'success': True},
            {'message': 'manual decision', 'source_state': fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, 'target_state': fsm_states.States.REJECT_WAIT_FOR_WALLE_DELETE, 'success': True},
            {'message': 'Wall-E deleted rejected task', 'source_state': fsm_states.States.REJECT_WAIT_FOR_WALLE_DELETE, 'target_state': fsm_states.States.COMPLETED, 'success': True},
        ]
    )
