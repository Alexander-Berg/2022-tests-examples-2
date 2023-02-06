import yatest.common


def test_run_services_binary(services_binary):
    res = yatest.common.execute([services_binary, "list"], check_exit_code=False)
    assert res.exit_code == 0

    res = yatest.common.execute([services_binary, "run", "--name", "cleaner"], check_exit_code=False)
    assert res.exit_code == 1
    assert "env 'SANDBOX_CONFIG' should be defined" in res.std_err
