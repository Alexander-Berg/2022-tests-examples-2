"""
    This module is executed in remote subprocesses and helps to
    control a remote testing session and relay back information.
    It assumes that 'py' is importable and does not have dependencies
    on the rest of the xdist code.  This means that the xdist-plugin
    needs not to be installed in remote environments.
"""

import os
import sys
import time

import _pytest.hookspec
import pytest


# pylint: disable=redefined-outer-name
class WorkerInteractor:
    def __init__(self, config, channel):
        self.config = config
        self.session = None
        self.item_index = None
        self.workerid = config.workerinput.get('workerid', '?')
        self.log = py.log.Producer('worker-%s' % self.workerid)
        if not config.option.debug:
            # pylint: disable=protected-access
            py.log.setconsumer(self.log._keywords, None)
        self.channel = channel
        config.pluginmanager.register(self)

    def sendevent(self, name, **kwargs):
        self.log('sending', name, kwargs)
        self.channel.send((name, kwargs))

    def pytest_internalerror(self, excrepr):
        for line in str(excrepr).split('\n'):
            self.log('IERROR>', line)

    def pytest_sessionstart(self, session):
        self.session = session
        workerinfo = getinfodict()
        self.sendevent('workerready', workerinfo=workerinfo)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_sessionfinish(self, exitstatus):
        self.config.workeroutput['exitstatus'] = exitstatus
        yield
        self.sendevent('workerfinished', workeroutput=self.config.workeroutput)

    def pytest_collection(self, session):
        self.sendevent('collectionstart')

    def pytest_runtestloop(self, session):
        self.log('entering main loop')
        torun = []
        while 1:
            try:
                name, kwargs = self.channel.receive()
            except EOFError:
                return True
            self.log('received command', name, kwargs)
            if name == 'runtests':
                torun.extend(kwargs['indices'])
            elif name == 'runtests_all':
                torun.extend(range(len(session.items)))
            self.log('items to run:', torun)
            # only run if we have an item and a next item
            while len(torun) >= 1:
                self.run_one_test(torun)
            if name == 'shutdown':
                if torun:
                    self.run_one_test(torun)
                break
        return True

    def run_one_test(self, torun):
        items = self.session.items
        self.item_index = torun.pop(0)
        item = items[self.item_index]
        if torun:
            nextitem = items[torun[0]]
        else:
            nextitem = None

        start = time.time()
        self.config.hook.pytest_runtest_protocol(
            item=item,
            nextitem=nextitem)
        duration = time.time() - start
        self.sendevent('runtest_protocol_complete', item_index=self.item_index,
                       duration=duration)

    def pytest_collection_finish(self, session):
        self.sendevent(
            'collectionfinish',
            topdir=str(session.fspath),
            ids=[item.nodeid for item in session.items])

    def pytest_runtest_logstart(self, nodeid, location):
        self.sendevent('logstart', nodeid=nodeid, location=location)

    # the pytest_runtest_logfinish hook was introduced in pytest 3.4
    if hasattr(_pytest.hookspec, 'pytest_runtest_logfinish'):
        def pytest_runtest_logfinish(self, nodeid, location):
            self.sendevent('logfinish', nodeid=nodeid, location=location)

    def pytest_runtest_logreport(self, report):
        data = serialize_report(report)
        data['item_index'] = self.item_index
        data['worker_id'] = self.workerid
        assert self.session.items[self.item_index].nodeid == report.nodeid
        self.sendevent('testreport', data=data)

    def pytest_collectreport(self, report):
        data = serialize_report(report)
        self.sendevent('collectreport', data=data)

    def pytest_logwarning(self, message, code, nodeid, fslocation):
        self.sendevent('logwarning', message=message, code=code, nodeid=nodeid,
                       fslocation=str(fslocation))


def serialize_report(rep):
    def disassembled_report(rep):
        reprtraceback = rep.longrepr.reprtraceback.__dict__.copy()
        reprcrash = rep.longrepr.reprcrash.__dict__.copy()

        new_entries = []
        for entry in reprtraceback['reprentries']:
            entry_data = {
                'type': type(entry).__name__,
                'data': entry.__dict__.copy(),
            }
            for key, value in entry_data['data'].items():
                if hasattr(value, '__dict__'):
                    entry_data['data'][key] = value.__dict__.copy()
            new_entries.append(entry_data)

        reprtraceback['reprentries'] = new_entries

        return {
            'reprcrash': reprcrash,
            'reprtraceback': reprtraceback,
            'sections': rep.longrepr.sections,
        }

    import py  # pylint: disable=redefined-outer-name
    dct = rep.__dict__.copy()
    if hasattr(rep.longrepr, 'toterminal'):
        if (hasattr(rep.longrepr, 'reprtraceback') and
                hasattr(rep.longrepr, 'reprcrash')):
            dct['longrepr'] = disassembled_report(rep)
        else:
            dct['longrepr'] = str(rep.longrepr)
    else:
        dct['longrepr'] = rep.longrepr
    for name in dct:
        if isinstance(dct[name], py.path.local):
            dct[name] = str(dct[name])
        elif name == 'result':
            dct[name] = None  # for now
    return dct


def getinfodict():
    import platform
    return dict(
        version=sys.version,
        version_info=tuple(sys.version_info),
        sysplatform=sys.platform,
        platform=platform.platform(),
        executable=sys.executable,
        cwd=os.getcwd(),
    )


def remote_initconfig(option_dict_, args_):
    from _pytest import config as conf
    option_dict_['plugins'].append('no:terminal')
    config_ = conf.Config.fromdictargs(option_dict_, args_)
    config_.option.looponfail = False
    config_.option.usepdb = False
    config_.option.dist = 'no'
    config_.option.distload = False
    config_.option.numprocesses = None
    config_.args = args_
    return config_


# pylint: disable=invalid-name, undefined-variable
if __name__ == '__channelexec__':
    channel = channel  # type: ignore  # noqa
    workerinput, args, option_dict = channel.receive()  # type: ignore
    importpath = os.getcwd()
    sys.path.insert(0, importpath)  # XXX only for remote situations
    os.environ['PYTHONPATH'] = (
        importpath + os.pathsep +
        os.environ.get('PYTHONPATH', ''))
    os.environ['PYTEST_XDIST_WORKER'] = workerinput['workerid']
    os.environ['PYTEST_XDIST_WORKER_COUNT'] = str(workerinput['workercount'])
    # os.environ['PYTHONPATH'] = importpath
    import py
    config = remote_initconfig(option_dict, args)
    config.workerinput = workerinput
    config.workeroutput = {}
    # TODO: deprecated name, backward compatibility only. Remove it in future
    config.slaveinput = config.workerinput
    config.slaveoutput = config.workeroutput
    interactor = WorkerInteractor(config, channel)  # type: ignore
    config.hook.pytest_cmdline_main(config=config)
