import os
import pytest

import metrika.admin.python.cms.frontend.tests.helper as helper
import metrika.admin.python.cms.lib.pg.queue as queue
from metrika.admin.python.cms.judge.lib import helpers as judge_helpers


def pytest_configure():
    os.environ['APP_DIR'] = os.path.join(
        os.path.dirname(__file__),
        '..',
    )
    os.environ['DJANGO_SETTINGS_MODULE'] = 'metrika.admin.python.cms.frontend.base.settings'

    import django
    django.is_in_test = True
    django.setup()


def pytest_unconfigure():
    import django
    del django.is_in_test


@pytest.fixture
def noop_queue(monkeypatch):
    monkeypatch.setattr(queue, 'Queue', helper.NoOpQueue)


@pytest.fixture(autouse=True)
def mock_host_is_supported(monkeypatch):
    monkeypatch.setattr(judge_helpers, "host_is_supported", lambda *args, **kwargs: True)
