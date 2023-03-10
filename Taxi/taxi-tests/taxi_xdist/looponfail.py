"""
    Implement -f aka looponfailing for py.test.

    NOTE that we try to avoid loading and depending on application modules
    within the controlling process (the one that starts repeatedly test
    processes) otherwise changes to source code can crash
    the controlling process which should best never happen.
"""

import sys

import execnet
import py
import pytest


def pytest_addoption(parser):
    group = parser.getgroup('taxi_xdist', 'distributed and subprocess testing')
    group._addoption(  # pylint: disable=protected-access
        '-f', '--looponfail',
        action='store_true', dest='looponfail', default=False,
        help='run tests in subprocess, wait for modified files '
             'and re-run failing test set until all pass.')


def pytest_cmdline_main(config):
    if config.getoption('looponfail'):
        usepdb = config.getoption('usepdb')  # a core option
        if usepdb:
            raise pytest.UsageError(
                '--pdb incompatible with --looponfail.')
        looponfail_main(config)
        return 2  # looponfail only can get stop with ctrl-C anyway
    return None


def looponfail_main(config):
    remotecontrol = RemoteControl(config)
    rootdirs = config.getini('looponfailroots')
    statrecorder = StatRecorder(rootdirs)
    try:
        while 1:
            remotecontrol.loop_once()
            if not remotecontrol.failures and remotecontrol.wasfailing:
                # the last failures passed, let's immediately rerun all
                continue
            repr_pytest_looponfailinfo(
                failreports=remotecontrol.failures,
                rootdirs=rootdirs)
            statrecorder.waitonchange(checkinterval=2.0)
    except KeyboardInterrupt:
        print()


class RemoteControl:
    def __init__(self, config):
        self.config = config
        self.wasfailing = None
        self.failures = []

    def trace(self, *args):
        if self.config.option.debug:
            msg = ' '.join([str(x) for x in args])
            py.builtin.print_('RemoteControl:', msg)

    @staticmethod
    def initgateway():
        return execnet.makegateway('popen')  # pylint: disable=no-member

    def setup(self, out=None):
        if out is None:
            out = py.io.TerminalWriter()
        # pylint: disable=access-member-before-definition
        # pylint: disable=attribute-defined-outside-init
        if hasattr(self, 'gateway'):
            raise ValueError('already have gateway %r' % self.gateway)
        self.trace('setting up worker session')
        self.gateway = self.initgateway()
        self.channel = channel = self.gateway.remote_exec(
            init_worker_session,
            args=self.config.args,
            option_dict=vars(self.config.option),
        )
        remote_outchannel = channel.receive()

        def write(line):
            out._file.write(line)  # pylint: disable=protected-access
            out._file.flush()       # pylint: disable=protected-access
        remote_outchannel.setcallback(write)

    def ensure_teardown(self):
        if hasattr(self, 'channel'):
            if not self.channel.isclosed():
                self.trace('closing', self.channel)
                self.channel.close()
            del self.channel
        if hasattr(self, 'gateway'):
            self.trace('exiting', self.gateway)
            self.gateway.exit()
            del self.gateway

    def runsession(self):
        try:
            self.trace('sending', self.failures)
            self.channel.send(self.failures)
            try:
                return self.channel.receive()
            except self.channel.RemoteError:
                exc = sys.exc_info()[1]
                self.trace('ERROR', exc)
                raise
        finally:
            self.ensure_teardown()

    def loop_once(self):
        self.setup()
        self.wasfailing = self.failures and len(self.failures)
        result = self.runsession()
        failures, _, collection_failed = result
        if collection_failed:
            pass  # "Collection failed, keeping previous failure set"
        else:
            uniq_failures = []
            for failure in failures:
                if failure not in uniq_failures:
                    uniq_failures.append(failure)
            self.failures = uniq_failures


