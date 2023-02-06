from __future__ import absolute_import

import time
import logging

from sandbox import sdk2

from sandbox.common import fs
from sandbox.common import errors as common_errors

import sandbox.common.types.task as ctt
import sandbox.common.types.resource as ctr


class OnCreateOnSaveTestTask(sdk2.Task):
    class Requirements(sdk2.Requirements):
        disk_space = 100

    class Parameters(sdk2.Parameters):
        value = sdk2.parameters.Integer("Initial value", default=0)
        expected_value = sdk2.parameters.Integer("Expected value", required=True)
        expected_disk_space = sdk2.parameters.Integer("Expected disk space", required=True)

        with sdk2.parameters.Output:
            output_ok = sdk2.parameters.Bool("Output parameters work ok")
            on_save_rest_call_failed = sdk2.parameters.Bool("REST call in on_save failed (as expected)")

    def on_create(self):
        self.Parameters.value += 1
        self.Requirements.disk_space += 100

    def on_save(self):
        self.Parameters.value += 2
        self.Requirements.disk_space += 200

        # GET requests are allowed
        assert self._sdk_server.task[self.id][:]["type"] == str(self.type)

        # POST requests on /task/current/hints are allowed
        hints = ["hint1", "hint2"]
        self._sdk_server.task.current.hints(hints)
        assert self._sdk_server.task.current[:]["hints"] == hints

        try:
            self._sdk_server.task[self.id].update({"description": "Fake description"})
        except common_errors.InvalidRESTCall:
            self.Parameters.on_save_rest_call_failed = True
        else:
            self.Parameters.on_save_rest_call_failed = False

    def on_execute(self):
        assert self.Parameters.value == self.Parameters.expected_value
        assert self.Requirements.disk_space == self.Parameters.expected_disk_space

        if not self.Parameters.output_ok:
            self.Parameters.output_ok = True


class ParentResourcesTestTask(sdk2.Task):
    class Requirements(sdk2.Requirements):
        disk_space = 100

    class Parameters(sdk2.Parameters):
        create_sub_task = sdk2.parameters.Bool("Create subtask")
        create_parent_resource = sdk2.parameters.Bool("Create parent resource")
        parent_resource = sdk2.parameters.ParentResource("External resource passed from parent")
        fail_test = sdk2.parameters.Bool("Test child task failing")

    def on_save(self):
        super(ParentResourcesTestTask, self).on_save()
        self.Parameters.description = "Changing description on save"

    def on_execute(self):
        logging.info("Synchrophazotron: %s", self.synchrophazotron)
        assert self.synchrophazotron.exists()
        logging.info("Arcaphazotron: %s", self.arcaphazotron)
        assert self.arcaphazotron.exists()

        assert self.Parameters.description == "Changing description on save"

        from sandbox.projects.sandbox import test_task_2
        TestTask2Resource = test_task_2.TestTask2Resource

        if self.Parameters.create_parent_resource:
            parent_res = TestTask2Resource(
                self.parent, "Resource from task #{}".format(self.id),
                "parent_resource_{}".format(self.id)
            )
            fs.allocate_file(str(parent_res.path), 1024)

        if self.Parameters.parent_resource:
            if self.Parameters.fail_test:
                raise common_errors.TaskFailure
            fs.allocate_file(str(self.Parameters.parent_resource.path), 1024)

        if self.Parameters.create_sub_task:
            subtasks = list(self.find().limit(0))
            parent_resource = TestTask2Resource(
                self, "Resource for subtask",
                "external_resource", test_attr=0,
            )
            if not subtasks:
                subtask = ParentResourcesTestTask(
                    self, description="Child of test task",
                    owner=self.Parameters.owner,
                    fail_test=self.Parameters.fail_test,
                    create_sub_task=False,
                    create_parent_resource=True,
                    parent_resource=parent_resource
                )
                subtask.enqueue()
                raise sdk2.WaitTask([subtask], ctt.Status.Group.FINISH, True)
            elif self.Parameters.fail_test:
                assert parent_resource.state == ctr.State.NOT_READY
                logging.warning("Child task failed. Creating parent resource anyway.")
                fs.allocate_file(str(parent_resource.path), 1024)

        # test setting description and tags
        self.Parameters.description = "New description"
        self.Parameters.tags = ["new_tag"]
        self.Parameters.score = 5


