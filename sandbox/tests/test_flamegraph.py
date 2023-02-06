import six

import yatest.common

from sandbox.projects.autocheck.lib import profile

if six.PY3:
    import pathlib
else:
    import pathlib2 as pathlib


class ProxyTask(object):
    class Resource(object):
        http_proxy = 'test_proxy_url'

    def __init__(self, path):
        self.log_resource = self.Resource()
        self.path = path

    def log_path(self, path=''):
        return self.path / path


def test_profile():
    work_dir = pathlib.Path(yatest.common.output_path('work_dir'))
    task = ProxyTask(work_dir)

    profiler = profile.FlamegraphProfiler(task.log_path('flamegraph'))

    with profiler.start_profile_thread():
        sum([i for i in range(1000000)])

    path, link = profiler.prepare_report(task)
    assert path is not None
    assert link is not None
    with open(str(path)) as f:
        content = f.read()
    return {
        'link': link,
        'content': content,
    }
