import os
import mock

from sandbox import sandboxsdk
import sandbox.projects.common.debpkg


class TestDebRelease:
    DUPLOAD_CONF = {
        'common': {
            'fqdn': "dist.yandex.ru",
            'method': "scpb",
            'login': "own_zomb_name",
            'incoming': "/repo/common/mini-dinstall/incoming/",
            'dinstall_runs': 1,
        },
        'search': {
            'fqdn': "dist.yandex.ru",
            'method': "scpb",
            'login': "own_zomb_name",
            'incoming': "/repo/common/mini-dinstall/incoming/",
            'dinstall_runs': 1,
        }
    }

    def test__deb_release(self):
        sandboxsdk.process.run_process = mock.MagicMock()
        with sandbox.projects.common.debpkg.DebRelease(self.DUPLOAD_CONF) as deb:
            deb.debrelease(['--to', 'TEST_REPO'])
            assert sandboxsdk.process.run_process.called
            args = sandboxsdk.process.run_process.call_args[0][0]
            assert args[0] == 'debrelease'
            assert all(o in args for o in ['--to', '-c', 'TEST_REPO'])
            assert os.path.isfile(os.path.expanduser('~/.dupload.conf'))
            assert 'login => "own_zomb_name"' in open(os.path.expanduser('~/.dupload.conf'), 'r').read()
