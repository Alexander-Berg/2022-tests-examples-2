import yatest.common as yacommon


def test_join_iter():
    cmd = [
        yacommon.binary_path("robot/lemur/tools/test_join_iter/test_join_iter")
    ]
    res = yacommon.process.execute(cmd, True)
    assert res.exit_code == 0, \
        "exit_code: %i\nstdout: %s\nstderr: %s" % \
            (res.exit_code, res.std_out, res.std_err)
