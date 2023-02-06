def test_not_unloading(steps):
    steps.input.setup_agent_api_mock(ping=True, unloading_status={"state": "Success"})
    walle_id = steps.input.create_walle_task_not_unloading("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=True)
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_not_initiate_loading(steps):
    steps.input.setup_agent_api_mock(ping=True, loading_initiate_status={"state": "Success"})
    walle_id = steps.input.create_walle_task_not_initiate_loading("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=True)
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_not_wait_for_loading_complete(steps):
    steps.input.setup_agent_api_mock(ping=True, loading_status={"state": "Success"})
    walle_id = steps.input.create_walle_task_not_wait_for_loading_complete("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=True)
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_not_finalize_loading(steps):
    steps.input.setup_agent_api_mock(ping=True, loading_finalize_status={"state": "Success"})
    walle_id = steps.input.create_walle_task_not_finalize_loading("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=True)
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)
