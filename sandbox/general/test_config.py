import yatest.common
import os

from sandbox.sdk2.path import Path

from sandbox.projects.geosuggest.component.daemonconf import make_isolated_config


def _run(name):
    src = yatest.common.source_path(os.path.join('sandbox/projects/geosuggest/component/ut/data', name))
    dst = 'output.conf'
    make_isolated_config(Path(src), Path(dst))
    return yatest.common.canonical_file(dst, local=True)


def test_isolated_config_prod():
    return _run('prod.daemon.conf')


def test_isolated_config_empty():
    return _run('empty.daemon.conf')
