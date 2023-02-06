import logging
import os
import re
from datetime import datetime

import pytest
import requests_mock

import yatest.common

from metrika.pylib.structures.dotdict import DotDict

from google.protobuf.json_format import MessageToDict

import sandbox.common.rest as sandbox_rest
from yp_proto.yp.client.api.proto import stage_pb2

from metrika.pylib.mtapi.cluster import BASE_URL as CLUSTER_BASE_URL

import metrika.pylib.deploy.client as mpd

import metrika.admin.python.mtapi.lib.api.packages.api as pkg_api
import metrika.admin.python.mtapi.lib.api.packages.lib as pkg_lib

import metrika.admin.python.mtapi.lib.app as lib_app


@pytest.fixture()
def args():
    return DotDict.from_dict(
        {
            "app": "packages",
            "bishop_env": None,
            "config": yatest.common.source_path('metrika/admin/python/mtapi/lib/api/packages/tests/config.yaml')
        }
    )


@pytest.fixture()
def client(args):
    app, config = lib_app.create_app(args)

    with app.test_client() as client:
        yield client


class YpApiMock(object):
    def __init__(self):
        self.stages = {}

    def add_stage(self, name, stage):
        self.stages[name] = stage

    def get_stage_specification(self, stage):
        d = MessageToDict(self.stages[stage], preserving_proto_field_name=True)
        logging.debug("Generated dict: %s" % d)
        return d

    @property
    def stage(self):
        return self

    def get_object(self, object_id, object_type, selectors):
        if object_type == 'release_rule':
            return [object_id]


@pytest.fixture
def stage():
    stage_obj = stage_pb2.TStageSpec()
    stage_obj.revision = 29
    stage_obj.account_id = "abc:service:185"

    yield stage_obj


