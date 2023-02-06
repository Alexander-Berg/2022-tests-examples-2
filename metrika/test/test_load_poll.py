from metrika.core.test_framework.steps.verification import verify


@verify
def test_status_ok(steps):
    steps.assert_that.loading_status_is_success(steps.get_loading_status())


@verify
def test_status_always_ok(steps):
    steps.setup_set_cluster("test_cluster_always_ok")

    steps.assert_that.loading_status_is_success(steps.get_loading_status())


@verify
def test_status_always_fail(steps):
    steps.setup_set_cluster("test_cluster_always_fail")

    steps.assert_that.loading_status_is_fail(steps.get_loading_status())


@verify
def test_status_step_timeout(steps):
    steps.setup_long_running_operation_step(step_duration=30, step_timeout=10)

    steps.assert_that.loading_status_is_fail_timeout(steps.get_loading_status())
