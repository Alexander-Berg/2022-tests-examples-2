import os.path

import pytest

from taxi import conf


@pytest.mark.parametrize('path', [
    'debian/settings.autotest.py',
    'debian/settings.development.py',
    'debian/settings.production.py',
    'debian/settings.stress.py',
    'debian/settings.testing.py',
    'debian/settings.unstable.py',
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_debian_config(path, monkeypatch):
    path = os.path.join(
        os.path.dirname(__file__), '..', path)
    monkeypatch.setattr(
        conf, 'settings', conf.LazySettings())
    execfile(path)
