from metrika.core.test_framework.steps.verification import verify


@verify
def test_status_ok(steps):
    steps.assert_that.host_status_is_success(steps.get_host_status())


@verify
def test_status_always_ok(steps):
    steps.setup_set_cluster("test_cluster_always_ok")

    steps.assert_that.host_status_is_success(steps.get_host_status())


@verify
def test_status_always_fail(steps):
    steps.setup_set_cluster("test_cluster_always_fail")

    steps.assert_that.host_status_is_fail(steps.get_host_status())


@verify
def test_status_step_timeout(steps):
    steps.setup_long_running_step(step_duration=30, step_timeout=10)

    steps.assert_that.host_status_is_fail_timeout(steps.get_host_status())


@verify
def test_status_ok_http(steps):
    steps.setup_http_server_reply_ok()
    steps.setup_http_step_expect_ok()

    steps.assert_that.host_status_is_success(steps.get_host_status())


@verify
def test_status_fail_http(steps):
    steps.setup_http_server_reply_service_unavailable()
    steps.setup_http_step_expect_ok()

    steps.assert_that.host_status_is_fail(steps.get_host_status())


@verify
def test_status_ok_http_text(steps):
    text = steps.setup_http_server_reply_ok()
    steps.setup_http_step_expect_text(text)

    steps.assert_that.host_status_is_success(steps.get_host_status())


@verify
def test_status_ok_http_json(steps):
    object = steps.setup_http_server_reply_pretend_clickhouse()
    steps.setup_http_step_expect_json(object)

    steps.assert_that.host_status_is_success(steps.get_host_status())
