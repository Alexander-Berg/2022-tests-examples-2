import pytest
import pathlib
import uuid

from datetime import datetime
import typing as tp
from reactor_client import reactor_objects as ro
from reactor_client import reactor_api as ra

from init_py_env import settings

from connection.reactor import get_reactor_client
from connection.reactor import get_reactor_objects_config
from connection.reactor import ReactorObjectConfig

from dmp_suite.ext_source_proxy.reactor import get_artifact_instance_range_by_user_timestamp


@pytest.fixture
def reactor_test_client_and_conf():
    def _reactor_settings():
        # TODO: унести настройки в yav когда будет доступ (добавить еще токен
        #       и permissions (чтобы можно было вручную удалить какую-нибудь
        #       упячку
        return {
            'reactor': {
                'base_url': 'https://test.reactor.yandex-team.ru',
                'project_root_path': '/taxi/dwh/test',
                'project_id': 534,
            }
        }

    with settings.patch(**_reactor_settings()):
        yield ClientAndConf(
            client=get_reactor_client(),
            config=get_reactor_objects_config(),
        )


class ClientAndConf(tp.NamedTuple):
    client: ra.ReactorAPIClientV1
    config: ReactorObjectConfig


@pytest.fixture
def reactor_artifact_by_path(reactor_test_client_and_conf: ClientAndConf):
    """Фикстура, которая создает артефакт с инстансами и сносит после себя"""

    client = reactor_test_client_and_conf.client
    config = reactor_test_client_and_conf.config

    project_root = pathlib.Path(config.project_root_path)

    random_name = uuid.uuid4().hex

    artifact_path = str(project_root / 'artifacts' / random_name)

    # TODO: try to move into reactor api after (TAXIDWH-11280)
    def _get_permissions(config):
        role_map = {
            'READER': ro.NamespaceRole.READER,
            'RESPONSIBLE': ro.NamespaceRole.RESPONSIBLE,
            'WRITER': ro.NamespaceRole.WRITER,
        }
        roles = {
            role['login']: role_map[role['role']]
            for role in config.artifact_permissions
        }
        return ro.NamespacePermissions(
            roles=roles
        )

    resp = client.artifact.create(
        artifact_type_identifier=ro.ArtifactTypeIdentifier(
            artifact_type_key='YT_PATH',
        ),
        artifact_identifier=ro.ArtifactIdentifier(
            namespace_identifier=ro.NamespaceIdentifier(
                namespace_path=artifact_path
            ),
        ),
        cleanup_strategy=ro.CleanupStrategyDescriptor(
            cleanup_strategies=[
                ro.CleanupStrategy(
                    ttl_cleanup_strategy=ro.TtlCleanupStrategy(
                        ttl_days=1,
                    ),
                ),
            ],
        ),
        project_identifier=ro.ProjectIdentifier(
            project_id=config.project_id,
        ),
        create_if_not_exist=True,
        create_parent_namespaces=True,
        permissions=_get_permissions(config),
        description='test instance ranges',
    )

    artifact_id = resp.artifact_id

    yield artifact_path

    client.namespace.delete(
        namespace_identifier_list=[
            ro.NamespaceIdentifier(
                namespace_id=artifact_id
            )
        ]
    )


def _instantiate_artifact(
        client: ra.ReactorAPIClientV1,
        artifact_path: str,
        user_time: datetime
):
    client.artifact_instance.instantiate(
        artifact_identifier=ro.ArtifactIdentifier(
            namespace_identifier=ro.NamespaceIdentifier(
                namespace_path=artifact_path,
            )
        ),
        metadata=ro.Metadata(
            type_='/yandex.reactor.artifact.YtPathArtifactValueProto',
            dict_obj={
                'cluster': 'igor',
                'path': '//path/to/success',
            }
        ),
        attributes={},
        user_time=user_time,
    )


# TODO: не скипать тест, когда отредактируется конфиг в yav для инт. тестов
@pytest.mark.skip
@pytest.mark.slow
def test_get_artifact_instance_range_by_user_timestamp_works(
        reactor_artifact_by_path: tp.Text,
        reactor_test_client_and_conf: ClientAndConf,
):
    client = reactor_test_client_and_conf.client
    artifact_path = reactor_artifact_by_path

    def _instantiate(user_time):
        _instantiate_artifact(client, artifact_path, user_time)

    _instantiate(datetime(2020, 4, 10, 10, 0))
    _instantiate(datetime(2020, 4, 10, 10, 30))
    _instantiate(datetime(2020, 4, 10, 11, 0))
    _instantiate(datetime(2020, 4, 10, 11, 30))
    _instantiate(datetime(2020, 4, 10, 13, 30))

    response = get_artifact_instance_range_by_user_timestamp(
        artifact_path=artifact_path,
        dttm_from=datetime(2020, 4, 10, 10, 20),
        dttm_to=datetime(2020, 4, 10, 13, 31),
        limit=10,
    )

    expected = [
        datetime(2020, 4, 10, 13, 30),
        datetime(2020, 4, 10, 11, 30),
        datetime(2020, 4, 10, 11, 0),
        datetime(2020, 4, 10, 10, 30),
    ]

    assert [a.user_time for a in response] == expected
