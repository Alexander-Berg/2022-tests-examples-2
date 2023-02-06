import os

import sandbox.common.threading as th

global_lock = th.FLock(str(os.getgid()) + ".lock")


pytest_plugins = (
    "sandbox.tests.common.base",
    "sandbox.tests.common.config",
    "sandbox.tests.common.db",
    "sandbox.tests.common.network",
    "sandbox.tests.common.path",
    "sandbox.tests.common.service",
    "sandbox.tests.common.serviceapi",
    "sandbox.tests.common.utils",
    "sandbox.tests.common.tvm",
    "sandbox.tests.common.mds",
)
