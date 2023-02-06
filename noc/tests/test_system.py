import modules.system as system


def test_make_cmd_call():
    assert "ping" in system.make_cmd_call(
        "/bin/echo ping"
    ), "make_cmd_call returned wrong output"


def test_exec_cmd_call():
    assert (
        system.exec_cmd_call("/bin/echo ping") == 0
    ), "exec_cmd_call return non zero exit code"
    assert system.exec_cmd_call(
        "/not_exist_dir/not_exist_file"
    ), "exec_cmd_call return wrong status code"
