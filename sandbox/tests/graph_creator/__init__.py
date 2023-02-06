from datetime import datetime
from unittest.mock import MagicMock

from ott.drm.library.python.packager_task.models import PackagerTask, TaskStatus
from yweb.video.faas.graphs.ott.common import Priority

from sandbox.projects.ott.packager_management_system.lib.graph_creator import GraphCreator
from sandbox.projects.ott.packager_management_system.lib.graph_creator import OttPackagerGraphCreationResult
from sandbox.projects.ott.packager_management_system.lib.graph_creator.ott_packager import (
    OttPackager,
    DummyOttPackagerRepository,
    OttPackagerResourceAttrs,
    OttPackagerReleaseStatus
)
from sandbox.projects.ott.packager_management_system.lib.tests.stubs import PackagerTasksApiClientStub


def test_no_tasks():
    tasks_client_stub = PackagerTasksApiClientStub()
    mocked_ott_packager = create_ott_packager_mock()

    graph_creator = create_graph_creator(tasks_client_stub, mocked_ott_packager, 2, 5)

    graph_creator.run()

    mocked_ott_packager.create_graph.assert_not_called()


def test_tasks_not_exceed_quota_limit():
    tasks_client_stub = PackagerTasksApiClientStub()

    graph_creator = create_graph_creator(tasks_client_stub, create_ott_packager_mock(), 2, 5)

    create_tasks(tasks_client_stub, 3)

    graph_creator.run()

    assert tasks_client_stub.count([TaskStatus.GRAPH_CREATED]) == 3


def test_tasks_exceed_quota_limit():
    tasks_client_stub = PackagerTasksApiClientStub()

    graph_creator = create_graph_creator(tasks_client_stub, create_ott_packager_mock(), 2, 5)

    create_tasks(tasks_client_stub, 6)

    graph_creator.run()

    assert tasks_client_stub.count([TaskStatus.GRAPH_CREATED]) == 5
    assert tasks_client_stub.count([TaskStatus.ENQUEUED_FOR_CREATE_GRAPH]) == 1


def create_tasks(tasks_client_stub, count):
    for _ in range(count):
        task = PackagerTask('input_stream_id', 'vod_provider_id', TaskStatus.NEW, 'author', Priority.MEDIUM, {},
                            nirvana_quota='ott-encoder')
        tasks_client_stub.create(task)


def create_graph_creator(tasks_client, ott_packager, max_graph_creating_workers, max_not_launched_graphs):
    return GraphCreator(
        tasks_client=tasks_client,
        ott_packager_repository=DummyOttPackagerRepository(ott_packager),
        max_graph_creating_workers=max_graph_creating_workers,
        max_not_launched_graphs=max_not_launched_graphs,
        nirvana_oauth_token='',
        retrieve_tasks_interval_secs=0.1,
        full_quota_check_interval_secs=0.1,
        nirvana_quota='ott-encoder',
        s3_creds_nirvana_secret_name='s3-creds',
        s3_creds='',
        vod_providers=['ott-packager']
    )


def create_ott_packager_mock():
    attrs = OttPackagerResourceAttrs(datetime.now(), '', OttPackagerReleaseStatus.TESTING)
    mocked_ott_packager = OttPackager('', attrs)

    mocked_ott_packager.create_graph = MagicMock(return_value=OttPackagerGraphCreationResult(0, None, {}))

    return mocked_ott_packager
