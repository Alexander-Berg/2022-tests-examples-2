# -*- coding: utf-8 -*-
import datetime
import hashlib
import logging
import os
import sys
import time

from urllib3.connection import NewConnectionError

import sandbox.common.types.resource as ctr
import sandbox.projects.common.time_utils as tu
import sandbox.projects.common.task_env as task_env
import sandbox.projects.common.link_builder as lb
import sandbox.projects.common.error_handlers as eh
import sandbox.projects.common.binary_task as binary_task
import sandbox.projects.common.gsid_parser as gsid_parser
import sandbox.projects.balancer.resources as serval_res
import sandbox.projects.release_machine.helpers.events_helper as events_helper
import sandbox.projects.release_machine.security as rm_security
import sandbox.projects.release_machine.release_engine.resources as rm_resources
import sandbox.sdk2 as sdk2

from sandbox.sdk2.helpers import subprocess as sp


if sys.version_info[0:2] >= (3, 8):  # python 3.8 or higher
    from functools import cached_property
else:
    from sandbox.projects.common.decorators import memoized_property as cached_property


def log_task_test_status(f):

    def wrapped(task, *args, **kwargs):
        task.set_info(f.__name__)
        result = f(task, *args, **kwargs)
        task.set_info("... OK")
        return result

    return wrapped


