import os
import mock
import pytest

from sandbox.sandboxsdk import copy


@pytest.fixture()
def subprocess(tmpdir, monkeypatch):
    import subprocess as sp
    monkeypatch.setattr(sp, "Popen", mock.MagicMock())
    sp.Popen.return_value = mock.MagicMock()
    sp.Popen.return_value.wait = mock.MagicMock()
    sp.Popen.return_value.wait.return_value = 0
    return sp


class TestRemoteCopy(object):
    def test__remote_copy_http(self, tmpdir, subprocess):
        from sandbox.projects.sandbox import remote_copy_resource
        tmpdir = str(tmpdir)
        filename = "favicon.png"
        url = "http://sandbox.yandex-team.ru/{}".format(filename)
        local_path = os.path.join(tmpdir, filename)
        remote_copy_resource.RemoteCopyResource._remote_copy(
            url,
            local_path,
            tmpdir,
            10,
            additional_positional_param=True
        )
        assert subprocess.Popen.called
        cmd = list(subprocess.Popen.call_args[0][0])
        assert cmd == ["curl", "-f", "-L", "-m", "5", "--additional-positional-param", "-o", local_path, url]

    def test__remote_copy_svn(self, tmpdir, subprocess):
        src = "svn+ssh://host/path"
        dst = "/local/path"
        copy.RemoteCopy(src, dst, log_dir=str(tmpdir))()
        assert subprocess.Popen.called
        cmd = list(subprocess.Popen.call_args[0][0])
        assert cmd == ["svn", "export", src, dst]
        subprocess.Popen.reset_mock()
        copy.RemoteCopy(src, dst, log_dir=str(tmpdir))(opt1=123, opt_2=456, opt3=True)
        assert subprocess.Popen.called
        cmd = list(subprocess.Popen.call_args[0][0])
        assert cmd == ["svn", "export", "--opt1", "123", "--opt-2", "456", "--opt3", src, dst]
