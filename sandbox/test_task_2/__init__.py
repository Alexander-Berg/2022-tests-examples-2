# coding: utf-8

import io
import os
import sys
import math
import time
import json
import random
import shutil
import logging
import getpass
import textwrap
import calendar
import aniso8601
import threading
import collections
import datetime as dt

import six
from six.moves import queue as Queue

from sandbox import common
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc
import sandbox.common.types.resource as ctr
import sandbox.common.types.notification as ctn

from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess as sp

import sandbox.projects.sandbox.resources as sb_resources
import sandbox.projects.common.constants as consts

running_on_windows = sys.platform == "win32"


class ActionFlow(common.enum.Enum):
    common.enum.Enum.lower_case()

    CONSECUTIVE = None
    PARALLEL = None


EXCEPTION_MAPPING = {
    exc_class.__name__: exc_class
    for exc_class in (
        common.errors.TaskError,
        KeyboardInterrupt,
        BaseException,
    )
}


ARC_TOKEN_NAME = "arc-token"


def _cqueue_pinger(hosts_list, timeout):
    # noinspection PyUnresolvedReferences
    import api.cqueue
    result = []
    with api.cqueue.Client(implementation="cqudp") as client:
        for host, res, err in client.ping(hosts_list).wait(timeout=timeout):
            result.append("{host}: {res}".format(host=host, res="Okay" if not err else err))
    return result


class TestTask2Resource(sdk2.Resource):
    """ Test resource """
    # common attributes
    releasers = ["guest", "test-robot-api-test", "robot-geosearch"]
    release_subscribers = ["sdfsdf", "ggggggggg", "testtesttesttest"]
    releasable = True
    restart_policy = ctr.RestartPolicy.DELETE  # default value, may be changed for particular resource

    # custom attributes
    test_attr = sdk2.parameters.Integer("Test attribute", default=None)
    test_required_attr = sdk2.parameters.String("Test required attribute", required=True, default="value")


class LastResource(sdk2.parameters.Resource):

    resource_type = TestTask2Resource.name

    @common.patterns.classproperty
    def default_value(cls):
        items = sdk2.Task.server.resource.read(
            type=cls.resource_type,
            attrs={"released": ctt.ReleaseStatus.STABLE},
            limit=1,
        )["items"]
        if items:
            return items[0]["id"]
        else:
            return None


