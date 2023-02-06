import os
import re
import sys
import inspect
import importlib
import traceback
import collections

import pytest

from sandbox import common
import sandbox.common.types.misc as ctm
import sandbox.common.types.client as ctc

from sandbox import sdk2
from sandbox import sandboxsdk as sdk1

import sandbox.tasks.tests.lib

from . import tasks_import


_TestingTask = collections.namedtuple("_TestingTask", ("class_name", "module_name", "package_name"))


def ensure_sandbox_dir_in_path(metafunc):
    sandbox_dir = metafunc.config.getoption("--sandbox-dir")
    for _ in (os.path.dirname(sandbox_dir), sandbox_dir):
        if _ not in sys.path:
            sys.path.append(_)


def pytest_generate_tests(metafunc):
    ensure_sandbox_dir_in_path(metafunc)
    task_types = metafunc.config.getoption("--tests").split()
    sandbox_dir = metafunc.config.getoption("--sandbox-dir")
    arcadia_dir = os.path.dirname(sandbox_dir)

    # This is the first time tasks are loaded during tests -- check environment while it is fresh.
    # Build lists required for import guard are supplied by sandbox/tasks/tests/bin program (RESOURCE section).
    if common.system.inside_the_binary():
        import run_import_hook
        import yalibrary.makelists as mk

        yamakes = map(
            mk.from_file,
            (
                os.path.join(arcadia_dir, "sandbox", "tasks", "tests", "bin", "ya.make"),
                os.path.join(arcadia_dir, "sandbox", "virtualenv", "ya.make"),
            )
        )
        import_guard = sandbox.tasks.tests.lib.BinaryImportGuard(run_import_hook.importer, *yamakes)

    # regular imports will fail anyway if there's a module not included in our virtualenv
    else:
        import_guard = sandbox.tasks.tests.lib.PlainImportGuard()

    with import_guard:
        common.projects_handler.load_project_types(
            True, force_from_fs=True,
            import_wrapper=sandbox.tasks.tests.lib.CheckEnvironWrapper()
        )

    from sandbox import projects
    for task_type in task_types:
        assert task_type in projects.TYPES, "Unknown task to test: {}".format(task_type)

    test_ids = []
    testing_tasks = []
    for task_type, task_info in sorted(projects.TYPES.iteritems()):
        if task_types and task_type not in task_types:
            continue
        class_name = task_info.cls.__name__
        module_name = task_info.cls.__module__
        test_ids.append(".".join([module_name, class_name]))
        testing_tasks.append(
            _TestingTask(class_name=class_name, module_name=module_name, package_name=task_info.package)
        )
    metafunc.parametrize(argnames="testing_task", argvalues=testing_tasks, ids=test_ids)