def repr_pytest_looponfailinfo(failreports, rootdirs):
    term_writer = py.io.TerminalWriter()
    if failreports:
        term_writer.sep('#', 'LOOPONFAILING', bold=True)
        for report in failreports:
            if report:
                term_writer.line(report, red=True)
    term_writer.sep('#', 'waiting for changes', bold=True)
    for rootdir in rootdirs:
        term_writer.line('### Watching:   %s' % (rootdir,), bold=True)


def init_worker_session(channel, args, option_dict):
    import os
    outchannel = channel.gateway.newchannel()
    sys.stdout = sys.stderr = outchannel.makefile('w')
    channel.send(outchannel)
    # prune sys.path to not contain relative paths
    newpaths = []
    for path in sys.path:
        if not path:
            continue
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        newpaths.append(path)
    sys.path[:] = newpaths

    # fullwidth, hasmarkup = channel.receive()
    from _pytest import config as cfg
    config = cfg.Config.fromdictargs(option_dict, list(args))
    config.args = args
    # pylint: disable=import-self
    from taxi_xdist import looponfail as lofail
    lofail.WorkerFailSession(config, channel).main()


class WorkerFailSession:
    def __init__(self, config, channel):
        self.config = config
        self.channel = channel
        self.recorded_failures = []
        self.collection_failed = False
        self.session = None
        self.trails = None
        self.current_command = None
        config.pluginmanager.register(self)
        config.option.looponfail = False
        config.option.usepdb = False

    def debug(self, *args):
        if self.config.option.debug:
            print(' '.join(map(str, args)))

    def pytest_collection(self, session):
        self.session = session
        self.trails = self.current_command
        hook = self.session.ihook
        try:
            items = session.perform_collect(self.trails or None)
        except pytest.UsageError:
            items = session.perform_collect(None)
        hook.pytest_collection_modifyitems(
            session=session, config=session.config, items=items)
        hook.pytest_collection_finish(session=session)
        return True

    def pytest_runtest_logreport(self, report):
        if report.failed:
            self.recorded_failures.append(report)

    def pytest_collectreport(self, report):
        if report.failed:
            self.recorded_failures.append(report)
            self.collection_failed = True

    def main(self):
        self.debug(
            'WORKER: received configuration, waiting for command trails',
        )
        try:
            command = self.channel.receive()
        except KeyboardInterrupt:
            return  # in the worker we can't do much about this
        self.debug('received', command)
        self.current_command = command
        self.config.hook.pytest_cmdline_main(config=self.config)
        trails, failreports = [], []
        for rep in self.recorded_failures:
            trails.append(rep.nodeid)
            loc = rep.longrepr
            loc = str(getattr(loc, 'reprcrash', loc))
            failreports.append(loc)
        self.channel.send((trails, failreports, self.collection_failed))


class StatRecorder:
    def __init__(self, rootdirlist):
        self.rootdirlist = rootdirlist
        self.statcache = {}
        self.check()  # snapshot state

    @staticmethod
    def fil(path):
        return path.check(file=1, dotfile=0) and path.ext != '.pyc'

    @staticmethod
    def rec(path):
        return path.check(dotfile=0)

    def waitonchange(self, checkinterval=1.0):
        while 1:
            changed = self.check()
            if changed:
                return
            py.std.time.sleep(checkinterval)

    def check(self, removepycfiles=True):  # noqa, too complex
        changed = False
        statcache = self.statcache
        newstat = {}
        for rootdir in self.rootdirlist:
            for path in rootdir.visit(self.fil, self.rec):
                oldstat = statcache.pop(path, None)
                try:
                    newstat[path] = curstat = path.stat()
                except py.error.ENOENT:
                    if oldstat:
                        changed = True
                else:
                    if oldstat:
                        if (oldstat.mtime != curstat.mtime or
                                oldstat.size != curstat.size):
                            changed = True
                            py.builtin.print_('# MODIFIED', path)
                            if removepycfiles and path.ext == '.py':
                                pycfile = path + 'c'
                                if pycfile.check():
                                    pycfile.remove()

                    else:
                        changed = True
        if statcache:
            changed = True
        self.statcache = newstat
        return changed
