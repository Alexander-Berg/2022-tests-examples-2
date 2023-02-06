import metrika.admin.python.cms.lib.fsm.states as fsm_states


def test_skip_load_unload(steps):
    steps.setup_auto_full()

    steps.ping_all()

    walle_id = steps.walle_create_task(action="temporary-unreachable")

    steps.input.wait_for_status(walle_id, fsm_states.States.OK_WAIT_FOR_WALLE_DELETE)

    steps.walle_delete_task(walle_id)

    steps.input.wait_for_status(walle_id, fsm_states.States.COMPLETED)

    steps.verify_audit(
        walle_id,
        [
            {'message': 'Task created by Wall-E', 'source_state': fsm_states.States.INITIAL, 'target_state': fsm_states.States.MAKING_DECISION, 'success': True},
            {'message': 'Task for judge has been enqueued', 'subject': 'cms frontend hook', 'success': True},
            {'message': 'Start processing', 'success': True},
            {'message': 'Lock acquired', 'success': True},
            {'message': 'Allow temporary unreachable', 'reason': 'Host is in allowlist', 'success': True},
            {'message': 'Positive decision', 'source_state': fsm_states.States.MAKING_DECISION, 'target_state': fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD, 'success': True},
            {
                'message': 'Skip unload for temporary-unreachable is allowed in settings', 'source_state': fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD,
                'target_state': fsm_states.States.WAIT_FOR_APPROVAL_OK, 'subject': 'cms frontend hook', 'success': True
            },
            {
                'message': 'Auto approval of positive decision allowed in settings', 'source_state': fsm_states.States.WAIT_FOR_APPROVAL_OK, 'subject': 'cms frontend hook',
                'target_state': fsm_states.States.OK_WAIT_FOR_WALLE_DELETE, 'success': True
            },
            {'message': 'Finish processing', 'success': True},
            {'message': 'Wall-E deleted ok task', 'source_state': fsm_states.States.OK_WAIT_FOR_WALLE_DELETE, 'success': True, 'target_state': fsm_states.States.INITIATE_LOADING},
            {
                'message': 'Skip load for temporary-unreachable is allowed in settings', 'source_state': fsm_states.States.INITIATE_LOADING,
                'target_state': fsm_states.States.COMPLETED, 'subject': 'cms frontend hook', 'success': True
            },
        ]
    )