class TestReleaseEngineBackend(binary_task.LastBinaryTaskRelease, sdk2.Task):

    RM_HOST = "localhost"
    RM_PORT = 50051
    WAIT_SERVICE_START_BEFORE_CHECK = 45
    WAIT_SERVICE_START_REQUEST_TIMEOUT = 60
    WAIT_SERVICE_START_REQUEST_RETRIES = 3

    class Parameters(binary_task.LastBinaryReleaseParameters):
        _lbrp = binary_task.binary_release_parameters(stable=True)
        release_machine_backend_binary = sdk2.parameters.Resource(
            "RM backend binary", resource_type=rm_resources.ReleaseMachineBinary, required=True
        )

    class Requirements(task_env.TinyRequirements):
        disk_space = 512  # 512 Mb
        ram = 2048  # 2 Gb

    @property
    def rm_url(self):
        return "{}:{}".format(self.RM_HOST, self.RM_PORT)

    @cached_property
    def rm_event_client(self):
        from release_machine.release_machine.services.release_engine.services.Event import EventClient
        return EventClient.from_address(self.rm_url)

    @cached_property
    def rm_model_client(self):
        from release_machine.release_machine.services.release_engine.services.Model import ModelClient
        return ModelClient.from_address(self.rm_url)

    def on_execute(self):

        self._post_proto_event(self.status)

        release_machine_binary_path = str(sdk2.ResourceData(self.Parameters.release_machine_backend_binary).path)
        logging.info("Binary path: %s", release_machine_binary_path)
        serval_binary = sdk2.Resource[serval_res.ServalExecutable].find(
            state=ctr.State.READY,
            attrs={"released": "stable"}
        ).first()
        logging.info("Got serval binary: %s", serval_binary)
        serval_path = str(sdk2.ResourceData(serval_binary).path)
        logging.info("Serval path: %s", serval_path)
        serval_configs_path = "serval_configs"
        sdk2.vcs.svn.Arcadia.export(
            "arcadia:/arc/trunk/arcadia/release_machine/release_machine/serval_configs",
            serval_configs_path,
            revision=self.Parameters.release_machine_backend_binary.arcadia_revision,
        )

        db_url = rm_security.get_rm_token(self, token_name="release_engine_db_test_url")

        with sdk2.helpers.ProcessLog(self, logger="rm_run") as rm_process_log:

            with sdk2.helpers.ProcessLog(self, logger="serval_run") as serval_process_log:

                rm_proc = sp.Popen(
                    [
                        release_machine_binary_path,
                        "run",
                        "server",
                        "model",
                        "stats",
                        "event",
                        "notification",
                        "testenv",
                        "state",
                        "idm",
                    ],
                    stdout=rm_process_log.stdout,
                    stderr=rm_process_log.stdout,
                    env={
                        "DB_URL": db_url,
                        "DEBUG": "1",
                        "LOGGING_LEVEL": "DEBUG",
                        "LOGGING_STDOUT": "1",
                        "LOGGING_INFRA_DEBUG": "1",
                    },
                )

                serval_proc = sp.Popen(
                    [serval_path, "--config", os.path.join(serval_configs_path, "serval_config.yaml")],
                    stdout=serval_process_log.stdout, stderr=serval_process_log.stderr,
                )

                self.set_info("Waiting {} seconds for service to start".format(self.WAIT_SERVICE_START_BEFORE_CHECK))
                time.sleep(self.WAIT_SERVICE_START_BEFORE_CHECK)

                self._check_service_started()

                self.set_info("Consider service started")

                self.test_get_components()
                self.test_get_scopes()
                self.test_get_scopes_tagged()

                rm_proc.kill()
                serval_proc.kill()

    def _check_service_started(self):
        from release_machine.release_machine.proto.structures import message_pb2
        from search.martylib.core.exceptions import MaxRetriesReached

        try:

            self.rm_model_client.get_components(
                request=message_pb2.Dummy(),
                timeout=self.WAIT_SERVICE_START_REQUEST_TIMEOUT,
                retries=self.WAIT_SERVICE_START_REQUEST_RETRIES,
            )

        except MaxRetriesReached:
            eh.check_failed(
                "ReleaseMachine service was unable to start. Failed after {} tries".format(
                    self.WAIT_SERVICE_START_REQUEST_RETRIES
                ),
            )

    @log_task_test_status
    def test_get_components(self):

        import grpc

        from release_machine.common_proto import events_pb2
        from release_machine.release_machine.proto.structures import message_pb2

        component_name = "get_components_test"

        self.rm_event_client.post_proto_events(
            request=message_pb2.PostProtoEventsRequest(events=[
                events_pb2.EventData(
                    general_data=events_pb2.EventGeneralData(
                        hash=hashlib.md5("{}{}".format(
                            datetime.datetime.now(),
                            "test_get_components",
                        ).encode("utf-8")).hexdigest(),
                        component_name=component_name,
                        referrer="test",
                    ),
                    component_update_data=events_pb2.ComponentUpdateData(
                        responsible="ilyaturuntaev",
                        display_name="Test Component",
                        release_cycle="branched",
                        te_db="",
                    ),
                ),
            ]),
        )

        self._check_component(component_name)

        for wait_time in range(4, -1, -1):
            try:
                components = self.rm_model_client.get_components()
            except (NewConnectionError, IOError):
                time.sleep(30)
                logging.debug("Wait for service start")
                eh.ensure(not wait_time, "Failed to establish new connection with Release Engine")
                continue
            except grpc.RpcError as rpc_error:
                eh.check_failed(
                    "Failed to get JSON data for get_components method, grpc error code: {}".format(rpc_error.code())
                )
            else:
                eh.ensure(len(components.components), "No data in Release Engine response")
                break

        self._delete_component(component_name)

    @log_task_test_status
    def test_get_scopes(self):

        from release_machine.common_proto import events_pb2
        from release_machine.release_machine.proto.structures import message_pb2

        component_name = "test_component_{}".format(self.id)

        # Post new component event
        # Post new Branch event
        # Post new changelog event
        # Check get_scopes response

        self.rm_event_client.post_proto_events(message_pb2.PostProtoEventsRequest(events=[
            events_pb2.EventData(
                general_data=events_pb2.EventGeneralData(
                    hash=hashlib.md5("{}{}compupdate".format(datetime.datetime.now(), component_name)).hexdigest(),
                    component_name=component_name,
                    referrer="test",
                ),
                component_update_data=events_pb2.ComponentUpdateData(
                    responsible="ilyaturuntaev",
                    display_name="Test Component",
                    release_cycle="branched",
                    te_db="",
                ),
            ),
        ]))

        self._check_component(component_name)

        self.rm_event_client.post_proto_events(message_pb2.PostProtoEventsRequest(events=[
            events_pb2.EventData(
                general_data=events_pb2.EventGeneralData(
                    hash=hashlib.md5("{}{}newbranch".format(datetime.datetime.now(), component_name)).hexdigest(),
                    component_name=component_name,
                    referrer="test"
                ),
                new_branch_data=events_pb2.NewBranchData(
                    base_commit_id="1",
                    first_commit_id="2",
                    arcadia_path="test_arcadia_path",
                    branch_created_at_timestamp=int(time.time()),
                    scope_number="1",
                    job_name="_NEW_BRANCH__TEST",
                ),
            ),
            events_pb2.EventData(
                general_data=events_pb2.EventGeneralData(
                    hash=hashlib.md5("{}{}newtag".format(datetime.datetime.now(), component_name)).hexdigest(),
                    component_name=component_name,
                    referrer="test"
                ),
                new_tag_data=events_pb2.NewTagData(
                    base_commit_id="2",
                    first_commit_id="3",
                    arcadia_path="test_arcadia_path",
                    tag_created_at_timestamp=int(time.time()),
                    scope_number="1",
                    tag_number="1",
                    tag_name="stable-1-1",
                    job_name="_NEW_TAG__TEST",
                ),
            ),
            events_pb2.EventData(
                general_data=events_pb2.EventGeneralData(
                    hash=hashlib.md5("{}{}changelog".format(datetime.datetime.now(), component_name)).hexdigest(),
                    component_name=component_name,
                    referrer="test"
                ),
                changelog_created_data=events_pb2.ChangelogCreatedData(
                    scope_number="1",
                    tag_number="1",
                    job_name="_CHANGELOG__TEST",
                    changelog_resource_id="123123123",
                ),
            ),
        ]))

        self._check_get_scopes(component_name)
        self._delete_component(component_name)

    @log_task_test_status
    def test_get_scopes_tagged(self):

        from release_machine.common_proto import events_pb2
        from release_machine.release_machine.proto.structures import message_pb2

        component_name = "test_tagged_component_{}".format(self.id)

        # Post new component event
        # Post new Tag event
        # Check get_scopes response

        self.rm_event_client.post_proto_events(message_pb2.PostProtoEventsRequest(events=[
            events_pb2.EventData(
                general_data=events_pb2.EventGeneralData(
                    hash=hashlib.md5("{}{}compupdate".format(datetime.datetime.now(), component_name)).hexdigest(),
                    component_name=component_name,
                    referrer="test",
                ),
                component_update_data=events_pb2.ComponentUpdateData(
                    responsible="ilyaturuntaev",
                    display_name="Test Component",
                    release_cycle="branched",
                    te_db="",
                ),
            ),
        ]))

        self._check_component(component_name)

        self.rm_event_client.post_proto_events(message_pb2.PostProtoEventsRequest(events=[
            events_pb2.EventData(
                general_data=events_pb2.EventGeneralData(
                    hash=hashlib.md5("{}{}newtag".format(datetime.datetime.now(), component_name)).hexdigest(),
                    component_name=component_name,
                    referrer="test"
                ),
                new_tag_data=events_pb2.NewTagData(
                    base_commit_id="1",
                    first_commit_id="2",
                    arcadia_path="test_arcadia_path",
                    tag_created_at_timestamp=int(time.time()),
                    scope_number="1",
                    tag_number="1",
                    tag_name="stable-1",
                    job_name="_NEW_TAG__TEST",
                ),
            ),
        ]))

        self._check_get_scopes(component_name)
        self._delete_component(component_name)

    def _check_component(self, component_name):
        from release_machine.release_machine.proto.structures import message_pb2

        component = self.rm_model_client.get_component(message_pb2.ComponentRequest(component_name=component_name))

        eh.verify(component, "Get component check failed. Component does not exist.")
        logging.debug("[component_check] Component name from RM: %s", component.name)

    def _check_get_scopes(self, component_name):
        import grpc
        from release_machine.release_machine.proto.structures import message_pb2

        try:
            self.rm_model_client.get_scopes(message_pb2.ScopesRequest(component_name=component_name))
        except grpc.RpcError:
            eh.check_failed("Get scopes check failed. Failed to get JSON data.")

    def _delete_component(self, component_name):

        import grpc
        from release_machine.release_machine.proto.structures import message_pb2

        logging.debug("Delete component %s", component_name)

        self.rm_model_client.delete_component(
            message_pb2.DeleteComponentRequest(component_name=component_name, irreversible=True),
        )

        try:
            get_component_response = self.rm_model_client.get_component(
                message_pb2.ComponentRequest(component_name=component_name)
            )
        except grpc.RpcError as rpc_error:
            eh.ensure(
                rpc_error.code() == grpc.StatusCode.NOT_FOUND,
                "Failed to delete component: getComponent returned grpc code {}".format(rpc_error.code()),
            )
        else:
            eh.fail("Failed to delete component: getComponent returned {}".format(get_component_response))

    @property
    def is_binary_run(self):
        return self.Parameters.binary_executor_release_type != 'none'

    def on_finish(self, prev_status, status):
        self._post_proto_event(status, "OK" if status == 'SUCCESS' else "CRIT")

    def _post_proto_event(self, task_status=None, test_result_status="ONGOING"):
        task_status = task_status or self.status
        event = self._construct_generic_test_event(
            task_status=task_status,
            test_result_status=test_result_status,
        )
        if not event:
            return
        try:
            events_helper.post_proto_events([event])
        except Exception as e:
            eh.log_exception("Unable to post proto event {}".format(event), e)

    def _construct_generic_test_event(self, task_status, test_result_status):
        if not self.is_binary_run:
            logging.debug("The task is not run in a binary mode so no proto event is going to be sent")
            return

        try:
            from release_machine.common_proto import events_pb2, test_results_pb2
        except ImportError:
            logging.exception("Unable to import Release Machine proto module. Is this a binary run?")
            return

        now_utc_iso = tu.datetime_utc_iso()
        job_name = gsid_parser.get_job_name_from_gsid(self.Context.__GSID)
        revision = gsid_parser.get_svn_revision_from_gsid(self.Context.__GSID)
        scope_number = self.Context.testenv_database.rsplit('-', 1)[-1]

        return events_pb2.EventData(
            general_data=events_pb2.EventGeneralData(
                component_name=u"release_machine",
                referrer=u"sandbox_task:{}".format(self.id),
                hash=hashlib.md5(u"{}{}{}".format(self.id, task_status, now_utc_iso)).hexdigest(),
            ),
            task_data=events_pb2.EventSandboxTaskData(
                task_id=self.id,
                status=task_status,
                created_at=self.created.isoformat(),
                updated_at=now_utc_iso,
            ),
            generic_test_data=events_pb2.GenericTestData(
                job_name=job_name,
                scope_number=scope_number,
                revision=revision,
                test_result=test_results_pb2.TestResult(
                    status=getattr(
                        test_results_pb2.TestResult.TestStatus,
                        test_result_status,
                        test_results_pb2.TestResult.TestStatus.ONGOING,
                    ),
                    task_link=lb.task_link(self.id, plain=True),
                ),
            ),
        )
