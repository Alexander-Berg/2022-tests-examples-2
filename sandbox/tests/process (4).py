import os
import logging

from sandbox import sdk2


class TestProcessHelper(object):
    def test__process_log__fd_leakage(self):
        prepre_fds = os.pipe()
        map(os.close, prepre_fds)
        with sdk2.helpers.ProcessLog(None, logger=logging.getLogger("test")) as pl:
            # instantiate pipes
            _ = pl.stdout, pl.stderr  # noqa
            pre_fds = os.pipe()
            map(os.close, pre_fds)
            for i in xrange(10):
                sdk2.helpers.subprocess.Popen("echo", shell=True, stdout=pl.stdout, stderr=pl.stderr).wait()
                post_fds = os.pipe()
                map(os.close, post_fds)
                assert pre_fds == post_fds
        postpost_fds = os.pipe()
        map(os.close, postpost_fds)
        assert prepre_fds == postpost_fds
