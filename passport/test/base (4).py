import grp
import pwd
from unittest import TestCase

from atomicwrites import AtomicWriter
import mock
from passport.backend.tvm_keyring.test.fake_tvm import FakeTVM
from pyfakefs.fake_filesystem_unittest import Patcher


class BaseTestCase(TestCase):
    def __init__(self, methodName='runTest'):
        super(BaseTestCase, self).__init__(methodName)
        self._fs_stubber = Patcher(
            additional_skip_names=[
                'logging',
                'ylog',
            ],
        )
        self._sync_patch = mock.patch.object(AtomicWriter, 'sync', mock.Mock())
        self._sync_directory_patch = mock.patch('atomicwrites._sync_directory', mock.Mock())
        self.fake_tvm = FakeTVM()

        self.getpwnam_mock = mock.Mock()
        self.getpwnam_mock.return_value.pw_uid = 1
        self.pwd_getpwnam_patch = mock.patch.object(pwd, 'getpwnam', self.getpwnam_mock)

        self.getgrnam_mock = mock.Mock()
        self.getgrnam_mock.return_value.gr_gid = 2
        self.grp_getgrnam_patch = mock.patch.object(grp, 'getgrnam', self.getgrnam_mock)

        self.patches = [
            self._sync_patch,
            self._sync_directory_patch,
            self.fake_tvm,
            self.pwd_getpwnam_patch,
            self.grp_getgrnam_patch,
        ]

    @property
    def fake_fs(self):
        return self._fs_stubber.fs

    def setUp(self):
        super(BaseTestCase, self).setUp()

        self._fs_stubber.setUp()

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        super(BaseTestCase, self).tearDown()

        for patch in reversed(self.patches):
            patch.stop()

        self._fs_stubber.tearDown()

        del self.grp_getgrnam_patch
        del self.pwd_getpwnam_patch
        del self.fake_tvm
        del self._sync_directory_patch
        del self._sync_patch
