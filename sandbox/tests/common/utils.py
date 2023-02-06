import os
import uuid
import signal
import socket
import getpass
import logging
import datetime
import functools

import six
import pytest

if six.PY2:
    import subprocess32 as sp
else:
    import subprocess as sp

from sandbox.common import system

import sandbox.tests.common as tests_common


@pytest.fixture(scope="session")
def work_id(request):
    if hasattr(request.config, "slaveinput"):
        ms_type = request.config.slaveinput["slaveid"]
    else:
        ms_type = "master"
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pid = os.getpid()

    return "{}_{}_{}".format(ms_type, now, pid)


@pytest.fixture(scope="session")
def user():
    return getpass.getuser()


@pytest.fixture(scope="session")
def host():
    return "localhost"


def hostname():
    return socket.gethostname().split(".")[0]


def _run_daemon_yatest(request, args, env=None):
    import yatest.common
    proxy = yatest.common.execute(args, env=env, wait=False)

    def stop_daemon():
        try:
            proxy.process.kill()
            proxy.wait(check_exit_code=False)
        except OSError:
            pass

    request.addfinalizer(stop_daemon)


def _run_daemon_subprocess(request, args, env=None):
    logging.debug("Running %s with env %s", str(args), str(env))

    proc = sp.Popen(args, env=env)

    def stop_daemon():
        try:
            proc.kill()
            proc.communicate()
        except OSError:
            pass

    request.addfinalizer(stop_daemon)


@pytest.fixture(scope="session")
def run_daemon(request):
    return functools.partial(
        _run_daemon_yatest if system.inside_the_binary() else _run_daemon_subprocess,
        request
    )


class ProcWrapper(object):
    """ Wrap subprocess.Popen and pretend it's skynet.services.procman.src.process.Proc """

    def __init__(self, parent_class, proc, tags, stdout, stderr):
        self.__parent = parent_class
        self.__proc = proc
        self.__tags = tags
        self.__stdout_path = stdout.name
        self.__stderr_path = stderr.name
        self.__fds = stdout.fileno(), stderr.fileno()

    @property
    def pid(self):
        return self.__proc.pid

    @property
    def tags(self):
        return self.__tags

    def close_fds(self):
        for fd in self.__fds:
            try:
                os.close(fd)
            except OSError:
                pass

    def poll(self):
        return self.__proc.poll()

    @staticmethod
    def __read(path):
        try:
            with open(path, "r") as fd:
                return fd.read()
        except (TypeError, IOError):
            return ""

    def stdout(self):
        return self.__read(self.__stdout_path)

    def stderr(self):
        return self.__read(self.__stderr_path)

    def signal(self, sig):
        try:
            os.kill(self.__proc.pid, sig)
            if sig in (signal.SIGKILL, signal.SIGTERM):
                self.__parent.discard(self)
        except OSError:
            self.__parent.logger.exception("Failed to send %d to pid %d", sig, self.__proc.pid)

    def kill(self):
        self.signal(signal.SIGKILL)

    def terminate(self):
        self.signal(signal.SIGTERM)

    def __int__(self):
        return self.__proc.pid


class TaskSubproc(object):
    """ Run processes via subprocess.Popen instead of ProcMan (SANDBOX-4196) """

    _processes = {}
    logger = logging.getLogger("client")

    @classmethod
    def discard(cls, proc):
        proc.close_fds()
        if proc.pid in cls._processes:
            del cls._processes[proc.pid]

    def __repr__(self):
        return "<{}: pid={}>".format(self.__class__.__name__, self.proc and self.pid)

    def __nonzero__(self):
        return bool(self.proc)

    def __init__(self, proc):
        self.__proc = proc

    def __getstate__(self):
        return {"pid": self.proc and self.pid}

    def __setstate__(self, value):
        self.__init__(self._processes.get(value["pid"]))

    # noinspection PyUnusedLocal
    @classmethod
    def create(cls, cmd, env=None, tags=(), *_, **__):
        if env is None:
            env = os.environ.copy()
        cls.logger.debug("Executing command %r via subprocess.Popen", cmd)

        uid = uuid.uuid4().hex
        out, err = [open("/tmp/executor_{}.{}".format(uid, type_), "w") for type_ in ("out", "err")]
        process = sp.Popen(cmd, env=env, close_fds=True, stdout=out, stderr=err)
        wrapper = ProcWrapper(cls, process, set(tags), out, err)
        cls._processes[process.pid] = wrapper
        return cls(wrapper)

    @property
    def proc(self):
        return self.__proc

    @classmethod
    def find_by_tags(cls, tags_):
        return [wrapper for wrapper in cls._processes.values() if set(tags_) & wrapper.tags]

    @property
    def status(self):
        done = self.proc.poll()
        if done is not None:
            self.discard(self.proc)
        return done is not None

    @property
    def pid(self):
        return self.proc.pid


def call_once(request, tests_common_path, func):
    """
        Function for calling function inside fixture once per session (with regard of xdist plugin)

        :param request: FixtureRequest object
        :param tests_common_path: path to common tests directory
        :param func: function to call
    """
    pid = str(os.getpid())
    with tests_common.global_lock:
        lock_file = os.path.join(tests_common_path, "fixture_{}.lock".format(request.fixturename))
        with open(lock_file, "a+") as f:
            pids = f.read().strip().split()
        with open(lock_file, "w+") as f:
            new_pids = set(pids) | {pid}
            f.write(" ".join(new_pids))
        if not pids:
            func()

        def finalizer():
            with tests_common.global_lock:
                with open(lock_file) as f:
                    pids = set(f.read().strip().split())
                if pids and pid in pids:
                    pids.remove(pid)
                    with open(lock_file, "w+") as f:
                        f.write(" ".join(pids))
        request.addfinalizer(finalizer)