class TestSandboxTasks(object):
    TASK_FIELD_ID_RE = re.compile("^\w+$")

    @classmethod
    def run_sdk1_task_class_tests(cls, obj):
        # check task type
        assert hasattr(obj, "type") and obj.type and obj.type != "TASK", (
            "Invalid task type for {}".format(obj.__name__)
        )

        if issubclass(obj.__class__, object):
            mro = obj.__class__.mro()
            acceptable_mro = mro.index(sdk1.task.SandboxTask) < mro.index(object)
            assert acceptable_mro, (
                "For SDK1 task classes, {} must precede {} in method resolution order".format(
                    sdk1.task.SandboxTask, object
                )
            )

        # check types of task properties
        for property_name, property_type in [("privileged", bool)]:
            prop = getattr(obj, property_name)
            assert isinstance(prop, property_type), (
                "Property {} has type {}, but must be {}".format(property_name, type(prop), property_type)
            )
        assert obj.dns in ctm.DnsType

        assert not hasattr(obj, "kill_timeout"), (
            "For SDK1, `kill_timeout` goes into context; "
            "do not hook it onto task class -- set it in initCtx() or modify context in on_enqueue() instead."
        )

        # check input_parameters
        if obj.input_parameters:
            if obj.input_parameters is not None:
                assert isinstance(obj.input_parameters, collections.Iterable), (
                    "`{}.input_parameters` of {} is not iterable. Re-declare it as list or tuple.".format(
                        obj.__class__.__name__, type(obj.input_parameters)
                    )
                )

            # must be string or unicode type
            for i, p in enumerate(obj.input_parameters):
                assert inspect.isclass(p) and issubclass(p, sdk1.parameters.SandboxParameter), (
                    "Input parameter {!r} must be subclass of `sandboxsdk.parameters.SandboxParameter`".format(p)
                )

                assert isinstance(p.name, basestring), (
                    "{}.input_parameters[{}].name is not string: {}. Broken parameter: {}".format(
                        obj.type, i, type(p.name), p
                    )
                )

                assert isinstance(p.description, basestring), (
                    "{}.input_parameters[{}].description is not string: {}. Broken parameter: {}".format(
                        obj.type, i, type(p.description), p
                    )
                )

                # every subfield must be a string
                if getattr(p, "sub_fields", None) is not None:
                    for subfield in p.sub_fields.iterkeys():
                        assert isinstance(subfield, basestring), (
                            "All subfields of {}.input_parameters[{}] must be strings. Broken subfield: {}".format(
                                obj.type, i, subfield
                            )
                        )

                        for j, name in enumerate(p.sub_fields[subfield]):
                            assert isinstance(name, basestring), (
                                "{}.input_parameters[{}].sub_fields[{}][{}] must be a string (use {}.name)".format(
                                    obj.type, i, subfield, j, name
                                )
                            )

            # look up for duplicates
            duplicates = [x for x, y in collections.Counter(p.name for p in obj.input_parameters).items() if y > 1]
            assert not duplicates, (
                "{}: Duplicates in parameter names: {}".format(
                    obj.type,
                    ", ".join(
                        "{!r} at positions {}".format(
                            dup_name, [i for i, p in enumerate(obj.input_parameters) if dup_name == p.name]
                        ) for dup_name in duplicates
                    )
                )
            )

        # check form fields
        system_ctx = {
            "kill_timeout", "important", "do_not_restart", "hidden", "fail_on_any_error",
            "execution_space", "disk_space_usage", "invalid_disk_space", "priority",
            "notify_via", "notify_if_failed", "notify_if_finished"
        }
        if hasattr(obj, "form_fields"):
            task_input_parameters = [item[0] for item in obj.form_fields]
            for i, p in enumerate(task_input_parameters):
                assert isinstance(p, basestring), (
                    "Input parameter name at index {} is not string: {}".format(i + 1, type(p))
                )

            # look up for duplicates
            duplicates = [x for x, y in collections.Counter(task_input_parameters).items() if y > 1]
            assert not duplicates, (
                "{}: Duplicates in parameter names: {}".format(obj.type, ", ".join(duplicates))
            )

            # system task context clashing
            clashes = set(task_input_parameters) & system_ctx
            assert not clashes, (
                "{}: System task ctx and form_fields clashing: {!r}".format(obj.type, ", ".join(clashes))
            )

            invalid = next((name for name in task_input_parameters if not cls.TASK_FIELD_ID_RE.match(name)), None)
            assert not invalid, (
                "{}: Task parameter {!r} does not match identifier pattern, "
                "it will cause Javascript errors in web interface.".format(
                    obj.type, invalid
                )
            )

        # check client_tags
        if obj.client_tags:
            assert not isinstance(obj.client_tags, tuple), "{}: client_tags parameter cannot be of type tuple".format(
                obj.type
            )
            ctc.Tag.Query(obj.client_tags).check()

        assert not obj.se_tags, "Use semaphores instead of SE tags"

    @pytest.mark.usefixtures("tasks_modules")
    def test__task(self, testing_task, monkeypatch, run_long_tests, run_tests_with_filter):
        if run_long_tests or run_tests_with_filter:
            tasks_import.clear_project_modules()

        monkeypatch.setattr(
            common.config.Registry,
            "__init__",
            lambda *args, **kws: pytest.fail(
                "Using of the config on global level is denied, use lazy values:\n{}".format(
                    "".join(traceback.format_stack())
                ))
        )
        setattr(common.config.Registry, common.config.Registry.tag, None)
        task_module = importlib.import_module(testing_task.module_name)
        monkeypatch.undo()
        tasks_import.monkeypatch_forbidden_calls(monkeypatch)
        for task_class in common.projects_handler.load_task_classes(task_module):
            if task_class.__name__ == testing_task.class_name:
                if task_class.type not in sdk2.Task:
                    self.run_sdk1_task_class_tests(task_class(0))
