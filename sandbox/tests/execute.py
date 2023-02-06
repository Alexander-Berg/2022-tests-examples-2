import tarfile
import tempfile

import py

from sandbox.client import platforms


class TestExecutor(object):
    def test__on_real_files(self, tmpdir):

        tmpdir = py.path.local(tmpdir)

        svn_dir = tmpdir.mkdir('.subversion')
        svn_config = svn_dir.join('config').ensure(file=True)
        svn_auth = svn_dir.mkdir('auth').join('fsd85f6sdf').ensure(file=True)
        bash_rc = tmpdir.join('.bashrc').ensure(file=True)
        profile = tmpdir.join('.profile').ensure(file=True)

        with tempfile.NamedTemporaryFile() as f:
            with tarfile.open(mode='w', fileobj=f) as tar:
                tar.add(str(tmpdir), arcname='')

            svn_trash = svn_dir.mkdir('trash')
            trash = tmpdir.mkdir('.hiddentrash')
            build_dir = tmpdir.mkdir('build')
            pip_build = build_dir.join('pip').ensure(file=True)
            wheel_build = build_dir.mkdir('wheel')

            debris = [
                svn_trash,
                trash,
                build_dir,
                pip_build,
                wheel_build
            ]

            platforms.Platform._clean_fs_debris(str(tmpdir))
            platforms.Platform._restore_home(str(tmpdir), f.name)

        assert svn_auth.check(file=True)
        assert svn_config.check(file=True)
        assert bash_rc.check(file=True)
        assert profile.check(file=True)

        for d in debris:
            assert not d.check()