class OnEnqueueResourceTestTask(sdk2.Task):
    def on_enqueue(self):
        import projects.sandbox.test_task_2
        TestTask2Resource = projects.sandbox.test_task_2.TestTask2Resource
        res = TestTask2Resource(self, "description", "on_enqueue_resource")
        self.Context.created_resource_on_enqueue = res.id

    def on_execute(self):
        on_enqueue_resource_data = sdk2.ResourceData(
            sdk2.Resource[self.Context.created_resource_on_enqueue]
        )
        on_enqueue_resource_data.path.write_bytes("This resource was registered in on_enqueue")
        on_enqueue_resource_data.ready()


class TaskCustomLogsTestTask(sdk2.Task):

    def on_execute(self):

        import projects.sandbox.test_task_2

        res = projects.sandbox.test_task_2.TestTask2Resource(self, "description", "non_log_resource")
        non_log_resource = sdk2.ResourceData(res)
        non_log_resource.path.write_bytes("non_log_resource")

        log_resource = sdk2.service_resources.TaskCustomLogs(self, "description", "log_resource")
        sdk2.ResourceData(log_resource)
        log_resource.path.write_bytes("log_resource")

        self.Context.log_sources = self._sdk_server.resource[log_resource.id][:].get("sources")
        self.Context.non_log_sources = self._sdk_server.resource[res.id][:].get("sources")


class SaveContextTestTask(sdk2.Task):
    class Parameters(sdk2.Parameters):
        live_time = sdk2.parameters.Integer("Time to live", default=10, required=True)
        with sdk2.parameters.Output:
            before_timeout_ok = sdk2.parameters.Bool("Before timeout got called")

    def on_prepare(self):
        self.Context.value = 42
        self.Context.save()
        logging.info("Saved context")

    def on_execute(self):
        time.sleep(self.Parameters.live_time)

    def on_timeout(self, prev_status):
        logging.info("Current value: %s", self.Context.value)
        assert self.Context.value == 42

    def timeout_checkpoints(self):
        return [5, 10]

    def on_before_timeout(self, seconds):
        self.Parameters.before_timeout_ok = True
        super(SaveContextTestTask, self).on_before_timeout()


class TaskWithOutputParameters(sdk2.Task):
    class Parameters(sdk2.Parameters):
        with sdk2.parameters.Output:
            output1 = sdk2.parameters.Integer("Output 1")
        with sdk2.parameters.Output(reset_on_restart=False):
            output2 = sdk2.parameters.Integer("Output 2")
        with sdk2.parameters.Output(reset_on_restart=True):
            output3 = sdk2.parameters.Integer("Output 3")


class SubResourceTestTask(sdk2.Task):
    class Parameters(sdk2.Parameters):
        resource = sdk2.parameters.Resource("Resource")

    def total_rest_count(self):
        return self.Context.__values__["__rest_request_count"]

    def on_execute(self):
        import projects.sandbox.test_task_2
        TestTask2Resource = projects.sandbox.test_task_2.TestTask2Resource

        resource = TestTask2Resource(self, "Some resource", "res.txt")
        fs.allocate_file(str(resource.path), 1024)

        subtask = SubResourceTestTask(self, description="Test subtask")

        rc = self.total_rest_count()
        for i in range(100):
            subtask.Parameters.resource = resource

        for i in range(79):
            subtask.Parameters.resource = resource.id

        self.Context.rest_in_range = self.total_rest_count() - rc

        assert subtask.Parameters.resource == resource


