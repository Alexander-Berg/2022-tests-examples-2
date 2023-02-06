import asyncio

import pytest


@pytest.fixture
async def _endless_sleep(pytestconfig):
    yield
    reporter = (
        pytestconfig.pluginmanager.get_plugin('servicetest_runner').reporter
    )
    reporter.write_line(
        'Service started, use C-c to terminate', yellow=True,
    )
    while True:
        await asyncio.sleep(1)


def pytest_addoption(parser):
    group = parser.getgroup('service runner', 'servicerunner')
    group.addoption(
        '--service-runner-mode', action='store_true',
        help='Run pytest in service runner mode',
    )


def pytest_configure(config):
    if config.option.service_runner_mode:
        runner = ServiceTestRunner(config)
        config.pluginmanager.register(runner, 'servicetest_runner')


class ServiceTestRunner:
    def __init__(self, config):
        self.config = config

    @property
    def reporter(self):
        return self.config.pluginmanager.get_plugin('terminalreporter')

    # Filter out all but servicetest items
    @pytest.hookimpl(trylast=True)
    def pytest_collection_modifyitems(self, session, items):
        service_items = []
        for item in items:
            for marker in item.own_markers:
                if marker.name == 'servicetest':
                    service_items.append(item)
                    break
        if len(service_items) != 1:
            self.reporter.write_line(
                f'You have to select only one servicetest, '
                f'{len(service_items)} selected', red=True,
            )
            raise session.Failed
        service_items[0].fixturenames.append('_endless_sleep')
        items[:] = service_items

    def pytest_sessionstart(self, session):
        reporter = self.config.pluginmanager.get_plugin('terminalreporter')
        reporter.write_line('Running in servicetest mode', yellow=True)

    def pytest_runtestloop(self, session):  # pylint: disable=no-self-use
        item = session.items[0]
        item.config.hook.pytest_runtest_protocol(item=item, nextitem=None)
        if session.shouldfail:
            raise session.Failed(session.shouldfail)
        if session.shouldstop:
            raise session.Interrupted(session.shouldstop)
        return True

    @pytest.hookimpl(hookwrapper=True, tryfirst=True)
    def pytest_runtest_call(self, item):
        try:
            result = yield
            result.get_result()
        except Exception:  # pylint: disable=broad-except
            self.reporter.write_line('Failed to start service', red=True)
