import random
import cPickle
import httplib

import mock
import pytest

from sandbox import common

import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
import sandbox.common.types.resource as ctr

from sandbox import sdk2
from sandbox import taskbox
from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.controller import task as task_controller

import sandbox.taskbox.errors as tb_errors
import sandbox.taskbox.client.protocol as tb_protocol


@pytest.fixture()
def db_connection(clear_mongo_uri):
    mapping.ensure_connection(clear_mongo_uri)


def taskboxer_common_resource(id_):
    return mapping.Resource(
        id=id_,
        type=sdk2.service_resources.SandboxTasksBinary.name, state=ctr.State.READY,
        size=0, arch=ctm.OSFamily.ANY, name="-", path="-", owner="-",
        task_id=100500, time=mapping.Resource.Time(),
        attributes=[
            mapping.Resource.Attribute(key=k, value=v)
            for k, v in (
                (ctr.BinaryAttributes.BINARY_AGE, str(taskbox.AGE)),
                (ctr.BinaryAttributes.TASKBOX_ENABLED, "1"),
            )
        ],
    ).save()


@pytest.fixture()
def taskboxer_resource(db_connection):
    return taskboxer_common_resource(1337)


@pytest.fixture()
def taskboxer_resource2(db_connection):
    return taskboxer_common_resource(1339)


@pytest.fixture()
def parameters_meta_mapping(db_connection):
    return mapping.ParametersMeta


@pytest.fixture()
def container_resource(db_connection):
    r = mapping.Resource(
        id=1338, type=sdk2.service_resources.LxcContainer.name, state=ctr.State.READY,
        size=0, arch=ctm.OSFamily.ANY, name="-", path="-", owner="-",
        task_id=100500, time=mapping.Resource.Time(),
        attributes=[
            mapping.Resource.Attribute(key="released", value=ctt.ReleaseStatus.STABLE),
            mapping.Resource.Attribute(key="platform", value=sdk2.parameters.Container.platform)
        ]
    )
    return r.save()


@pytest.fixture()
def taskboxed_task_model(taskboxer_resource, rest_session_login, rest_session_group, db_connection):
    model = mapping.Task(type="TASKBOXER_TASK", author=rest_session_login, owner=rest_session_group)
    model.requirements = model.Requirements()
    model.requirements.tasks_resource = model.Requirements.TasksResource(id=taskboxer_resource.id, age=taskbox.AGE)
    return model


@pytest.fixture()
def taskboxed_task_wrapper(taskboxed_task_model, serviceapi, taskbox, dispatcher, db_connection, request_env):
    return task_controller.TBWrapper(taskboxed_task_model)


def test__run_taskbox(dispatcher):

    x = random.randrange(1024)
    assert x == dispatcher.ping(x)


def test__base_task_hooks(taskboxed_task_model, container_resource, dispatcher):
    model = taskboxed_task_model
    model.requirements.container_resource = container_resource.id
    req = tb_protocol.TaskboxRequest("init_model", model)
    raw_resp = dispatcher("call", model.requirements.tasks_resource.id, req.encode(), "testcall", __no_wait=True).wait()
    resp = tb_protocol.TaskboxResponse.decode(raw_resp, req)
    context = cPickle.loads(resp.model.context)

    assert resp.model.description == "Taskboxer!"
    assert context.get("some_number") == 1