class ReportTestTask(sdk2.Task):
    @sdk2.report()
    def hidden_later(self):
        return None

    @sdk2.report("Title")
    def hidden_later_v2(self):
        return None

    @sdk2.report(label="demo")
    def overridden(self):
        return None

    @sdk2.report("Title", "label")
    def report2(self):
        return None

    @sdk2.header()
    def not_a_footer(self):
        return None

    @sdk2.footer()
    def totally_not_a_footer(self):
        return None


class ReportInheritanceTestTask(ReportTestTask):
    @sdk2.report(title="Override 'demo' label", label="dEmO")
    def asdfghjkl(self):
        return "Overridden"

    hidden_later = None
    hidden_later_v2 = sdk2.report()(None)


class TaskWithOnlyFooter(sdk2.Task):
    pass


class TaskWithHintedParameters(sdk2.Task):
    class Parameters(sdk2.Parameters):
        hinted = sdk2.parameters.Integer("Hinted parameter", default=42, hint=True)
        hint_on_enqueue = sdk2.parameters.String("Add this value to hints on enqueue")
        hint_for_output = sdk2.parameters.String("Set hinted_output to this value")

        with sdk2.parameters.Output:
            hinted_output = sdk2.parameters.String("Hinted output parameter", hint=True)

    def on_enqueue(self):
        if self.Parameters.hint_on_enqueue:
            self.hint(self.Parameters.hint_on_enqueue)
        if self.Parameters.hint_for_output:
            self.Parameters.hinted_output = self.Parameters.hint_for_output


class ExpiredTestTask(sdk2.Task):
    class Parameters(sdk2.Parameters):
        expires_on_enqueue = sdk2.parameters.Integer("Expire in N seconds (set in on_enqueue)")
        expires_on_execute = sdk2.parameters.Integer("Expire in N seconds (set in on_execute)")

    def on_enqueue(self):
        if self.Parameters.expires_on_enqueue:
            self.Parameters.expires = self.Parameters.expires_on_enqueue

    def on_execute(self):
        if self.Parameters.expires_on_execute:
            self.Parameters.expires = self.Parameters.expires_on_execute
        time.sleep(1000)


class VaultParamTask(sdk2.Task):
    class Parameters(sdk2.Parameters):
        vault = sdk2.parameters.Vault("Vault to use")
        expected_value = sdk2.parameters.String("Expected value in vault")

    def on_execute(self):
        assert self.Parameters.vault.data() == self.Parameters.expected_value


class MaybeCachesTask(sdk2.Task):
    pass


class NoCachesTask(sdk2.Task):
    class Requirements(sdk2.Requirements):
        class Caches(sdk2.Requirements.Caches):
            pass


class PortoTask(sdk2.Task):
    def on_save(self):
        self.Requirements.porto_layers = [
            sdk2.service_resources.BasePortoLayer.find().first().id
        ]
        super(PortoTask, self).on_save()


class TaskWithTasksResourceRequirement(sdk2.Task):
    def on_save(self):
        if not self.Requirements.tasks_resource:
            self.Requirements.tasks_resource = sdk2.service_resources.SandboxTasksBinary.find().first()
        super(TaskWithTasksResourceRequirement, self).on_save()


class DummyTask(sdk2.Task):
    pass


class TaskWithContainerResourceRequirement(sdk2.Task):
    class Requirements(sdk2.Requirements):
        container_resource = sdk2.parameters.Container("LXC Container")


# TODO: [SANDBOX-6188] remove after all SDK2 tasks will be fixed
class TaskWithContainerResourceParameter(sdk2.Task):
    class Parameters(sdk2.Parameters):
        container_resource = sdk2.parameters.Container("LXC Container")


class TaskWithWrongDefaultContainerResourceRequirement(sdk2.Task):
    class Requirements(sdk2.Requirements):
        container_resource = "qwer"