class TestTask2(sdk2.ServiceTask):  # Use sdk2.Task as base class in your task class
    """
    A test task is widely used by Sandbox build-time tests and also by Sandbox developers to check new releases

    Following commonly used behaviours can be checked by the task:

    - Resources management
    - Child tasks creation and monitoring
    - Multi-threading
    - ... and much more!
    """

    class Requirements(sdk2.Requirements):
        ram = 512
        disk_space = 3522
        client_tags = ctc.Tag.GENERIC | ctc.Tag.MULTISLOT | ctc.Tag.SERVER | ctc.Tag.Group.OSX
        cores = 1

    class Parameters(sdk2.Parameters):
        # common parameters
        description = "Test"
        max_restarts = 10
        kill_timeout = 3600
        tcpdump_args = "-v 'host ya.ru'"

        # custom parameters
        overwrite_client_tags = sdk2.parameters.Bool("Overwrite client tags", default=False)
        with overwrite_client_tags.value[True]:
            client_tags = sdk2.parameters.ClientTags(
                "Client tags",
                default=ctc.Tag.GENERIC | ctc.Tag.MULTISLOT | ctc.Tag.SERVER | ctc.Tag.Group.OSX
            )
        with sdk2.parameters.Group("Lifetime parameters") as life_block:
            prep_live_time = sdk2.parameters.Integer("Time to live in preparing", required=True)
            live_time = sdk2.parameters.Integer("Time to live", default=10, required=True)
            fin_live_time = sdk2.parameters.Integer("Time to live in finishing", required=True)
            break_time = sdk2.parameters.Integer("Time to break")
            termination_time = sdk2.parameters.Integer("Time to terminate (on signal handling)")
            raise_exception_on_start = sdk2.parameters.Bool("Raise exception on task start")
            with raise_exception_on_start.value[True]:
                with sdk2.parameters.String("Exception class", multiline=True) as exc_class:
                    for k, v in EXCEPTION_MAPPING.items():
                        exc_class.values[k] = exc_class.Value(v.__name__)

            raise_exception_on_enqueue = sdk2.parameters.Bool("Raise exception on enqueue")
            with sdk2.parameters.String("Go to state", multiline=True) as go_to_state:
                go_to_state.values.SUCCESS = go_to_state.Value(default=True)
                go_to_state.values.TEMPORARY = None  # implicitly set to "TEMPORARY"
                go_to_state.values.EXCEPTION = go_to_state.Value(ctt.Status.EXCEPTION)
                go_to_state.values.FAILURE = "Go to state 'FAILURE'"
                go_to_state.values.STOPPED = None
            use_no_timeout = sdk2.parameters.Bool("If the task times out during \"Time to live\", switch to TEMPORARY")
            sleep_in_subprocess = sdk2.parameters.Bool("Sleep in subprocess")
            use_cgroup = sdk2.parameters.Bool("Create cgroup and run subprocess")
            suspend = sdk2.parameters.Bool("Suspend before finish")
            wait_time = sdk2.parameters.Integer("Wait for timeout", required=True)
            wait_on_enqueue = sdk2.parameters.Integer("Wait on enqueue")
            wait_task_on_enqueue = sdk2.parameters.List("Wait for tasks on enqueue")
            stop_on_enqueue = sdk2.parameters.Bool("Stop on enqueue")
            kill_executor = sdk2.parameters.Bool("Kill executor via unhandleable exception")
            expires_on_enqueue = sdk2.parameters.Integer("Expire in N seconds (set in on_enqueue)")
            expires_on_execute = sdk2.parameters.Integer("Expire in N seconds (set in on_execute)")
            run_actions = sdk2.parameters.Bool("Test actions using ProgressMeter", default=False)
            with run_actions.value[True]:
                with sdk2.parameters.String("Actions flow") as actions_flow:
                    for v in ActionFlow:
                        actions_flow.values[v] = v
                actions = sdk2.parameters.Dict("Actions (duration in seconds -> number of steps); omit for randomness")

        create_sub_task = sdk2.parameters.Bool("Create subtask")
        with create_sub_task.value[True]:
            subtasks_block = sdk2.parameters.Info("Subtasks Parameters")
            number_of_subtasks = sdk2.parameters.Integer("Number of subtasks", default=1)
            save_stages = sdk2.parameters.Bool("Save subtasks audit to STAGES")
            subtask_exec_limit = sdk2.parameters.Integer("Simultaneously execution limit using semaphore")
            create_public_semaphore = sdk2.parameters.Bool("Create public auto semaphore")
            subtask_wait_time = sdk2.parameters.Integer("Subtask wait time")
        with sdk2.parameters.Group("Resources Parameters") as resource_block:
            dependent_resource = sdk2.parameters.LastReleasedResource(
                "Dependent resource",
                resource_type=TestTask2Resource,
                state=(ctr.State.READY, ctr.State.NOT_READY),
                required=False
            )
            dependent_resources = sdk2.parameters.LastReleasedResource(
                "Dependent resources",
                resource_type=TestTask2Resource,
                state=(ctr.State.READY, ctr.State.NOT_READY),
                required=False,
                multiple=True
            )
            auto_resource = LastResource("Resource with default value")
            sync_resource_in_subprocess = sdk2.parameters.Bool("Sync resource with Synchrophazotron")
            create_resources = sdk2.parameters.Bool("Create resources", default=True)
            with create_resources.value[True]:
                create_resources_file_size = sdk2.parameters.Integer("Size (file), bytes", default=1024)
                single_file_resource_in_dir = sdk2.parameters.Bool("Create single file resource in directory")
                create_resources_dir_size = sdk2.parameters.Integer("Size (directory), bytes", default=4096)
                create_tar_resource = sdk2.parameters.Bool("Create resource with tar archive")
                create_tgz_resource = sdk2.parameters.Bool("Create resource with tgz archive")
            create_empty_resource = sdk2.parameters.Bool("Create empty resource")
            create_resource_on_enqueue = sdk2.parameters.Bool("Create resource on enqueue")
            modify_resource = sdk2.parameters.Bool("Modify resource")
            create_resource_ttl_inf = sdk2.parameters.Bool("Create resource with ttl:inf")
            create_parent_resource = sdk2.parameters.Bool("Create parent resource")
            create_parent_resource_on_enqueue = sdk2.parameters.Bool("Create parent resource on enqueue")
            pass_resources_to_subtasks = sdk2.parameters.Bool("Pass resources to subtasks")
            parent_resource = sdk2.parameters.ParentResource("External resource passed from parent")
            check_coredump = sdk2.parameters.Bool("Check coredump")
            create_custom_logs = sdk2.parameters.Bool("Create resource with custom logs")
            mount_image = sdk2.parameters.Resource(
                "Resource with SquashFS image to mount",
                resource_type=sb_resources.SandboxTasksImage,
                required=False
            )
            mount_image_with_synchrophazotron = sdk2.parameters.Bool(
                "Mounting SquashFS image via synchrophazotron and AgentR", default=False
            )
            mount_overlay = sdk2.parameters.Bool("Test mounting directories via AgentR")
            with mount_overlay.value[True]:
                mount_overlay_with_synchrophazotron = sdk2.parameters.Bool(
                    "Mounting directories via synchrophazotron and AgentR", default=False
                )
            do_not_unmount = sdk2.parameters.Bool("Do not unmount")

        with sdk2.parameters.Group("Vault Parameters") as vault_block:
            check_vault = sdk2.parameters.Bool("Check vault data")
            with check_vault.value[True]:
                vault_item_owner = sdk2.parameters.String("Vault item owner")
                vault_item_name = sdk2.parameters.String("Vault item name", default="test_data")
                expected_secret = sdk2.parameters.String(
                    "Expected contents of the item", default="test vault data for test task"
                )
        with sdk2.parameters.Group("Subversion Parameters") as subversion_block:
            test_get_arcadia_url = sdk2.parameters.ArcadiaUrl("Path to Arcadia svn", default="", required=False)
            build_with_arcadiasdk = sdk2.parameters.Bool("Do a test build with Arcadia SDK")
            with build_with_arcadiasdk.value[True]:
                use_arc = sdk2.parameters.Bool("Use arc instead of aapi")
                with use_arc.value[True]:
                    arc_secret = sdk2.parameters.YavSecret(
                        "Yav secret with OAuth token (the key should be '{}')".format(ARC_TOKEN_NAME), required=True
                    )

        with sdk2.parameters.Group("Notification Parameters") as notification_block:
            send_email_to_recipient = sdk2.parameters.Bool("Send test email")
            with send_email_to_recipient.value[True]:
                email_recipient = sdk2.parameters.String("Email recipient")
                mark_as_urgent = sdk2.parameters.Bool("Mark as urgent (send from sandbox-urgent@)", default=False)

        with sdk2.parameters.Group("Output Parameters") as output_params_block:
            wait_for_output_parameters = sdk2.parameters.Bool("Wait for output parameters")
            with wait_for_output_parameters.value[True]:
                output_param_targets = sdk2.parameters.Dict(
                    "Output param targets (task id/comma-separated param names)"
                )
                wait_output_all = sdk2.parameters.Bool("Wait all")
                wait_output_on_enqueue = sdk2.parameters.Bool("Wait on enqueue")

        with sdk2.parameters.Group("Miscellaneous Parameters") as misc_block:
            ramdrive = sdk2.parameters.Integer("Create a RAM drive of specified size in GiB")
            create_ramdir_on_prepare = sdk2.parameters.Bool("Create directory in ramdrive from `on_prepare`")
            create_ramdir_on_execute = sdk2.parameters.Bool("Create directory in ramdrive from `on_execute`")
            privileged = sdk2.parameters.Bool("Run under root privileges")
            _container = sdk2.parameters.Container(
                "Container", default=None, required=False, resource_type=sb_resources.LXC_CONTAINER
            )
            ping_host_via_skynet = sdk2.parameters.String(
                "Pass hostnames separated with comma in old style syntax (e.g. sandbox0{1..4}h)"
            )
            create_independent_task = sdk2.parameters.Bool("Create independent task")
            check_ssh_agent = sdk2.parameters.Bool("Check ssh agent")
            write_to_syslog = sdk2.parameters.String("Write a message to syslog")
            with sdk2.parameters.CheckGroup("Just a multiselect field") as multiselect:
                multiselect.values.option1 = "Option One"
                multiselect.values.option2 = multiselect.Value("Option Two", checked=True)
                multiselect.values.option3 = "Option Three"
            list_of_strings = sdk2.parameters.List(
                "Dynamic parameter of type 'List'", default=["aaa", "bbb", "ccc"],
                description="Description for List parameter"
            )
            dict_of_strings = sdk2.parameters.Dict(
                "Dynamic parameter of type 'Dict'", default={"aaa": "123", "bbb": "456", "ccc": "789"},
                description="Description for Dict parameter"
            )
            with sdk2.parameters.Dict(
                "Dynamic parameter of type 'Dict' with choices"
            ) as dict_of_strings_choices:
                dict_of_strings_choices.values[""] = ""
                dict_of_strings_choices.values.SUCCESS = "success"
                dict_of_strings_choices.values.TEMPORARY = "temporary"
                dict_of_strings_choices.values.EXCEPTION = "exception"
                dict_of_strings_choices.values.FAILURE = "failure"
            with sdk2.parameters.List(
                "Dynamic parameter of type 'List' with choices"
            ) as list_of_strings_with_choices:
                list_of_strings_with_choices.values["ZERO"] = "0"
                list_of_strings_with_choices.values.ONE = "1"
                list_of_strings_with_choices.values.TWO = "2"
            with sdk2.parameters.RadioGroup("Just a radio field group") as radio_group:
                radio_group.values.value1 = None
                radio_group.values.value2 = radio_group.Value(default=True)
                radio_group.values.value3 = None
            string_parameter = sdk2.parameters.String("Does nothing", description="Description for String parameter")
            json_parameter = sdk2.parameters.JSON(
                "Value type or all keys and values (if it's dict) will be printed to debug.log",
                description="Description for JSON parameter"
            )
            unlock_group_1 = sdk2.parameters.Bool("Unlock subgroup 1")
            unlock_group_2 = sdk2.parameters.Bool("Unlock subgroup 2")
            with unlock_group_1.value[True], unlock_group_2.value[True]:
                # these params should open when either unlock_group_1 or unlock_group_2 is checked
                locked_param = sdk2.parameters.Bool("Locked param, does nothing")
                locked_param_2 = sdk2.parameters.Integer("Locked integer param, does nothing", required=True)

            with sdk2.parameters.RadioGroup("RadioGroup with False/True values", per_line=3) as boolean_group:
                boolean_group.values[False] = boolean_group.Value("Falsy value")
                boolean_group.values[True] = boolean_group.Value("Truthy value", default=True)

        with sdk2.parameters.Output:
            result = sdk2.parameters.Integer(
                "Answer to the Ultimate Question of Life, the Universe, and Everything", default=42, required=True
            )
            head = sdk2.parameters.Integer(
                "This parameter is set when the task starts executing"
            )

        with sdk2.parameters.Group("Test UI") as whatever:
            boolean_dictionary = sdk2.parameters.Dict("Dictionary of boolean values", value_type=sdk2.parameters.Bool)
            boolean_list = sdk2.parameters.List("List of boolean values", value_type=sdk2.parameters.Bool)

        set_custom_parameter_from_on_create = sdk2.parameters.Integer(
            "Set parameter initialized_from_on_create from on_create"
        )
        initialized_from_on_create = sdk2.parameters.Integer("Initialized to the value of 42 from the on_create")
        set_tasks_resource_from_on_create = sdk2.parameters.Integer("Set requirement tasks_resource from on_create")
        upload_to_mds = sdk2.parameters.Bool("Upload resources to MDS")
        with upload_to_mds.value[True]:
            sync_upload_to_mds = sdk2.parameters.Bool("Synchronous upload to MDS")

    class Context(sdk2.Context):
        test_task_test_context_key = 0xBEAF
        some_number = 0
        tuple_key = (1, 2, 3)
        __STAGES = {}

    ARCADIA_URI = "arcadia-arc:#trunk"

    @sdk2.report(title="beep boop hello i'm a drone")
    def report_example(self):
        return textwrap.dedent("""
            <h2>HELLO FROM SANDBOX</h2><br>
            <marquee behavior="alternate">
                MY PARENTS: {parents}
            </marquee>
        """.format(
            parents=" ".join((
                "<span class='tags-list__item'>{}.{}</span>".format(_.__module__, _.__name__)
                for _ in type(self).mro()
            ))
        )).strip()

    @sdk2.report(title="Another report", label="another_report")
    def test_report(self):
        return textwrap.dedent("""
            Hello From <a href="https://sandbox.yandex-team.ru">Sandbox</a>
        """).strip()

    @sdk2.header()
    def head(self):
        return textwrap.dedent("""
            <b>hello from sandbox</b>
        """).strip()

    @property
    def release_template(self):
        subject = u"Test task \"{}\" has been released!".format(self.Parameters.description)
        return sdk2.ReleaseTemplate(
            ["sandbox-noreply", "devnull"],
            subject,
            textwrap.dedent(u"""
                Good news, everyone!

                {}

                --
                Sincerely,
                    your Sandbox ({}) installation.
            """.format(subject, common.config.Registry().this.id))
        )

    @property
    def footer(self):
        return [
            {"helperName": "replacePlaceholders",
             "content": textwrap.dedent(u"""
            <div style="border: 2px solid yellow;">
                <h2 align="center">
                    footer: <h1>{}</h1>
                </h2>
                <br/>
                Placeholder replacement should also works fine: <b>%TEST%</b>
            </div>
            """.format(self.Parameters.description))}
        ]

    def on_create(self):
        self.Context.some_number += 1
        if self.Parameters.set_custom_parameter_from_on_create:
            self.Parameters.initialized_from_on_create = self.Parameters.set_custom_parameter_from_on_create
        if self.Parameters.set_tasks_resource_from_on_create:
            self.Requirements.tasks_resource = self.Parameters.set_tasks_resource_from_on_create

    def on_save(self):
        super(TestTask2, self).on_save()
        self.Context.some_number += 1
        self.Requirements.privileged = self.Parameters.privileged
        if self.Parameters.ramdrive:
            self.Requirements.ramdrive = ctm.RamDrive(
                ctm.RamDriveType.TMPFS,
                self.Parameters.ramdrive << 10,
                None
            )
        if self.Parameters.overwrite_client_tags and self.Parameters.client_tags:
            self.Requirements.client_tags = self.Parameters.client_tags
            if any(ctc.Tag.MULTISLOT in p for p, n in ctc.Tag.Query.predicates(self.Parameters.client_tags)):
                self.Requirements.Caches.qwer = None
                del self.Requirements.Caches.qwer

    def on_enqueue(self):
        super(TestTask2, self).on_enqueue()
        if self.Parameters.raise_exception_on_enqueue:
            raise Exception("Exception on enqueue.")

        with self.memoize_stage.set_expires_on_enqueue:
            if self.Parameters.expires_on_enqueue:
                self.Parameters.expires = self.Parameters.expires_on_enqueue

        self.Context.test_on_enqueue = True
        if not common.system.inside_the_binary():  # TODO: remove check after SANDBOX-6049
            self.set_info("Test set_info on enqueue.")
            with self.memoize_stage.wait_on_enqueue:
                if self.Parameters.wait_on_enqueue:
                    raise sdk2.WaitTime(self.Parameters.wait_on_enqueue)
            with self.memoize_stage.wait_task_on_enqueue:
                if self.Parameters.wait_task_on_enqueue:
                    raise sdk2.WaitTask(
                        filter(None, iter(self.Parameters.wait_task_on_enqueue)),
                        ctt.Status.Group.FINISH, True
                    )
            if (
                self.Parameters.wait_for_output_parameters and
                not self.Context.waited_output and
                self.Parameters.wait_output_on_enqueue
            ):
                self.wait_output()

            if self.Parameters.create_parent_resource_on_enqueue:
                self.create_parent_resource()

        with self.memoize_stage.create_resource_on_enqueue:
            if self.Parameters.create_resource_on_enqueue:
                res = TestTask2Resource(self, self.Parameters.description, "on_enqueue_resource")
                self.Context.created_resource_on_enqueue = res.id

        if self.Parameters.stop_on_enqueue:
            raise common.errors.TaskStop

        self.Context.tuple_key = (3, 4, 5)

    def on_release(self, params):
        # self.Context.has_vault_key = bool(self.Parameters.vault_key)
        if params["release_subject"] == "die":
            raise Exception
        if self.Parameters.check_ssh_agent:
            assert sdk2.ssh.SshAgent()._keys
        self.Context.test_on_release = params
        if params.get("_release_subscriber") and params.get("release_subject"):
            self.server.notification(
                subject=params["release_subject"],
                body="[testing] Release body",
                recipients=params["_release_subscriber"],
                transport=ctn.Transport.EMAIL
            )
        super(TestTask2, self).on_release(params)

    def on_prepare(self):
        self.Context.test_on_prepare = True
        super(TestTask2, self).on_prepare()
        if self.ramdrive and self.Parameters.create_ramdir_on_prepare:
            os.mkdir(str(self.ramdrive.path.joinpath("on_prepare")))
        if self.Parameters.prep_live_time:
            sleep = self.Parameters.prep_live_time
            logging.info("Sleeping for %.2fs", sleep)
            time.sleep(sleep)

    def on_break(self, prev_status, status):
        self.Context.test_on_break = True
        super(TestTask2, self).on_break(prev_status, status)
        msg = "on_break: switching from {} to {}".format(prev_status, status)
        logging.debug(msg)
        self.set_info(msg)
        time.sleep(self.Parameters.break_time)

    def on_terminate(self):
        logging.info("Terminating")
        self.Context.test_on_terminate = True
        time.sleep(self.Parameters.termination_time)
        logging.info("Terminated")

    def on_wait(self, prev_status, status):
        super(TestTask2, self).on_wait(prev_status, status)
        msg = "on_wait: switching from {} to {}".format(prev_status, status)
        logging.debug(msg)
        time.sleep(self.Parameters.break_time)

    def on_finish(self, prev_status, status):
        self.Context.test_on_finish = True
        super(TestTask2, self).on_finish(prev_status, status)
        assert self.Context.test_on_execute
        logging.debug("on_finish: switching from %s to %s", prev_status, status)

        if self.Parameters.check_ssh_agent:
            assert sdk2.ssh.SshAgent()._keys

        if self.Parameters.check_coredump:
            if not list(sdk2.Resource["CORE_DUMP"].find(task=self).limit(1)):
                raise common.errors.TaskFailure("Coredump check failed: no resource found")

        if self.Parameters.fin_live_time:
            sleep = self.Parameters.fin_live_time
            logging.info("Sleeping for %.2fs", sleep)
            time.sleep(sleep)
        self.Parameters.result = random.random() * 1000

    def prepare_stages(self, subtask_id):
        def set_range_to_stages(self_, name, start_time, finish_time):
            self_.Context.__STAGES[name + "_started"] = start_time
            self_.Context.__STAGES[name + "_finished"] = finish_time

        def fetch_task_times(task_id):
            client = self.server
            return client.task[task_id].audit.read()

        def make_timestamp(d):
            utc_dt = aniso8601.parse_datetime(d)
            timestamp = calendar.timegm(utc_dt.timetuple())
            local_dt = dt.datetime.fromtimestamp(timestamp)
            return time.mktime(local_dt.replace(microsecond=utc_dt.microsecond).timetuple())

        def refactor_times(times_list):
            result = collections.defaultdict(list)
            for item in sorted(times_list, key=lambda x: x["time"]):
                sts = item.get("status", "").lower()
                if not sts:
                    continue
                result[sts] = sorted(result[sts] + [make_timestamp(item["time"])])
            return result

        self.Context.time_metrics = {}
        self_times = refactor_times(fetch_task_times(self.id))
        logging.debug("Times for this task are %s", json.dumps(self_times, indent=4, sort_keys=True))

        subtask_times = refactor_times(fetch_task_times(subtask_id))
        logging.debug("Times for child task %d are %s", subtask_id, json.dumps(subtask_times, indent=4, sort_keys=True))

        base_time = self_times["draft"][0]

        for status, values in six.iteritems(subtask_times):
            for value in values:
                self.Context.time_metrics["child_task_" + status] = value - base_time

        logging.debug("Times for task %d are %s", self.id, json.dumps(self_times, indent=4, sort_keys=True))

        set_range_to_stages(self, "first-parent-queue-lag", self_times["draft"][0], self_times["preparing"][0])
        set_range_to_stages(self, "first-parent-preparing", self_times["preparing"][0], self_times["executing"][0])
        set_range_to_stages(self, "first-parent-executing", self_times["executing"][0], self_times["wait_task"][0])

        set_range_to_stages(self, "child-task-finishing", subtask_times["finishing"][-1], subtask_times["success"][-1])
        set_range_to_stages(self, "wait-child", subtask_times["success"][-1], self_times["enqueued"][-1])

        set_range_to_stages(self, "last-parent-queue-lag", self_times["enqueued"][-1], self_times["preparing"][-1])
        set_range_to_stages(self, "last-parent-preparing", self_times["preparing"][-1], self_times["executing"][-1])

    def wait_output(self):
        self.Context.waited_output = True
        logging.info("WaitOutput: %s", self.Parameters.output_param_targets)
        output_targets = {}
        for task_id, params in six.iteritems(self.Parameters.output_param_targets):
            try:
                output_targets[int(task_id)] = [param.strip() for param in params.split(",")]
            except ValueError:
                logging.warning("Invalid task_id: %s", task_id)
                continue
        if output_targets:
            raise sdk2.WaitOutput(output_targets, self.Parameters.wait_output_all)

    def create_parent_resource(self):
        if self.parent:
            with self.memoize_stage.parent_resource:
                parent_res = TestTask2Resource(
                    self.parent, "Resource from task #{}".format(self.id),
                    "parent_resource_{}".format(self.id)
                )
                self.Context.parent_resource = parent_res.id

    def test_actions(self):
        number_of_actions = random.randint(1, 6)
        actions = {
            int(k): int(v)
            for k, v in six.iteritems(self.Parameters.actions)
        }
        if not actions:
            actions = {
                duration: steps
                for duration, steps in zip(
                    (random.randint(1, 30) for _ in six.moves.range(number_of_actions)),
                    (random.randint(1, 1000) for _ in six.moves.range(number_of_actions)),
                )
            }
        logging.info("Actions (duration -> steps): %r", actions)

        word_sets = [
            ["Testing", "Running", "Evaluating", "Processing"],
            ["<b>{}</b>".format(w) for w in ("my", "a fast", "a wonderful", "a brilliant")],
            ["cat", "dog", "Sandbox task", "solution"],
        ]
        messages = [
            " ".join(random.choice(s) for s in word_sets)
            for _ in six.moves.range(len(actions))
        ]
        items = {
            duration: sdk2.helpers.ProgressMeter(
                message, maxval=steps, escape=False,
                formatter=lambda s: "{} items".format(s)
            )
            for message, (duration, steps) in zip(messages, six.iteritems(actions))
        }

        if self.Parameters.actions_flow == ActionFlow.CONSECUTIVE:
            for duration, meter in six.iteritems(items):
                logging.debug("Using meter %r, gonna take %ds", meter.message, duration)
                with meter:
                    delta = int(math.ceil(meter.maxval / float(duration)))
                    for _ in six.moves.range(duration):
                        meter.add(delta)
                        time.sleep(1)

        else:
            for meter in six.itervalues(items):
                meter.__enter__()

            for _ in six.moves.range(max(six.iterkeys(items))):
                for duration, meter in six.iteritems(items):
                    if meter.value >= meter.maxval:
                        continue
                    delta = int(math.ceil(meter.maxval / float(duration)))
                    meter.add(delta)
                time.sleep(1)

            for meter in six.itervalues(items):
                meter.__exit__()

    def on_execute(self):
        self.Context.test_on_execute = True
        logging.info("Current environments: %r", os.environ)
        with self.memoize_stage.first_run:
            logging.info("This is my FIRST RUN!")
            self.Parameters.head = int(time.time())
            if self.Parameters.expires_on_execute:
                self.Parameters.expires = self.Parameters.expires_on_execute

        self._test_context_serialization()

        if self.scheduler:
            logging.info(
                "This is a %s run under scheduler #%d",
                "scheduled" if self.scheduler > 0 else "manual",
                abs(self.scheduler)
            )

        uid, gid = (None, None) if running_on_windows else (os.getuid(), os.getgid())
        logging.info("Current user is %r (UID %s, GID %s)", getpass.getuser(), uid, gid)

        if sys.platform.startswith("linux"):
            logging.info(
                "Current capabilities:\n%s",
                sp.check_output("grep Cap /proc/{}/status".format(os.getpid()), shell=True)
            )

        if self.Parameters.run_actions:
            self.test_actions()

        if self.Parameters.raise_exception_on_start:
            raise EXCEPTION_MAPPING[self.Parameters.exc_class]("Here goes an exception raised from on_execute()")

        if self.Parameters.check_ssh_agent:
            assert sdk2.ssh.SshAgent()._keys

        if self.ramdrive:
            logging.info(
                "RAM drive of size %s path: %r",
                common.format.size2str(self.ramdrive.size << 20),
                self.ramdrive.path
            )
            if self.Parameters.create_ramdir_on_execute:
                os.mkdir(str(self.ramdrive.path.joinpath("on_execute")))
            with sdk2.helpers.ProcessLog(self, logger="mount") as pl:
                sp.Popen("mount".split(), stdout=pl.stdout, stderr=sp.STDOUT).wait()
            with sdk2.helpers.ProcessLog(self, logger="df_h") as pl:
                sp.Popen("df -h".split(), stdout=pl.stdout, stderr=sp.STDOUT).wait()

        logging.info("Test run process")
        cmd = "c:\\tools\\du.exe /accepteula" if running_on_windows else "du -h"
        with sdk2.helpers.ProcessLog(self, logger="du_h") as pl:
            sp.Popen(cmd, shell=True, stdout=pl.stdout, stderr=sp.STDOUT).wait()

        if self.Parameters.check_coredump:
            with sdk2.helpers.ProcessRegistry:
                p = sp.Popen(["sleep", "1000"])
                os.kill(p.pid, 3)

        if self.Parameters.write_to_syslog:
            logging.info("Writing %r to system log", self.Parameters.write_to_syslog)
            sp.Popen(["logger", self.Parameters.write_to_syslog]).wait()

        logging.info("Test logging message.")

        logging.info("Test environment")
        with sdk2.helpers.ProcessLog(self, logger="env") as pl:
            pl.logger.propagate = True
            cmd = "set" if running_on_windows else "env | sort"
            sp.Popen(cmd, shell=True, stdout=pl.stdout, stderr=sp.STDOUT).wait()

        if self.Parameters.check_vault:
            logging.info("Test vault")
            vault_data = sdk2.Vault.data(
                self.Parameters.vault_item_owner or self.owner,
                self.Parameters.vault_item_name
            )
            if vault_data != self.Parameters.expected_secret:
                raise common.errors.TaskError(
                    "Vault error: {} \"{}\" differs from {}".format(
                        self.Parameters.vault_item_name, vault_data, self.Parameters.expected_secret
                    )
                )
            logging.info("Vault data: %s", vault_data)

        if self.Parameters.ping_host_via_skynet:
            # noinspection PyUnresolvedReferences
            import library.sky.hosts
            hosts = library.sky.hosts.braceExpansion(self.Parameters.ping_host_via_skynet.split(","))
            timeout = len(hosts) * 3
            logging.info(
                "Staring ping via cqueue %d host(s): %s with timeout %d",
                len(hosts),
                ", ".join(hosts),
                timeout
            )
            import sandbox.projects.common.utils as utils
            utils.receive_skynet_key(self.owner)
            logging.info("Here is results:\n%s", "\n".join(_cqueue_pinger(hosts, timeout=timeout)))
            logging.info("Ping is over")

        if self.Context.multi_threading:
            logging.info("Test multi-threading")

            def ping_server(queue):
                # noinspection PyBroadException
                try:
                    for _ in six.moves.range(3):
                        data = random.randint(0, 0x7FFFFFFF)
                        assert self.server.ping(data) == data
                    queue.put(True)
                except Exception:
                    logging.exception("Error occurred during pinging server")
                    queue.put(False)

            q = Queue.Queue()
            threads = []
            for x in six.moves.range(10):
                th = threading.Thread(target=ping_server, args=(q, ))
                th.start()
                threads.append(th)

            res = True
            for x in six.moves.range(q.qsize()):
                res &= q.get(timeout=3)
            list(map(threading.Thread.join, threads))
            if not res:
                raise common.errors.TaskFailure("Threading error. See logs for more info")

        if self.Parameters.create_resources:
            attrs = {"test_attr": 42}
            if self.Parameters.upload_to_mds:
                attrs["sync_upload_to_mds"] = self.Parameters.sync_upload_to_mds
            file_name = "lifetime.log"
            if self.Parameters.single_file_resource_in_dir:
                file_name = "subdir/" + file_name
            file_resource_data = sdk2.ResourceData(TestTask2Resource(
                self, self.Parameters.description, file_name, **attrs
            ))
            if self.Parameters.single_file_resource_in_dir:
                file_resource_data.path.parent.mkdir()

            common.fs.allocate_file(
                six.text_type(file_resource_data.path), self.Parameters.create_resources_file_size
            )

            attrs = {}
            if self.Parameters.upload_to_mds:
                attrs["sync_upload_to_mds"] = self.Parameters.sync_upload_to_mds
            if running_on_windows:
                attrs["custom_platform"] = "windows"
            folder_resource_data = sdk2.ResourceData(TestTask2Resource(
                self, self.Parameters.description, "directory_resource", **attrs
            ))
            folder_resource_data.path.mkdir(0o755, parents=True, exist_ok=True)
            logging.info("write file1")
            folder_resource_data.path.joinpath("file1.txt").write_bytes(
                six.ensure_binary("Some test data in file1.txt")
            )
            logging.info("write file2")
            common.fs.allocate_file(
                six.text_type(folder_resource_data.path.joinpath("file2")),
                self.Parameters.create_resources_dir_size
            )
            if not running_on_windows:
                try:
                    if not (folder_resource_data.path / "file1.txt.symlink").exists():
                        (folder_resource_data.path / "file1.txt.symlink").symlink_to("file1.txt")
                except NotImplementedError:
                    pass
                subdir = folder_resource_data.path / "subdir"
                subdir.mkdir(0o755, exist_ok=True)
                (folder_resource_data.path / "subdir-2").mkdir(0o755, exist_ok=True)
                (subdir / "file").write_bytes(
                    six.ensure_binary("Some test data in file")
                )
                try:
                    if not (folder_resource_data.path / "subdir_link").exists():
                        (folder_resource_data.path / "subdir_link").symlink_to("./subdir")
                except NotImplementedError:
                    pass
            if self.Parameters.create_tar_resource:
                attrs["pack_tar"] = 1
                resource_data = sdk2.ResourceData(TestTask2Resource(
                    self, self.Parameters.description, "tar_archive", **attrs
                ))
                shutil.copytree(str(self.log_path()), str(resource_data.path))
            if self.Parameters.create_tgz_resource:
                attrs["pack_tar"] = 2
                resource_data = sdk2.ResourceData(TestTask2Resource(
                    self, self.Parameters.description, "tgz_archive", **attrs
                ))
                shutil.copytree(str(self.log_path()), str(resource_data.path))

        if self.Parameters.create_empty_resource:
            # Empty resource cannot marked as READY
            TestTask2Resource(self, self.Parameters.description, "empty_resource")

        if self.Parameters.create_custom_logs:
            custom_log_resource = sdk2.service_resources.TaskCustomLogs(self, "Custom Logs", "custom_logs")
            custom_log_data = sdk2.ResourceData(custom_log_resource)
            custom_log_data.path.mkdir(0o755, parents=True, exist_ok=True)
            custom_log_data.path.joinpath("custom.log").write_bytes(six.ensure_binary("..."))

        if self.Parameters.create_parent_resource:
            self.create_parent_resource()

        if self.Parameters.create_resource_ttl_inf:
            attrs["ttl"] = "inf"
            file_resource_data = sdk2.ResourceData(TestTask2Resource(
                self, self.Parameters.description, "ttl_inf.log", **attrs
            ))
            common.fs.allocate_file(six.text_type(file_resource_data.path), 10)

        if self.Context.created_resource_on_enqueue:
            on_enqueue_resource_data = sdk2.ResourceData(
                sdk2.Resource[self.Context.created_resource_on_enqueue]
            )
            on_enqueue_resource_data.path.write_bytes(six.ensure_binary("This resource was registered in on_enqueue"))

        if (

            self.Parameters.wait_for_output_parameters and
            not self.Context.waited_output and
            not self.Parameters.wait_output_on_enqueue
        ):
            self.wait_output()

        wait_time = self.Parameters.wait_time
        if wait_time and not self.Context.waited_time:
            self.Context.waited_time = True
            raise sdk2.WaitTime(wait_time)

        if self.Context.parent_resource:
            parent_res = sdk2.Resource[self.Context.parent_resource]
            common.fs.allocate_file(six.text_type(parent_res.path), self.Parameters.create_resources_file_size)

        if self.Parameters.parent_resource:
            common.fs.allocate_file(
                six.text_type(self.Parameters.parent_resource.path),
                self.Parameters.create_resources_file_size
            )

        if self.Parameters.create_sub_task:
            if self.Context.subtasks:
                subtasks = list(self.find(id=self.Context.subtasks).limit(len(self.Context.subtasks)))
            else:
                subtasks = None
            if not subtasks:
                logging.info("Create subtasks")
                subtasks = []
                for i in six.moves.range(self.Parameters.number_of_subtasks):
                    parent_resource = TestTask2Resource(
                        self, "Resource for subtask {}".format(i), "external_resource_{}".format(i), test_attr=i,
                    ) if self.Parameters.pass_resources_to_subtasks else None

                    subtask = TestTask2(
                        self,
                        __requirements__={"tasks_resource": self.Requirements.tasks_resource},
                        description="Child of test task {}".format(self.id),
                        owner=self.Parameters.owner,
                        notifications=self.Parameters.notifications,
                        create_sub_task=False,
                        overwrite_client_tags=self.Parameters.overwrite_client_tags,
                        client_tags=self.Parameters.client_tags,
                        subtask_exec_limit=self.Parameters.subtask_exec_limit,
                        go_to_state=self.Parameters.go_to_state,
                        create_parent_resource=self.Parameters.create_parent_resource,
                        create_parent_resource_on_enqueue=self.Parameters.create_parent_resource_on_enqueue,
                        wait_time=self.Parameters.subtask_wait_time or 0,
                        parent_resource=parent_resource,
                    )
                    exec_limit = self.Parameters.subtask_exec_limit
                    if exec_limit:
                        sem_name = "{}_{}".format(self.type.name, self.id)
                        subtask.Requirements.semaphores = ctt.Semaphores(
                            acquires=[
                                ctt.Semaphores.Acquire(name=sem_name, weight=1, capacity=exec_limit, public=self.Parameters.create_public_semaphore)
                            ],
                            release=(ctt.Status.Group.BREAK, ctt.Status.Group.FINISH, ctt.Status.Group.WAIT)
                        )
                    subtask.save()
                    subtasks.append(subtask.enqueue())
                if subtasks:
                    self.Context.subtasks = list(map(lambda _: _.id, subtasks))

                self.Context.wait_all_tasks = self.Parameters.number_of_subtasks > 1
                raise sdk2.WaitTask(
                    subtasks,
                    common.utils.chain(ctt.Status.Group.FINISH, ctt.Status.Group.BREAK),
                    wait_all=False,
                )

            else:
                if self.Context.wait_all_tasks:
                    self.Context.wait_all_tasks = False
                    raise sdk2.WaitTask(
                        subtasks,
                        common.utils.chain(ctt.Status.Group.FINISH, ctt.Status.Group.BREAK),
                        wait_all=True,
                    )
                else:
                    if self.Parameters.save_stages:
                        self.prepare_stages(subtasks[0].id)
                    for subtask in subtasks:
                        logging.info("Subtask #%s status: %s", subtask.id, subtask.status)
            return

        if self.Parameters.build_with_arcadiasdk:
            test_get_arcadia_url = self.Parameters.test_get_arcadia_url
            import sandbox.projects.common.arcadia.sdk as arcadiasdk
            do_build_params = dict(
                build_system=consts.YMAKE_BUILD_SYSTEM,
                targets=["contrib/libs/openssl"],
                build_type=consts.RELEASE_BUILD_TYPE,
                clear_build=True,
                results_dir="release",
                def_flags={"SANDBOX_TASK_ID": self.id}
            )
            if self.Parameters.use_arc:
                with arcadiasdk.mount_arc_path(self.ARCADIA_URI, use_arc_instead_of_aapi=True, fetch_all=False) as aarcadia:
                    do_build_params["source_root"] = aarcadia
                    arcadiasdk.do_build(**do_build_params)
            elif test_get_arcadia_url:
                test_get_arcadia_path = sdk2.svn.Arcadia.get_arcadia_src_dir(test_get_arcadia_url)
                logging.info("Arcadia repo path %s:\n%s", test_get_arcadia_path, os.listdir(test_get_arcadia_path))
                do_build_params["source_root"] = test_get_arcadia_path
                arcadiasdk.do_build(**do_build_params)

        resource = self.Parameters.dependent_resource
        if resource:
            logging.info("dependent resource: %r", resource)
            if self.Parameters.sync_resource_in_subprocess:
                with sdk2.helpers.ProcessLog(self, logger="synchrophazotron") as pl:
                    buf = io.BytesIO()
                    pl.logger.addHandler(logging.StreamHandler(buf))
                    sp.Popen(
                        [str(self.path("synchrophazotron")), str(resource.id)], stdout=pl.stdout, stderr=sp.STDOUT
                    ).wait(3600)
                    dependent_resource_path = sdk2.path.Path(six.ensure_str(buf.getvalue().strip()))
                    # or more simpler without writing to file
                    # dependent_resource_path = sdk2.path.Path(sp.check_output(
                    #     [str(self.path("synchrophazotron")), str(resource.id)],
                    #     timeout=3600
                    # ))

            else:
                dependent_resource_path = sdk2.ResourceData(resource).path

            owner = (
                common.os.User.service_users.service
                if ctc.Tag.NEW_LAYOUT in common.config.Registry().client.tags else
                common.os.User.service_users.unprivileged
            )
            logging.info("Dependent resource path: %r, owner should be %r", dependent_resource_path, owner)
            # assert dependent_resource_path.stat().st_uid == owner.uid

            if dependent_resource_path.is_file():
                logging.info(dependent_resource_path.read_bytes())
            if self.Parameters.modify_resource:
                if dependent_resource_path.is_file():
                    with dependent_resource_path.open("a") as f:
                        f.write("test modification")
                else:
                    dependent_resource_path.joinpath("new_file.mdf").write_bytes(six.ensure_binary("test modification"))

        if self.Parameters.mount_image:
            if self.Parameters.mount_image_with_synchrophazotron:
                with sdk2.helpers.ProcessLog(self, logger="synchrophazotron") as pl:
                    path = sdk2.Path(six.ensure_str(sp.Popen(
                        [
                            str(self.path("synchrophazotron")), "mount_image",
                            str(sdk2.ResourceData(self.Parameters.mount_image).path)
                        ],
                        stdout=sp.PIPE, stderr=pl.stderr
                    ).communicate()[0]).strip())
            else:
                path = sdk2.ResourceData(self.Parameters.mount_image).mount()
            dirlist = common.itertools.chain(*(["\n", "\t", str(node)] for node in path.iterdir()))
            logging.info(
                "Mounted resource %r as SquashFS image at %r. Follows its content:%s",
                self.Parameters.mount_image, path, "".join(dirlist)
            )

        if self.Parameters.mount_overlay:
            self._test_overlay_mounting(
                (self.ramdrive.path.joinpath if self.Parameters.ramdrive else self.path)("mounting")
            )

        if self.Parameters.live_time:
            live_time = self.Parameters.live_time

            def sleep():
                logging.info("Sleeping for %.2fs", live_time)
                if self.Parameters.sleep_in_subprocess:
                    with sdk2.helpers.ProcessLog(self) as _:
                        sp.check_call(["sleep", str(live_time)], stdout=_.stdout)
                else:
                    for i in six.moves.range(live_time):
                        logging.info("Iteration #%d. Sleeping another second", i)
                        time.sleep(1)

            if self.Parameters.use_no_timeout:
                with sdk2.helpers.NoTimeout():
                    sleep()
            else:
                sleep()

        if self.Parameters.use_cgroup:
            cg = common.os.CGroup("test_task")
            cg.memory["low_limit_in_bytes"] = 16911433728
            cg.memory["limit_in_bytes"] = 21421150208
            cmd = ["/bin/sleep", str(self.Parameters.kill_timeout)]
            logging.info("Running %r in %r", cmd, cg)
            p = sp.Popen(cmd, preexec_fn=cg.set_current)
            logging.info("Process started in %r", list(common.os.CGroup(pid=p.pid)))

        if self.Parameters.suspend:
            self.suspend()

        go_to_state = self.Context.go_to_state or self.Parameters.go_to_state
        exception_classes = {
            ctt.Status.FAILURE: common.errors.TaskFailure,
            ctt.Status.EXCEPTION: common.errors.TaskError,
            ctt.Status.TEMPORARY: common.errors.TemporaryError,
            ctt.Status.STOPPED: common.errors.TaskStop,
        }
        if go_to_state in exception_classes:
            if go_to_state not in ctt.Status.Group.FINISH:
                self.Context.go_to_state = ctt.Status.SUCCESS
            exception_class = exception_classes[go_to_state]
            raise exception_class(
                "{} was raised. The task state should be {}.".format(exception_class.__name__, go_to_state)
            )

        if self.Parameters.create_independent_task:
            independent_task = TestTask2(
                None,
                priority=ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.HIGH)
            )
            independent_task.Parameters.description = "Created from {!r} for test user inherit".format(self)
            independent_task.Parameters.owner = self.owner
            self.Context.independent_task_id = independent_task.save().enqueue().id

        if self.Parameters.send_email_to_recipient:
            self.Context.email_notification_id = self.server.notification(
                subject="Test email from TestTask #{}".format(self.id),
                body="Email body",
                recipients=[self.Parameters.email_recipient],
                transport=ctn.Transport.EMAIL,
                urgent=self.Parameters.mark_as_urgent,
            )["id"]

        if self.Parameters.json_parameter:
            if isinstance(self.Parameters.json_parameter, dict):
                logging.debug("JSON parameter keys and values: %r", self.Parameters.json_parameter.items())
            else:
                logging.debug("JSON parameter's type is %r", type(self.Parameters.json_parameter))

        if self.Parameters.kill_executor:
            raise BaseException("Die, Executor, die!")

    def _test_context_serialization(self):
        # Type checks below will fail on sdk2 with taskbox enabled.
        # See https://wiki.yandex-team.ru/sandbox/cookbook/#kakmnesoxranitsostojaniezadachi
        # assert isinstance(self.Context.tuple_key, tuple), "Tuple was not initialized properly"
        assert self.Context.tuple_key[0] == 3, "Tuple was not modified in `on_enqueue`"
        if len(self.Context.tuple_key) == 3:
            self.Context.tuple_key = (1, 2, 3, 4)
            self.Context.save()

        # assert isinstance(self.Context.tuple_key, tuple)
        assert len(self.Context.tuple_key) == 4, "Tuple was not updated properly"

    def _test_overlay_mounting(self, path):
        def iter_dir(d):
            if not d.is_dir():
                try:
                    content = d.read_text()
                except OSError as er:
                    content = str(er)
                yield "{}:{}".format(d, content)
                return
            yield str(d)
            try:
                for f in d.iterdir():
                    for subf in iter_dir(f):
                        yield subf
            except OSError:
                pass

        lower_dirs = []
        for lower_dir_num in range(3):
            lower_dir = path.joinpath("lower{}".format(lower_dir_num))
            lower_dir.mkdir(0o755, parents=True, exist_ok=True)
            for file_num in range(lower_dir_num + 1):
                lower_dir.joinpath(str(file_num)).write_bytes(six.ensure_binary(str(lower_dir_num)))
            lower_dirs.append(str(lower_dir))

        mount_point = path.joinpath("merged")
        upper_dir = path.joinpath("upper")
        work_dir = path.joinpath("work")
        for lower_dir_count in range(1, 4):
            if self.Parameters.mount_overlay_with_synchrophazotron:
                data = {
                    "mount_point": str(mount_point),
                    "lower_dirs": lower_dirs[:lower_dir_count],
                    "upper_dir": str(upper_dir),
                    "work_dir": str(work_dir)
                }
                data_json = json.dumps(data)
                logging.info("Mounting args: %s", data_json)
                with sdk2.helpers.ProcessLog(self, logger="synchrophazotron") as pl:
                    p = sp.Popen(
                        [str(self.path("synchrophazotron")), "mount_overlay"], stdout=pl.stdout, stderr=sp.STDOUT,
                        stdin=sp.PIPE
                    )
                    p.communicate(six.ensure_binary(data_json))
            else:
                sdk2.os.mount_overlay(mount_point, lower_dirs[:lower_dir_count], upper_dir=upper_dir, work_dir=work_dir)

            logging.debug("Mounting iteration #%s", lower_dir_count)
            mount_point.joinpath("touch{}".format(lower_dir_count)).write_bytes(
                six.ensure_binary("touch{}".format(lower_dir_count))
            )
            logging.debug("Merged: %s", sorted(map(str, iter_dir(mount_point))))
            logging.debug("Upper: %s", sorted(map(str, iter_dir(upper_dir))))

            if not self.Parameters.do_not_unmount:
                if self.Parameters.mount_overlay_with_synchrophazotron:
                    with sdk2.helpers.ProcessLog(self, logger="synchrophazotron") as pl:
                        sp.Popen(
                            [str(self.path("synchrophazotron")), "umount_overlay", str(mount_point)],
                            stdout=pl.stdout, stderr=sp.STDOUT
                        ).communicate()
                else:
                    sdk2.os.umount(mount_point)
