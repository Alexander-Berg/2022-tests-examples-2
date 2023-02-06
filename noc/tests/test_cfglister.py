import os
import concurrent.futures
import pathlib
import tempfile
from unittest import mock

import pytest

from checkist.cfglister import CfglisterUpdater, ConfigUpdater


class BaseFixures:
    @pytest.fixture
    def remote_client(self):
        m = mock.Mock()
        m.info = mock.Mock(return_value={"commit_revision": 1})
        m.url = "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister"
        return m

    @pytest.fixture
    def local_client(self):
        return mock.Mock()

    @pytest.fixture
    def local_path(self):
        tmpdir = tempfile.TemporaryDirectory()
        return tmpdir.name

    @pytest.fixture
    def cfglister_updater(self, remote_client, local_path):
        return CfglisterUpdater(remote_client=remote_client, local_path=local_path)

    @pytest.fixture
    def core(self, event_loop):
        c = mock.Mock()
        c.db = mock.MagicMock()
        c.loop = event_loop
        c.executor = concurrent.futures.thread.ThreadPoolExecutor()
        c.settings = mock.Mock()
        c.settings.cfglister = mock.Mock()
        c.settings.cfglister.url = "svn+ssh://user@example.com/url"
        c.settings.cfglister.username = "some-username"
        c.settings.cfglister.identity_file = "/path/to/idenitity"
        c.settings.cfglister.local_path = "/path/to/svn/local/repo"
        return c


class TestCfglisterUpdater(BaseFixures):
    def test_updater_update_checkout(self, remote_client, cfglister_updater):
        cfglister_updater.update()
        remote_client.checkout.assert_called_once_with(cfglister_updater._local_path)

    def test_updater_create(self, core):
        env = {"SVN_SSH": f"ssh -i {core.settings.cfglister.identity_file}"}
        with mock.patch("svn.remote.RemoteClient") as remote_client_cls:
            updater = CfglisterUpdater.create(core)
            remote_client_cls.assert_called_once_with(
                core.settings.cfglister.url, env=env,
            )
            assert updater.local_path == core.settings.cfglister.local_path

    def test_updater_update_return_none(self, cfglister_updater):
        cfglister_updater._commit_revision = 1
        cfglister_updater._remote_client.info = mock.MagicMock(return_value={
            "commit_revision": 1
        })
        result = cfglister_updater.update()
        assert cfglister_updater._commit_revision == 1
        assert result == ([], [])

    def test_updater_update_return_all(self, cfglister_updater):
        cfglister_updater._commit_revision = None
        cfglister_updater._remote_client.info = mock.MagicMock(return_value={
            "commit_revision": 1
        })
        result = cfglister_updater.update()
        assert cfglister_updater._commit_revision == 1
        assert result == (["*.cfg", "*.cfg/**/*"], [])

    def test_cfglister_updater_update_return_files(self, cfglister_updater):
        cfglister_updater._commit_revision = 1
        cfglister_updater._remote_client.info = mock.MagicMock(return_value={
            "commit_revision": 2
        })
        cfglister_updater._remote_client.diff_summary = mock.MagicMock(return_value=[
            # modified test
            {
                "item": "modified",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/sas1-s1.yndx.net.cfg",
            },
            # added test
            {
                "item": "added",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/sas1-s2.yndx.net.cfg",
            },
            # deleted test
            {
                "item": "deleted",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/sas1-s3-deleted.cfg",
            },
            # replaced test
            {
                "item": "replaced",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/vla2-8s73.yndx.net.cfg",
            },
            # whitebox config test
            {
                "item": "modified",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/vla2-8s73.yndx.net.cfg/etc/cumulus/acl/policy.d/00control_plane.rules",
            },
            # glob escape test
            {
                "item": "modified",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/vla2-8s73.yndx.net.cfg/etc/service*/config.yml",
            },
            # ignore non-config file
            {
                "item": "added",
                "kind": "dir",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/somedir/dir-ignored",
            },
        ])
        result = cfglister_updater.update()
        assert cfglister_updater._commit_revision == 2
        assert result == (
            [
                "sas1-s1.yndx.net.cfg",
                "sas1-s2.yndx.net.cfg",
                "vla2-8s73.yndx.net.cfg/etc/cumulus/acl/policy.d/00control_plane.rules",
                "vla2-8s73.yndx.net.cfg/etc/service[*]/config.yml",  # "*" is escaped as "[*]"
            ],
            [
                "sas1-s3-deleted.cfg",
                "vla2-8s73.yndx.net.cfg",
            ],
        )


class TestConfigUpdater(BaseFixures):
    @pytest.fixture
    def config_updater(self, core, cfglister_updater):
        config_updater = ConfigUpdater(core, cfglister_updater)
        config_updater._fs_storage = mock.AsyncMock()
        return config_updater

    @pytest.mark.asyncio
    async def test_config_updater_update_when_updated(self, cfglister_updater, config_updater):
        cfglister_updater.update = mock.MagicMock(return_value=(["*.cfg"], []))
        await config_updater.update()
        config_updater._fs_storage.upload_from_dir.assert_called_once_with(
            src_dir=os.path.join(cfglister_updater.local_path, "config"),
            bucket="current_configs",
            metadata_callbacks=mock.ANY,
            path_callback=mock.ANY,
            globs=["*.cfg"],
            make_upsert_params=ConfigUpdater._make_upsert_params,
        )

    @pytest.mark.asyncio
    async def test_config_updater_update_when_not_updated(self, cfglister_updater, config_updater):
        cfglister_updater.update = mock.MagicMock(return_value=([], []))
        await config_updater.update()
        assert not config_updater._fs_storage.upload_from_dir.called

    @pytest.mark.asyncio
    async def test_config_updater_update_return_files(self, cfglister_updater, config_updater):
        cfglister_updater._commit_revision = 1
        cfglister_updater._remote_client.info = mock.MagicMock(return_value={
            "commit_revision": 2
        })
        cfglister_updater._remote_client.diff_summary = mock.MagicMock(return_value=[
            {
                "item": "modified",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/sas1-s1.yndx.net.cfg",
            },
            {
                "item": "modified",
                "kind": "file",
                "path": "svn+ssh://robot-checkist@arcadia.yandex.ru/robots/trunk/noc/cfglister/config/vla2-8s73.yndx.net.cfg/etc/cumulus/acl/policy.d/00control_plane.rules",
            },
        ])
        result = await config_updater.update()
        assert result == [
            "sas1-s1.cfg",
            "vla2-8s73.cfg/etc/cumulus/acl/policy.d/00control_plane.rules",
        ], []

    @pytest.mark.parametrize("db_path, expected_path", (
        (
            "sas1-s1.cfg",
            "config/sas1-s1.yndx.net.cfg"
        ),
        (
            "vla2-8s73.cfg/etc/cumulus/acl/policy.d/00control_plane.rules",
            "config/vla2-8s73.yndx.net.cfg/etc/cumulus/acl/policy.d/00control_plane.rules"
        )

    ))
    def test_cfglister_fullpath(self, config_updater, local_path, db_path, expected_path):
        assert config_updater.cfglister_fullpath(db_path) == pathlib.Path(local_path).joinpath(expected_path)
