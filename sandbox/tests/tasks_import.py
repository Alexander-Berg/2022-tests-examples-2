import ctypes.util
import os
import sys
import pytest
import inspect
import threading as th
import subprocess as sp
import collections
import subprocess32 as sp32
import multiprocessing as mp
import __builtin__

from sandbox import common

from sandbox import sdk2
import sandbox.sdk2.legacy


def monkeypatch_forbidden_calls(mpatch):
    msg_tmpl = "Usage of {} is denied in __init__.py, task modules"
    mpatch.setattr(
        common.proxy,
        "ReliableServerProxy",
        type(
            "ReliableServerProxyAsserter", (object,),
            dict(__init__=lambda *args, **kws: pytest.fail(msg_tmpl.format("XMLRPC client")))
        )
    )

    allowed_popen = [
        sandbox.sdk2.legacy.SandboxSvnUrlParameter.cast.im_func.__code__.co_code,
        sandbox.sdk2.legacy.SandboxArcadiaUrlParameter.cast.im_func.__code__.co_code,
        ctypes.util.find_library.__code__.co_code,
    ]

    try:
        allowed_popen.append(sandbox.common.projects_handler.py3_modules.__code__.co_code)
    except AttributeError:
        # TODO: for backward compatibility
        pass

    def patched_popen(module):
        original_popen = module.Popen

        def popen(*args, **kwargs):
            if inspect.currentframe().f_back.f_back.f_code.co_code in allowed_popen:
                return original_popen(*args, **kwargs)
            return pytest.fail(msg_tmpl.format("{}.Popen".format(module.__name__)))

        popen.__patched__ = True
        return popen

    for mod in (sp, sp32, sdk2.helpers.subprocess):
        if not getattr(mod.Popen, "__patched__", False):
            mpatch.setattr(
                mod,
                "Popen",
                patched_popen(mod)
            )
        mpatch.setattr(
            mod,
            "call",
            lambda *args, **kws: pytest.fail(msg_tmpl.format("{}.call".format(mod.__name__)))
        )

        mpatch.setattr(
            mod,
            "call",
            lambda *args, **kws: pytest.fail(msg_tmpl.format("{}.call".format(mod.__name__)))
        )

    orig_open = __builtin__.open
    disabled_open_flags = ("w", "a", "r+")
    mpatch.setattr(
        __builtin__,
        "open",
        lambda *args, **kws: (
            pytest.fail(msg_tmpl.format("open"))
            if any(f in kws.get("mode", args[1] if len(args) > 1 else "") for f in disabled_open_flags)
            and os.devnull not in args[:1] else
            orig_open(*args, **kws)
        )
    )

    orig_os_open = os.open
    disabled_os_open_flags = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT
    mpatch.setattr(
        os,
        "open",
        lambda *args, **kws: (
            pytest.fail(msg_tmpl.format("os.open"))
            if len(args) > 1 and args[1] != 0 and args[1] | disabled_os_open_flags == disabled_os_open_flags else
            orig_os_open(*args, **kws)
        )
    )
    for sym, attr in ((mp.Pool, "__init__"), (th.Thread, "__init__")):
        mpatch.setattr(
            sym, attr,
            lambda *args, **kws: pytest.fail(msg_tmpl.format("{}.{}.{}".format(sym.__module__, sym.__name__, attr)))
        )


def monkeypatch_forbidden_imports(mpatch):
    orig_import = __builtin__.__import__

    def new_import(*args, **kwargs):
        if args and (args[0] == "api" or args[0].startswith("api.")):
            pytest.fail(
                "Usage of skynet.api is forbidden in module scope. It is made to ensure tasks build for linux systems "
                "where skynet service is not available (notebooks for example)."
            )
        return orig_import(*args, **kwargs)

    mpatch.setattr(__builtin__, "__import__", new_import)


def clear_project_modules():
    projects_path = os.path.dirname(os.path.dirname(__file__))
    type(sdk2.Task).__registry__.clear()
    type(sdk2.Resource).__registry__.clear()
    for name in sys.modules.keys():
        m = sys.modules[name]
        if m and getattr(m, "__file__", None) and m.__file__.startswith(projects_path):
            rel_dir = os.path.dirname(m.__file__[len(projects_path):])
            parts = filter(None, rel_dir.split(os.path.sep))
            if len(parts) > 0 and parts[0] not in ("tests", "resource_types"):
                del sys.modules[name]


def check_resources():
    import sandbox.projects.resource_types as rt
    for res in rt.AbstractResource:
        msg = "Resource {} description must be `str`, not `unicode`".format(res)
        assert not (res.__doc__ and isinstance(res.__doc__, unicode)), msg


def check_container_resources():
    """
    Require that all resources accepted by `Container` parameters are compatible with `Requirements.container_resource`
    """
    from sandbox import projects

    container_types = collections.defaultdict(list)

    for task_type, task in projects.TYPES.iteritems():
        task_cls = task.cls
        if not hasattr(task_cls, "Parameters"):
            continue

        container_params = filter(lambda p: issubclass(p, sdk2.parameters.Container), task_cls.Parameters)

        for param in container_params:
            if isinstance(param.resource_type, basestring):
                resource_types = [param.resource_type]
            else:
                resource_types = [str(t) for t in param.resource_type]

            for type_ in resource_types:
                if type_ != "LXC_CONTAINER":
                    container_types[type_].append(task_type)

    errors = []

    for container_type, tasks in container_types.iteritems():
        resource = sdk2.Resource[container_type]
        if not issubclass(resource, sdk2.service_resources.LxcContainer):
            errors.append(
                "* {} (used in tasks {})"
                .format(container_type, ', '.join(tasks))
            )

    if errors:
        msg = "The following resource types must subclass from `sdk2.service_resources.LxcContainer`:\n{}"
        pytest.fail(msg.format("\n".join(errors)))


def test_imports(monkeypatch):
    clear_project_modules()
    monkeypatch_forbidden_calls(monkeypatch)
    if common.system.inside_the_binary():
        monkeypatch_forbidden_imports(monkeypatch)
    os.chdir("/")
    common.projects_handler.load_project_types(True, force_from_fs=True)
    check_resources()
    check_container_resources()
