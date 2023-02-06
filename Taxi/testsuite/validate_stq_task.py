def validate_stq_task(
        task_name, mock_stq_agent, order_id, change_name, exists=True,
):
    tasks = mock_stq_agent.get_tasks(task_name)
    if not exists:
        assert len(tasks) == 0
        return
    assert len(tasks) == 1
    assert tasks[0].id == '(u\'{}\', u\'{}\')'.format(order_id, change_name)
    log_extra = tasks[0].args.pop(1)
    assert 'log_extra' in log_extra
    assert '_link' in log_extra['log_extra']
    assert tasks[0].args == [tasks[0].id, order_id, change_name]


def validate_process_change_stq_task(mock_stq_agent, order_id, change_name):
    validate_stq_task('process_change', mock_stq_agent, order_id, change_name)


def validate_notify_on_change_stq_task(
        mock_stq_agent, order_id, change_name, exists=True,
):
    validate_stq_task(
        'notify_on_change', mock_stq_agent, order_id, change_name, exists,
    )


def validate_process_update_stq_task(
        mock_stq_agent, order_id, change_name, exists=True,
):
    tasks = mock_stq_agent.get_tasks('process_update')
    if not exists:
        assert len(tasks) == 0
        return
    assert len(tasks) == 1
    assert tasks[0].id == '{}_{}'.format(order_id, change_name)
    assert tasks[0].kwargs['order_id'] == order_id
    assert tasks[0].kwargs['type'] == change_name
