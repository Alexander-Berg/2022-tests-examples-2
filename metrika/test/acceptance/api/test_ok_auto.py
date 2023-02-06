import metrika.admin.python.cms.lib.fsm.states as fsm_states


def test_ok_auto(steps):
    steps.setup_manual()

    steps.ping_all()

    walle_id = steps.walle_create_task_auto()

    steps.input.wait_for_status(walle_id, fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD)

    steps.operator_approve_unloading(walle_id)

    steps.input.wait_for_status(walle_id, fsm_states.States.WAIT_FOR_APPROVAL_OK)

    steps.operator_approve_ok_walle_task(walle_id)

    steps.input.wait_for_status(walle_id, fsm_states.States.OK_WAIT_FOR_WALLE_DELETE)

    steps.walle_delete_task(walle_id)

    steps.input.wait_for_status(walle_id, fsm_states.States.COMPLETED)

    steps.verify_audit(
        walle_id,
        [
            {'message': 'Task created by Wall-E', 'source_state': fsm_states.States.INITIAL, 'target_state': fsm_states.States.MAKING_DECISION, 'success': True},
            {'message': 'Task for judge has been enqueued', 'subject': 'cms frontend hook', 'success': True},
            {'message': 'Positive decision', 'source_state': fsm_states.States.MAKING_DECISION, 'target_state': fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD, 'success': True},
            {'message': 'allow unloading', 'source_state': fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD, 'target_state': fsm_states.States.UNLOADING, 'subject': 'operator', 'success': True},
            {'message': 'Unloading task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
            {'message': 'Unloading operation succeeded', 'source_state': fsm_states.States.UNLOADING, 'success': True, 'target_state': fsm_states.States.WAIT_FOR_APPROVAL_OK},
            {'message': 'manual approve', 'source_state': fsm_states.States.WAIT_FOR_APPROVAL_OK, 'subject': 'operator', 'success': True, 'target_state': fsm_states.States.OK_WAIT_FOR_WALLE_DELETE},
            {'message': 'Wall-E deleted ok task', 'source_state': fsm_states.States.OK_WAIT_FOR_WALLE_DELETE, 'success': True, 'target_state': fsm_states.States.INITIATE_LOADING},
            {'message': 'Initiate loading task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
            {'message': 'Initiate loading operation succeeded and host in good state.', 'source_state': fsm_states.States.INITIATE_LOADING, 'success': True,
             'target_state': fsm_states.States.WAIT_FOR_LOADING_COMPLETE},
            {'message': 'Wait for loading complete task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
            {'message': 'Wait for loading complete finished.', 'source_state': fsm_states.States.WAIT_FOR_LOADING_COMPLETE, 'success': True, 'target_state': fsm_states.States.FINALIZE_LOADING},
            {'message': 'Finalize loading task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
            {'message': 'Finalize loading operation succeeded', 'success': True},
            {'message': 'Host in good state after finalize loading succeeded', 'source_state': fsm_states.States.FINALIZE_LOADING, 'success': True, 'target_state': fsm_states.States.COMPLETED},
        ]
    )


def test_ok_auto_full(steps):
    steps.setup_auto_full()

    steps.ping_all()

    walle_id = steps.walle_create_task_auto()

    steps.input.wait_for_status(walle_id, fsm_states.States.OK_WAIT_FOR_WALLE_DELETE)

    steps.walle_delete_task(walle_id)

    steps.input.wait_for_status(walle_id, fsm_states.States.COMPLETED)

    steps.verify_audit(walle_id,
                       [
                           {'message': 'Task created by Wall-E', 'source_state': fsm_states.States.INITIAL, 'target_state': fsm_states.States.MAKING_DECISION, 'success': True},
                           {'message': 'Task for judge has been enqueued', 'subject': 'cms frontend hook', 'success': True},
                           {'message': 'Start processing', 'success': True},
                           {'message': 'Lock acquired', 'success': True},
                           {'message': '\'OK\' is the only option', 'subject': 'always OK decider', 'success': True},
                           {'message': 'Positive decision', 'source_state': fsm_states.States.MAKING_DECISION, 'target_state': fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD,
                            'success': True},
                           {'message': 'Auto unloading allowed in settings', 'source_state': fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD, 'target_state': fsm_states.States.UNLOADING,
                            'subject': 'cms frontend hook', 'success': True},
                           {'message': 'Unloading task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
                           {'message': 'Finish processing', 'success': True},
                           {'message': 'Start processing. Action: unload', 'success': True},
                           {'message': 'Lock acquired', 'success': True},
                           {'message': 'Unloading operation succeeded', 'source_state': fsm_states.States.UNLOADING, 'success': True, 'target_state': fsm_states.States.WAIT_FOR_APPROVAL_OK},
                           {'message': 'Auto approval of positive decision allowed in settings', 'source_state': fsm_states.States.WAIT_FOR_APPROVAL_OK, 'subject': 'cms frontend hook',
                            'success': True, 'target_state': fsm_states.States.OK_WAIT_FOR_WALLE_DELETE},
                           {'message': 'Finish processing', 'success': True},
                           {'message': 'Wall-E deleted ok task', 'source_state': fsm_states.States.OK_WAIT_FOR_WALLE_DELETE, 'success': True, 'target_state': fsm_states.States.INITIATE_LOADING},
                           {'message': 'Initiate loading task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
                           {'message': 'Start processing. Action: initiate_loading', 'success': True},
                           {'message': 'Lock acquired', 'success': True},
                           {'message': 'Initiate loading operation succeeded and host in good state.', 'source_state': fsm_states.States.INITIATE_LOADING, 'success': True,
                            'target_state': fsm_states.States.WAIT_FOR_LOADING_COMPLETE},
                           {'message': 'Wait for loading complete task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
                           {'message': 'Finish processing', 'success': True},
                           {'message': 'Start processing. Action: wait_for_loading_complete', 'success': True},
                           {'message': 'Lock acquired', 'success': True},
                           {'message': 'Wait for loading complete finished.', 'source_state': fsm_states.States.WAIT_FOR_LOADING_COMPLETE, 'success': True,
                            'target_state': fsm_states.States.FINALIZE_LOADING},
                           {'message': 'Finalize loading task for marshal has been enqueued', 'subject': 'cms frontend hook', 'success': True},
                           {'message': 'Finish processing', 'success': True},
                           {'message': 'Start processing. Action: finalize loading', 'reason': 'operation succeeded', 'success': True},
                           {'message': 'Lock acquired', 'success': True},
                           {'message': 'Finalize loading operation succeeded', 'success': True},
                           {'message': 'Host in good state after finalize loading succeeded', 'source_state': fsm_states.States.FINALIZE_LOADING, 'success': True,
                            'target_state': fsm_states.States.COMPLETED},
                           {'message': 'Finish processing', 'success': True}
                       ]
                       )