@pytest.fixture
def stage_with_docker_image_single_du_single_box(stage):
    du = stage.deploy_units["my_deploy_unit"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "my_box"

    layers = pod_agent_spec.resources.layers
    layer_0 = layers.add()
    layer_0.id = "my_app"

    image = du.images_for_boxes["my_box"]
    image.name = "my_app"
    image.tag = "1.2.3"

    yield stage


@pytest.fixture
def stage_with_docker_image_many_du_single_box(stage):
    du = stage.deploy_units["not_my_deploy_unit_not"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "my_app"

    layers = pod_agent_spec.resources.layers
    layer_0 = layers.add()
    layer_0.id = "my_app"

    image = du.images_for_boxes["my_box"]
    image.name = "my_app"
    image.tag = "fake"

    du = stage.deploy_units["my_deploy_unit"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "my_app"

    layers = pod_agent_spec.resources.layers
    layer_0 = layers.add()
    layer_0.id = "my_app"

    image = du.images_for_boxes["my_box"]
    image.name = "my_app"
    image.tag = "1.2.3"

    yield stage


@pytest.fixture
def stage_with_docker_image_many_du_many_box(stage):
    du = stage.deploy_units["any_deploy_unit"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "wrong"
    box_1 = pod_agent_spec.boxes.add()
    box_1.id = "my_app"

    layers = pod_agent_spec.resources.layers
    layer_0 = layers.add()
    layer_0.id = "my_app"

    image = du.images_for_boxes["my_box"]
    image.name = "wrong"
    image.tag = "fake"

    image = du.images_for_boxes["another_box"]
    image.name = "not_my_app_not"
    image.tag = "1.2.3"

    du = stage.deploy_units["my_deploy_unit"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "wrong"
    box_1 = pod_agent_spec.boxes.add()
    box_1.id = "my_app"

    layers = pod_agent_spec.resources.layers
    layer_0 = layers.add()
    layer_0.id = "my_app"

    image = du.images_for_boxes["my_box"]
    image.name = "wrong"
    image.tag = "fake"

    image = du.images_for_boxes["another_box"]
    image.name = "my_app"
    image.tag = "3.2.1"

    yield stage


@pytest.fixture
def stage_with_layer_meta(stage):
    du = stage.deploy_units["random_name"]
    rs = du.replica_set.replica_set_template
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "realy_random_name"
    box_layers = box_0.rootfs.layer_refs

    layers = pod_agent_spec.resources.layers

    layer_0 = layers.add()
    layer_0.id = "wtf1"
    box_layers.append("wtf1")
    layer_0.meta.sandbox_resource.task_id = "1337"
    attributes = layer_0.meta.sandbox_resource.attributes
    attributes["resource_name"] = "res_app_fake"
    attributes["resource_version"] = "fake"

    layer_1 = layers.add()
    layer_1.id = "wtf2"
    box_layers.append("wtf2")
    layer_1.meta.sandbox_resource.task_id = "1337"
    attributes = layer_1.meta.sandbox_resource.attributes
    attributes["resource_name"] = "res_app"
    attributes["resource_version"] = "3.2.1"

    yield stage


@pytest.fixture
def multi_cluster_stage_with_layer_meta(stage):
    du = stage.deploy_units["asd"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "qwe"
    layers = pod_agent_spec.resources.layers
    box_layers = box_0.rootfs.layer_refs

    layer_0 = layers.add()
    layer_0.id = "base-layer-0"
    box_layers.append("base-layer-0")
    layer_0.url = "rbtorrent:version"

    layer_1 = layers.add()
    layer_1.id = "wtf"
    box_layers.append("wtf")
    layer_1.meta.sandbox_resource.task_id = "1337"
    attributes = layer_1.meta.sandbox_resource.attributes
    attributes["resource_name"] = "other"
    attributes["resource_version"] = "100500"

    yield stage


@pytest.fixture
def stage_with_layer_url(stage):
    du = stage.deploy_units["du"]
    rs = du.replica_set.replica_set_template
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "box"
    layers = pod_agent_spec.resources.layers
    box_layers = box_0.rootfs.layer_refs

    layer_0 = layers.add()
    layer_0.id = "not_layer"
    box_layers.append("not_layer")
    layer_0.url = "rbtorrent:fake"

    layer_1 = layers.add()
    layer_1.id = "layer"
    box_layers.append("layer")
    layer_1.url = "rbtorrent:version"

    yield stage


@pytest.fixture
def monster_stage(stage):
    # per cluster, 2 boxes
    du = stage.deploy_units["du1"]
    rs = du.replica_set.replica_set_template
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec
    du_layers = pod_agent_spec.resources.layers

    # два слоя
    box = pod_agent_spec.boxes.add()
    box.id = "qwe"
    box_layers = box.rootfs.layer_refs

    layer = du_layers.add()
    layer.id = "wtf"
    box_layers.append("wtf")
    layer.meta.sandbox_resource.task_id = "1337"
    attributes = layer.meta.sandbox_resource.attributes
    attributes["resource_name"] = "other"
    attributes["resource_version"] = "100500"

    layer = du_layers.add()
    layer.id = "zxc"
    box_layers.append("zxc")
    layer.url = 'rbtorrent:qwe'

    # 1 докерный слой
    box = pod_agent_spec.boxes.add()
    box.id = "my_box"

    image = du.images_for_boxes["my_box"]
    image.name = "my_app"
    image.tag = "1.2.3"

    # multi cluster, 1 box
    du = stage.deploy_units["asd"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec
    du_layers = pod_agent_spec.resources.layers

    # 2 слоя, базовый + тарбол
    box = pod_agent_spec.boxes.add()
    box.id = "box"
    box_layers = box.rootfs.layer_refs

    layer = du_layers.add()
    layer.id = "base-layer-0"
    box_layers.append("base-layer-0")
    layer.url = "rbtorrent:asd-qwe"

    layer = du_layers.add()
    layer.id = "app"
    box_layers.append("app")
    layer.url = "rbtorrent:bestappurl"
    layer.meta.sandbox_resource.task_id = "1337"
    attributes = layer.meta.sandbox_resource.attributes
    attributes["resource_name"] = "best_app"
    attributes["resource_version"] = "100500"

    # multi cluster, 1 box
    du = stage.deploy_units["qwerty"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec
    pod_agent_spec.resources.SetInParent()

    # 1 докерный слой
    box = pod_agent_spec.boxes.add()
    box.id = "not_my_box"

    image = du.images_for_boxes["not_my_box"]
    image.name = "not_my_app"
    image.tag = "4.5.6"

    yield stage


@pytest.fixture
def stage_with_docker_no_layers(stage):
    du = stage.deploy_units["my_deploy_unit"]
    rs = du.multi_cluster_replica_set.replica_set
    pod_agent_spec = rs.pod_template_spec.spec.pod_agent_payload.spec

    box_0 = pod_agent_spec.boxes.add()
    box_0.id = "my_box"

    image = du.images_for_boxes["my_box"]
    image.name = "my_app"
    image.tag = "1.2.3"

    yield stage


@pytest.fixture
def yp_api():
    mock = YpApiMock()

    yield mock


@pytest.fixture
def token(monkeypatch):
    os.environ["ROBOT_METRIKA_ADMIN_OAUTH"] = 'qwe'
    yield


@pytest.fixture
def deploy_pkg_version_getter(token):
    return pkg_api.YandexDeployPackageVersionGetter()


@pytest.fixture
def sandbox_api(populate_mock):
    yield lambda: sandbox_rest.Client()


def mock_deploy_api_answer(monkeypatch, answer):
    monkeypatch.setattr(mpd.DeployAPI, 'get_object', YpApiMock().get_object)
    monkeypatch.setattr(mpd.stage.Stage, 'get_stage_specification', answer)


@pytest.fixture
def mock_deploy_good(monkeypatch, multi_cluster_stage_with_layer_meta):
    def good_answer(*args, **kwargs):
        d = MessageToDict(multi_cluster_stage_with_layer_meta, preserving_proto_field_name=True)
        logging.debug("Generated dict: %s" % d)
        return d

    mock_deploy_api_answer(monkeypatch, good_answer)


@pytest.fixture
def mock_deploy_bad(monkeypatch):
    def bad_answer(*args, **kwargs):
        raise mpd.exceptions.DeployAPIObjectDoesNotExistException("There is no such stage: %s, %s" % (args, kwargs))

    mock_deploy_api_answer(monkeypatch, bad_answer)


@pytest.fixture
def populate_mock():
    with requests_mock.mock() as mock:
        mock.get(os.path.join(CLUSTER_BASE_URL, 'list/fqdn?group=mtlog'),
                 json={
                     'data': [
                         'mtlog03-02-7.yandex.ru'
                     ],
                     'result': True}, status_code=200)

        mock.get(os.path.join(pkg_lib.CONDUCTOR_BASE_URL, 'packages_on_host/mtlog03-02-7.yandex.ru?format=json'),
                 json=[
                     {
                         'name': 'bummer-lib-metrika-yandex',
                         'version': '2.9.777',
                         'upgrade': False,
                         'tags': ''
                     }], status_code=200)

        mock.get(os.path.join(CLUSTER_BASE_URL, 'list/fqdn?group=not_existing_group'),
                 json={
                     "data": [],
                     "reason": "No fqdn found by filter",
                     "result": False}, status_code=404)

        mock.get(os.path.join(pkg_lib.CONDUCTOR_BASE_URL, 'packages_on_host/not_existing_package?format=json'), status_code=404)

        mock.get(os.path.join(pkg_lib.CONDUCTOR_BASE_URL, 'package2hosts/not_existing_package'), status_code=404)

        mock.get(os.path.join(pkg_lib.CONDUCTOR_BASE_URL, 'package2hosts/bummer-lib-metrika-yandex'),
                 text='mtlog03-02-7.yandex.ru', status_code=200)

        mock.get(os.path.join(pkg_lib.CONDUCTOR_BASE_URL, 'package2hosts/asd'), status_code=404)

        mock.get(os.path.join(CLUSTER_BASE_URL, 'list/root_group?environment=testing'),
                 json={
                     'result': True,
                     'data': [
                         'mtlog'
                     ]}, status_code=200)

        mock.get(re.compile(sandbox_rest.Client.DEFAULT_BASE_URL),
                 json={
                     'items': [],
                     'limit': 1,
                     'offset': 0,
                     'total': 0,
                     }, status_code=200)

        mock.get(os.path.join(sandbox_rest.Client.DEFAULT_BASE_URL, "resource?limit=1&attrs=%7B%22rbtorrent%22%3A+%22rbtorrent%3Aqwe%22%7D"),
                 json={
                     'items': [
                         {
                             "attributes": {
                                 "resource_name": "asd",
                                 "resource_version": "qwe",
                             },
                         },
                     ],
                     'limit': 1,
                     'offset': 0,
                     'total': 1,
                     }, status_code=200)

        yield mock


@pytest.fixture
def rr_doesnt_exist():
    class FakeAPI(mpd.DeployAPI):
        def get_object(*args, **kwargs):
            raise mpd.exceptions.DeployAPIObjectDoesNotExistException()

    return FakeAPI(token='test')


@pytest.fixture
def rr_exists():
    class FakeAPI(mpd.DeployAPI):
        def get_object(*args, **kwargs):
            return ['exists']

    return FakeAPI(token='test')


@pytest.fixture
def rr_exists_with_versions(monkeypatch):
    class FakeAPI(mpd.DeployAPI):
        def get_object(*args, **kwargs):
            if kwargs['selectors'] == ['/spec/patches/update_binary_layer/sandbox/static']:
                return [{'deploy_unit_id': 'du', 'layer_ref': 'layer'}]
            elif kwargs['selectors'] == ['/meta/stage_id']:
                return ['stage']
            else:
                assert False

    def _get_all_versions(self):
        self.all_versions = {'du': {'box': {'layer': 1337}}}

    monkeypatch.setattr(pkg_lib.DeployVersionGetter, '_get_all_versions', _get_all_versions)
    return FakeAPI(token='test')


def make_object_history(history):
    class FakeDeployApi:
        def select_object_history(self, *args, **kwargs):
            return [
                {
                    'results': [
                        {'value': event['revision']},
                        {'value': event['revision_info']}
                    ],
                    'time': event['revision'],
                    'user': str(event['revision'])
                }
                for event in history
            ]

    return pkg_lib.DeployVersionGetter(FakeDeployApi(), None, 'test', None)


def make_revision(revision, revert=None):
    return {'revision': revision, 'revision_info': {'description': 'Reverting to Revision {}'.format(revert)} if revert else {}}


@pytest.fixture
def history():
    return make_object_history([
        make_revision(10),
        make_revision(9, 8),
        make_revision(8),
        make_revision(7, 6),
        make_revision(6, 5),
        make_revision(5),
        make_revision(4, 2),
        make_revision(3),
        make_revision(2),
        make_revision(1),
    ])


@pytest.fixture
def release_getter(monkeypatch):
    class FakeVersionGetter(pkg_lib.DeployVersionGetter):
        def _get_revision_info(self, *args, **kwargs):
            return datetime.utcfromtimestamp(0), 'from_revision'

        def get_version(self):
            return '1337'

        def get_info(self):
            return None, None, None, 'layer'

    class FakeAllVersionsGetter(pkg_lib.DeployAllVersionsGetter):
        stage_name = None
        stage_spec = {'revision': None}

    version_getter = FakeVersionGetter(None, None, 'test', None)
    version_getter.getter = FakeAllVersionsGetter(None, None)
    return version_getter


@pytest.fixture
def getter_with_release(release_getter):
    class FakeDeployApi:
        def find_sb_release_by_task_id(self, *args, **kwargs):
            return [{'sandbox': {'release_author': 'from_release'}}, {'id': '1337'}]

    release_getter.deploy_api = FakeDeployApi()
    release_getter.getter.layer_sb_tasks['layer'] = '1337'
    return release_getter


@pytest.fixture
def getter_without_release(release_getter):
    class FakeDeployApi:
        def find_sb_release_by_resource(self, *args, **kwargs):
            return None

    release_getter.deploy_api = FakeDeployApi()
    return release_getter
