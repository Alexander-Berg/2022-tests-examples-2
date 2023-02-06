from __future__ import absolute_import

import pytest

from sandbox import sdk2
from sandbox.common import system
from sandbox import projects


@pytest.mark.usefixtures("project_types")
def test__inner_classes():
    """
    Check that inner task classes (Requirements, Parameters, etc) have valid base classes
    """
    inner_base_classes = (sdk2.Context, sdk2.Parameters, sdk2.Requirements)
    errors = []

    for cls in sdk2.Task:
        for inner_cls in inner_base_classes:
            if not issubclass(getattr(cls, inner_cls.__name__, None), inner_cls):
                errors.append((
                    "{}.{}".format(cls.__module__, cls.__name__), inner_cls, "sdk2.{}".format(inner_cls.__name__)
                ))
        if getattr(cls, "Requirements", None):
            caches = getattr(cls.Requirements, "Caches", None)
            if not issubclass(caches, sdk2.Requirements.Caches):
                errors.append((
                    "{}.{}.Requirements".format(cls.__module__, cls.__name__),
                    sdk2.Requirements.Caches,
                    "sdk2.Requirements.Caches"
                ))

    if not errors:
        return

    details = [
        "* `{}.{}` must be a subclass of `{}`".format(path, inner_cls.__name__, cls_path)
        for path, inner_cls, cls_path in errors
    ]
    msg = "Invalid type of inner classes:\n{}"
    pytest.fail(msg.format("\n".join(details)))


@pytest.mark.usefixtures("project_types")
def test__important_task_classes():
    """
    Check that projects contains classes of several important tasks
    Inside the binary, TYPES are not imported, so them can't be checked
    """
    if system.inside_the_binary:
        return

    important_tasks = {
        "YA_MAKE",
        "YA_MAKE_2",
        "YA_PACKAGE",
        "YA_PACKAGE_2"
        "HTTP_UPLOAD",
        "HTTP_UPLOAD_2",
        "MDS_UPLOAD",
        "SANDBOX_ACCEPTANCE",
    }

    for task_type in projects.TYPES:
        if task_type in important_tasks:
            important_tasks.remove(task_type)
    if important_tasks:
        pytest.fail("This important task classes are not found: {}".format(important_tasks))