@pytest.mark.usefixtures("serviceapi", "taskbox", "dispatcher")
def test__task_wrapper(
    taskboxed_task_model, taskboxed_task_wrapper, container_resource,
):
    from sandbox.projects.sandbox.taskboxer import internal

    if not common.system.inside_the_binary():
        taskboxed_task_model.parameters = taskboxed_task_model.Parameters(
            input=[taskboxed_task_model.Parameters.Parameter(key="check_rest_from_server_hooks", value=True)]
        )

    tw = taskboxed_task_wrapper
    tw.init_model()

    # Check initial values
    for k, v in dict(internal.Context).items():
        assert tw.ctx.get(k) == v
    assert tw.model.description == internal.Parameters.description.default
    assert tw.model.requirements.container_resource == container_resource.id
    assert tw._task().Requirements.container_resource.id == container_resource.id

    tw.create().on_create().on_save()
    assert tw.model.requirements.container_resource == container_resource.id
    # `ctx` is a `singleton_property`, force update it
    del tw.ctx

    assert tw.ctx.get("on_create_done") is True
    assert tw.ctx.get("on_create_count") == 1
    assert tw.ctx.get("on_save_done") is True
    assert tw.ctx.get("on_save_count") == 1

    if not common.system.inside_the_binary():
        assert tw.ctx.get("on_create_task_id_from_rest") == tw.id
        assert tw.ctx.get("on_create_non_existent_task_from_rest") == httplib.NOT_FOUND
        assert tw.ctx.get("on_create_non_existent_path_from_rest") == httplib.NOT_FOUND
        assert tw.ctx.get("on_create_create_task_from_rest") == httplib.INTERNAL_SERVER_ERROR

        assert tw.ctx.get("on_save_task_id_from_rest") == tw.id
        assert tw.ctx.get("on_save_non_existent_task_from_rest") == httplib.NOT_FOUND
        assert tw.ctx.get("on_save_non_existent_path_from_rest") == httplib.NOT_FOUND
        assert tw.ctx.get("on_save_create_task_from_rest") == httplib.INTERNAL_SERVER_ERROR

    tw.on_save()
    # `ctx` is a `singleton_property`, force update it
    del tw.ctx

    assert tw.ctx.get("on_save_done") is True
    assert tw.ctx.get("on_save_count") == 2
    assert tw.model.requirements.container_resource == container_resource.id

    er = tw.on_enqueue()
    assert er.new_status == ctt.Status.WAIT_TIME

    # `ctx` is a `singleton_property`, force update it
    del tw.ctx

    assert tw.ctx.get("on_enqueue_done") is True
    assert tw.ctx.get("on_enqueue_count") == 1

    if not common.system.inside_the_binary():
        assert tw.ctx.get("on_enqueue_task_id_from_rest") == tw.id
        assert tw.ctx.get("on_enqueue_non_existent_task_from_rest") == httplib.NOT_FOUND
        assert tw.ctx.get("on_enqueue_non_existent_path_from_rest") == httplib.NOT_FOUND
        assert tw.ctx.get("on_enqueue_create_task_from_rest") == httplib.INTERNAL_SERVER_ERROR

    er = tw.on_enqueue()
    assert er.new_status == ctt.Status.ENQUEUING

    # `ctx` is a `singleton_property`, force update it
    del tw.ctx

    assert tw.ctx.get("on_enqueue_done") is True
    assert tw.ctx.get("on_enqueue_count") == 2


def test__tbwrapper_parameters_meta(
    taskboxed_task_wrapper, taskboxer_resource, taskboxer_resource2, parameters_meta_mapping
):
    from sandbox.projects.sandbox.taskboxer import internal

    tw = taskboxed_task_wrapper
    assert tw.model.parameters_meta is None
    tw.init_model()
    assert tw.model.parameters_meta
    tw.create().on_create()

    parameters_meta = tw.parameters_meta
    assert tw.model.parameters_meta.params == parameters_meta.params
    taskbox_call_mock = mock.Mock(return_value=parameters_meta_mapping(params=[]))
    taskbox_call, tw._tb._taskbox_call = tw._tb._taskbox_call, taskbox_call_mock

    del tw.parameters_meta
    try:
        assert tw.parameters_meta.params == parameters_meta.params
    finally:
        tw._tb._taskbox_call = taskbox_call
    assert not taskbox_call_mock.called
    assert sorted([_.name for _ in parameters_meta.params]) == sorted([_.name for _ in internal.Parameters])

    tw.update_context(dict(new_tasks_resource=taskboxer_resource2.id))
    tw.on_enqueue()
    tw._tb._taskbox_call = taskbox_call_mock

    del tw.parameters_meta
    try:
        assert tw.parameters_meta.params == []
    finally:
        tw._tb._taskbox_call = taskbox_call
    assert taskbox_call_mock.called

    tw.update_context(dict(new_tasks_resource=taskboxer_resource.id))
    tw.on_enqueue()

    del tw.parameters_meta
    assert tw.parameters_meta.params == parameters_meta.params

    assert parameters_meta_mapping.objects.count() == 2


