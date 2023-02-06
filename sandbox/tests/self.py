import os

import sandbox.tests.common.utils as tests_utils


class TestClientSubproc(object):

    def test__single_proc(self):
        sp = tests_utils.TaskSubproc.create(["/bin/echo", "hello pytest"])
        assert sp.pid
        os.waitpid(sp.pid, 0)
        assert sp.status
        assert sp.proc.stdout().rstrip() == "hello pytest"

        sp = tests_utils.TaskSubproc.create(["/bin/sleep", "10s"])
        assert sp.pid in tests_utils.TaskSubproc._processes
        sp.proc.kill()
        assert sp.pid not in tests_utils.TaskSubproc._processes

    def test__multiple_proc(self):
        procs = [
            tests_utils.TaskSubproc.create(["/bin/echo", "hello pytest"])
            for _ in xrange(10)
        ]
        [os.waitpid(_.pid, 0) for _ in procs]
        assert len(tests_utils.TaskSubproc._processes) == len(procs)
        assert all(_.status for _ in procs)
        [_.proc.kill() for _ in procs]
        assert len(tests_utils.TaskSubproc._processes) == 0
