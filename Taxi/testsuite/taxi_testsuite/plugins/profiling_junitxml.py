import time

import pytest


class ProfilingJunitxmlPlugin:
    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef, request):
        t0 = time.perf_counter()
        yield
        t1 = time.perf_counter()
        user_properties = _get_user_properties(request.node)
        if user_properties is not None:
            user_properties.append(
                (f'{fixturedef.argname}_setup_time', t1 - t0),
            )

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item):
        t0 = time.perf_counter()
        yield
        t1 = time.perf_counter()
        item.user_properties.append((f'total_setup_time', t1 - t0))

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_teardown(self, item, nextitem):
        t0 = time.perf_counter()
        yield
        t1 = time.perf_counter()
        item.user_properties.append((f'total_teardown_time', t1 - t0))


def pytest_addoption(parser):
    group = parser.getgroup('profiling')
    group.addoption(
        '--profile-junitxml',
        action='store_true',
        help='Write fixture setup / teardown timings to junitxml report',
    )


def pytest_configure(config):
    if config.option.profile_junitxml:
        config.pluginmanager.register(ProfilingJunitxmlPlugin())


def _get_user_properties(node):
    if hasattr(node, 'user_properties'):
        return node.user_properties
    if hasattr(node, 'items'):
        if node.items:
            return _get_user_properties(node.items[0])
    return None