def test__tbwrapper_parameters(taskboxed_task_wrapper):
    tw = taskboxed_task_wrapper
    tw.init_model()

    for validate_only in (True, False):
        update_result = tw.update_parameters(
            {"not_existed_param": "whatever", "int_param": 111},
            {"result": "answer"},
            {},
            validate_only
        )
        assert "No task field" in update_result.errors["not_existed_param"], validate_only
        assert "ValueError" in update_result.errors["result"], validate_only
        ipp_dict, opp_dict = tw.parameters_dicts()
        assert (ipp_dict["int_param"] != 111) == validate_only
        assert (opp_dict.get("result") != "answer") == validate_only

    update_result = tw.update_parameters({"not_existed_param": "whatever", "str_param": "test"}, {}, {}, False)
    assert "No task field" in update_result.errors["not_existed_param"]
    ipp_dict, opp_dict = tw.parameters_dicts()
    assert ipp_dict["str_param"] == "test"
    assert opp_dict["result"] == "answer"  # Previous invalid value was saved. Legacy.

    tw.update_parameters({"result": "test"}, {}, {}, False)  # Output param in input dict. Ignored case.
    assert tw.parameters_dicts()[1]["result"] == "answer"
    with pytest.raises(tb_errors.OutputParameterReassign) as ex:
        tw.update_parameters({}, {"result": "test"}, {}, False)
    assert isinstance(ex.value.args[0], list) and "result" in ex.value.args[0]


def test__exceptions_on_hook(taskboxed_task_wrapper):
    tw = taskboxed_task_wrapper
    tw.init_model()

    tw.update_parameters({"raise_exception_on_hook": "on_create"}, {}, {}, False)
    try:
        tw.on_create()
    except common.joint.errors.ServerError as ex:
        assert "raise TypeError" in ex.tb[-2]
        assert "TypeError" in ex.tb[-1]
    else:
        raise AssertionError("common.joint.errors.ServerError must be raised")

    tw.update_parameters({"raise_exception_on_hook": "on_save"}, {}, {}, False)
    try:
        tw.on_create()
    except common.joint.errors.ServerError as ex:
        assert "raise KeyError" in ex.tb[-2]
        assert "KeyError" in ex.tb[-1]

    tw.update_parameters({"raise_exception_on_hook": "on_enqueue"}, {}, {}, False)
    try:
        tw.on_enqueue()
    except common.joint.errors.ServerError as ex:
        assert "raise ValueError" in ex.tb[-2]
        assert "ValueError" in ex.tb[-1]


def test__tbwrapper_reports(taskboxed_task_wrapper):
    from sandbox.projects.sandbox.taskboxer import internal

    tw = taskboxed_task_wrapper
    tw.init_model()

    with pytest.raises(tb_errors.UnknownReportName):
        tw.report("unknown_report")

    for report_name in ("footer", "header"):
        assert report_name in tw.report(report_name)

    report = tw.report("context_report")
    for k, _ in internal.Context:
        assert k in report

    reports = tw.reports
    assert reports == tw.model.reports
    assert set(report.label for report in reports) == {"footer", "header", "context_report"}

    release_template = tw.release_template()
    assert release_template == dict(internal.RELEASE_TEMPLATE)
