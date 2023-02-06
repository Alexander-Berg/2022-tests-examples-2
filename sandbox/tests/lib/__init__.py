import __builtin__

import os
import sys
import copy

from sandbox import common


def is_subpath_of_any(src, allowed_paths):
    return any(
        src == path or src.startswith(path + os.sep)
        for path in allowed_paths
    )


class CheckEnvironWrapper(object):
    def __init__(self):
        self.env_before = self.collect_environ()

    @staticmethod
    def collect_environ():
        env = {"os.environ['{}']".format(k): v for k, v in os.environ.iteritems()}

        sys_getters = (
            "getcheckinterval",
            "getdefaultencoding",
            "getdlopenflags",
            "getfilesystemencoding",
            "getprofile",
            "getrecursionlimit",
            "gettrace",
        )
        for getter in sys_getters:
            env["sys.{}()".format(getter)] = copy.copy(getattr(sys, getter)())

        sys_attrs = (
            "path",
            "path_hooks",
        )
        for attr in sys_attrs:
            env["sys.{}".format(attr)] = copy.copy(getattr(sys, attr))

        # FIXME: SANDBOX-6872: set default encoding globally
        env["sys.getdefaultencoding()"] = "utf8"

        return env

    @staticmethod
    def compare_environs(before, after):
        common_keys = set(before).intersection(set(after))
        diff = set(k for k in common_keys if before[k] != after[k])
        deleted = set(before) - set(after)
        added = set(after) - set(before)
        return sorted(set.union(diff, deleted, added))

    def __call__(self, import_func, pkg, *args, **kwargs):
        mod = import_func(pkg, *args, **kwargs)

        env_after = self.collect_environ()
        if self.env_before != env_after:
            diff = self.compare_environs(self.env_before, env_after)
            self.env_before = env_after
            raise AssertionError("`{}` changes Python environment during import: {}".format(pkg, ", ".join(diff)))
        return mod


class BinaryImportGuard(object):
    """
    This hook restricts packages imported on the top level only to these allowed
    (system ones, or installed in virtual environment) by putting additional checks
    around library.python.runtime.resource.ResourceImporter's import mechanisms.

    The list of allowed modules is read from this binary's build list and sandbox/virtualenv;
    paths which are tough to match are hard-coded instead.
    """

    ERROR_TEMPLATE = (
        "\"{}\" from {} is forbidden to be imported on the top level: "
        "only system modules and these from Sandbox's virtual environment are allowed"
    )

    HARDCODED_PATHS = {
        "contrib/libs/protobuf/python/google",
        "subprocess.py",
        "skynet/kernel",
        "library/python/runtime/__res.pyx",
    }

    PEERDIRS_ALLOWED_FROM = ("contrib", "skynet")

    def __init__(self, importer, *yamakes):
        self.importer = importer
        self.loader = None
        self.yamakes = yamakes
        self.__original_import = __builtin__.__import__
        self.builtins = set(sys.builtin_module_names)

    def __enter__(self):
        sys.meta_path.insert(0, self)

        self.__original_import = __builtin__.__import__
        __builtin__.__import__ = self.import_wrapper

        return self

    def __exit__(self, *_):
        sys.meta_path.remove(self)
        __builtin__.__import__ = self.__original_import

    def import_wrapper(self, name, *args, **kwargs):
        """
        This is intended to catch builtins that reside in Arcadia and bypass import hooks (see: SANDBOX-7070).
        Python treats them as regular builtin modules, so an additional chech is required.

        The other modules are dealt with by the import hook itself in find_module()/load_module() functions
        """

        module = self.__original_import(name, *args, **kwargs)
        module_path = getattr(module, "__file__", None)
        if (
            name in self.builtins and
            module_path is not None and
            not self.is_module_allowed(module_path)
        ):
            raise ImportError(self.ERROR_TEMPLATE.format(name, module_path))

        return module

    def extract_allowed_paths(self, ya_make):
        dependencies_node = ya_make.find_siblings("PEERDIR")[0]
        return set(filter(
            lambda path: is_subpath_of_any(path, self.PEERDIRS_ALLOWED_FROM),
            (value.path for value in dependencies_node.get_values())
        ))

    @common.utils.singleton_property
    def allowed_paths(self):
        """
        Return modules from PEERDIR section of this binary's build list,
        which acts as a virtual environment
        """

        return set.union(self.HARDCODED_PATHS, *map(self.extract_allowed_paths, self.yamakes))

    def is_module_allowed(self, source):
        return (
            source.endswith("<frozen>")  # system module (built-in)
            or source.startswith("sandbox")
            or is_subpath_of_any(source, self.allowed_paths)
        )

    def find_module(self, fullname, path=None):
        self.loader = self.importer.find_module(fullname, path)
        if self.loader:
            return self
        else:
            return None  # other import hooks will do the job

    def load_module(self, modname):
        res = self.loader.load_module(modname)
        source_location = res.__file__
        if not self.is_module_allowed(source_location):
            raise ImportError(self.ERROR_TEMPLATE.format(modname, source_location))
        return res


class PlainImportGuard(object):
    def __init__(self, *a, **kw):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a, **kw):
        pass
