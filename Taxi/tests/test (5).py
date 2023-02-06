import os
import subprocess

import yatest.common  # pylint: disable=import-error

from codegen import plugin_manager
from util.codegen_utils import core_plugins


def test_codegen(monkeypatch):
    monkeypatch.setattr(subprocess, 'call', lambda *args, **kwargs: 0)
    repo_dir = os.path.normpath(yatest.common.source_path('taxi/uservices'))
    monkeypatch.chdir(os.path.dirname(os.path.dirname(repo_dir)))
    argv = ['--build-dir=/fake/path/build', '-s', 'arcadia-userver-test']
    repo = core_plugins.Repository(repo_dir, argv)
    manager = plugin_manager.PluginManager(
        repo, repo_dir, scope_requires=repo.scope_requires, progress=False,
    )
    manager.init()
    manager.configure()
    try:
        manager.validate(filter_plugins=('ya-make', 'ya-make-index'))
    except plugin_manager.ValidationError as exc:
        assert exc.got == exc.expected, exc
