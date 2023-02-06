from datetime import datetime

import pytest

from metrika.admin.python.mtapi.lib.api.packages import lib as mtplib


class TestDockerVersion:
    @staticmethod
    def test_single_du_single_box(yp_api, sandbox_api, stage_with_docker_image_single_du_single_box):
        yp_api.add_stage("any_name-any_env", stage_with_docker_image_single_du_single_box)

        version = mtplib.DeployVersionGetter(
            deploy_api=yp_api,
            sandbox_api=sandbox_api,
            package="any_name",
            environment="any_env",
        ).get_version()
        assert version == "1.2.3"

    @staticmethod
    def test_docker_no_layer(yp_api, sandbox_api, stage_with_docker_no_layers):
        yp_api.add_stage("any_name-any_env", stage_with_docker_no_layers)

        version = mtplib.DeployVersionGetter(
            deploy_api=yp_api,
            sandbox_api=sandbox_api,
            package="any_name",
            environment="any_env",
        ).get_version()
        assert version == "1.2.3"

    @staticmethod
    def test_many_du_single_boxes(yp_api, sandbox_api, stage_with_docker_image_many_du_single_box):
        yp_api.add_stage("my_deploy_unit-prod", stage_with_docker_image_many_du_single_box)
        version = mtplib.DeployVersionGetter(
            deploy_api=yp_api,
            sandbox_api=sandbox_api,
            package="my_deploy_unit",
            environment="prod",
        ).get_version()
        assert version == "1.2.3"

    @staticmethod
    def test_many_du_many_boxes(yp_api, sandbox_api, stage_with_docker_image_many_du_many_box):
        yp_api.add_stage("my_app-prod", stage_with_docker_image_many_du_many_box)
        version = mtplib.DeployVersionGetter(
            deploy_api=yp_api,
            sandbox_api=sandbox_api,
            package="my_app",
            environment="prod",
        ).get_version()
        assert version == "3.2.1"

    @staticmethod
    def test_wrong_config(yp_api, sandbox_api, stage_with_docker_image_many_du_many_box):
        yp_api.add_stage("smth-wrong", stage_with_docker_image_many_du_many_box)
        with pytest.raises(mtplib.PackagesUserError):
            mtplib.DeployVersionGetter(
                deploy_api=yp_api,
                sandbox_api=sandbox_api,
                package="smth",
                environment="wrong",
            ).get_version()


class TestGetVersionFromTarball:
    @staticmethod
    def test_get_layer_meta_version(yp_api, sandbox_api, stage_with_layer_meta):
        yp_api.add_stage("res_app-env", stage_with_layer_meta)
        version = mtplib.DeployVersionGetter(
            deploy_api=yp_api,
            sandbox_api=sandbox_api,
            package="res_app",
            environment="env",
        ).get_version()
        assert version == "3.2.1"

    @staticmethod
    def test_get_layer_meta_version_multi_cluster(yp_api, sandbox_api, multi_cluster_stage_with_layer_meta):
        yp_api.add_stage("res_app-env", multi_cluster_stage_with_layer_meta)
        version = mtplib.DeployVersionGetter(
            deploy_api=yp_api,
            sandbox_api=sandbox_api,
            package="res_app",
            environment="env",
        ).get_version()
        assert version == "100500"

    @staticmethod
    def test_get_layer_url_version(yp_api, sandbox_api, stage_with_layer_url):
        yp_api.add_stage("layer-or-not", stage_with_layer_url)
        with pytest.raises(mtplib.PackagesInternalError):
            mtplib.DeployVersionGetter(deploy_api=yp_api,
                                       sandbox_api=sandbox_api,
                                       package="layer",
                                       environment="or-not",
                                       ).get_version()


class TestGetAllVersions:
    @staticmethod
    def test_get_all_versions(yp_api, sandbox_api, monster_stage):
        yp_api.add_stage("monster", monster_stage)
        result = mtplib.DeployAllVersionsGetter(
            deploy_api=yp_api,
            sandbox_api=sandbox_api,
            stage_name="monster",
        ).get_versions()

        assert result == dict(
            du1=dict(
                qwe=dict(
                    wtf=dict(
                        other="100500",
                    ),
                    zxc=dict(
                        asd="qwe",
                    ),
                ),
                my_box={
                    "docker": dict(
                        my_app="1.2.3",
                    ),
                },
            ),
            asd=dict(
                box={
                    "base-layer-0": dict(
                        url="rbtorrent:asd-qwe",
                    ),
                    "app": dict(
                        best_app="100500",
                    ),
                },
            ),
            qwerty=dict(
                not_my_box={
                    "docker": dict(
                        not_my_app="4.5.6",
                    ),
                },
            ),
        )

    def test_stage_name_without_env(self, yp_api):
        assert mtplib.DeployAllVersionsGetter(deploy_api=yp_api, sandbox_api=None, daemon_name="test").stage_name == "test"

    def test_stage_name_with_stage_name(self):
        assert mtplib.DeployAllVersionsGetter(deploy_api=None, sandbox_api=None, stage_name="test").stage_name

    def test_stage_name_doesnt_exist(self, rr_doesnt_exist):
        assert mtplib.DeployAllVersionsGetter(deploy_api=rr_doesnt_exist, sandbox_api=None, daemon_name="test", environment="testing").stage_name == "test-testing"

    def test_stage_name(self, rr_exists):
        assert mtplib.DeployAllVersionsGetter(deploy_api=rr_exists, sandbox_api=None, daemon_name="test", environment="testing").stage_name == "exists"


class TestGetInfo:
    def test_get_info_without_rr(self, rr_doesnt_exist):
        with pytest.raises(mtplib.PackagesUserError):
            mtplib.DeployVersionGetter(deploy_api=rr_doesnt_exist, sandbox_api=None, package="test", environment="testing").get_info()

    def test_get_info_with_rr(self, rr_exists_with_versions):
        assert mtplib.DeployVersionGetter(deploy_api=rr_exists_with_versions, sandbox_api=None, package="test", environment="testing").get_info() == ('stage', 'du', 'box', 'layer')


@pytest.mark.parametrize('revision, real_revision', [
    (10, 10),
    (9, 8),
    (8, 8),
    (7, 5),
    (6, 5),
    (5, 5),
    (4, 2),
    (3, 3),
    (2, 2),
    (1, 1)
])
def test_revision_info(history, revision, real_revision):
    assert history._get_revision_info('test', revision)[1] == str(real_revision)


class TestGetReleaseInfo:
    def test_with_release(self, getter_with_release):
        assert getter_with_release.get_release_info() == ('1337', datetime.utcfromtimestamp(0), 'from_release', '1337')

    def test_without_release(self, getter_without_release):
        assert getter_without_release.get_release_info() == ('1337', datetime.utcfromtimestamp(0), 'from_revision', None)
