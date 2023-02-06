from metrika.core.test_framework.steps.verification import verify

import metrika.admin.python.cms.lib.agent.steps.state as state


@verify
def test_load_initiate_status(steps):
    steps.assert_that.operation_is_not_started(steps.get_load_initiate_status())


@verify
def test_load_initiate_start(steps):
    steps.start_load_initiate()

    steps.wait_for_load_initiate_status(state.State.SUCCESS)

    steps.assert_that.operation_is_success(steps.get_load_initiate_status())


@verify
def test_load_initiate_inprogress(steps):
    steps.setup_long_running_operation_step(step_duration=30, step_timeout=40)

    steps.start_load_initiate()

    steps.wait_for_load_initiate_status(state.State.IN_PROGRESS)

    steps.assert_that.operation_is_in_progress(steps.get_load_initiate_status())


@verify
def test_load_initiate_cancel(steps):
    steps.setup_long_running_operation_step(step_duration=30, step_timeout=40)

    steps.start_load_initiate()

    steps.wait_for_load_initiate_status(state.State.IN_PROGRESS)

    steps.cancel_load_initiate()

    steps.assert_that.operation_is_not_started(steps.get_load_initiate_status())


@verify
def test_load_initiate_unload(steps):
    steps.start_load_initiate()

    steps.wait_for_load_initiate_status(state.State.SUCCESS)

    steps.start_unloading()

    steps.wait_for_unloading_status(state.State.IN_PROGRESS, state.State.SUCCESS)

    steps.assert_that.operation_is_not_started(steps.get_load_initiate_status())


@verify
def test_load_initiate_load_finalize(steps):
    steps.start_load_initiate()

    steps.wait_for_load_initiate_status(state.State.SUCCESS)

    steps.start_load_finalize()

    steps.wait_for_load_finalize_status(state.State.IN_PROGRESS, state.State.SUCCESS)

    steps.assert_that.operation_is_not_started(steps.get_load_initiate_status())


@verify
def test_load_initiate_inprogress_unload(steps):
    steps.setup_long_running_operation_step(step_duration=30, step_timeout=40)

    steps.start_load_initiate()

    steps.wait_for_load_initiate_status(state.State.IN_PROGRESS)

    steps.start_unloading()

    steps.wait_for_unloading_status(state.State.IN_PROGRESS)

    steps.assert_that.operation_is_not_started(steps.get_load_initiate_status())


@verify
def test_load_initiate_inprogress_load_finalize(steps):
    steps.setup_long_running_operation_step(step_duration=30, step_timeout=40)

    steps.start_load_initiate()

    steps.wait_for_load_initiate_status(state.State.IN_PROGRESS)

    steps.start_load_finalize()

    steps.wait_for_load_finalize_status(state.State.IN_PROGRESS)

    steps.assert_that.operation_is_not_started(steps.get_load_initiate_status())
