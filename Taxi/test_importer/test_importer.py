import os
import sys

from replication.common import local_importer

_IMPORTS_TO_TEST = (
    'test_replication.common.test_importer.test_package',
    'test_replication.common.test_importer.test_package.some_module',
    'test_replication.common.test_importer.test_package.third_module',
)


def test_local_importer():
    importer = local_importer.Importer()  # noqa: F821 pylint: disable=E0602
    for _import in _IMPORTS_TO_TEST:
        assert _import not in sys.modules
    with importer.get_importer(os.path.dirname(__file__)):
        from . import test_package  # noqa: F401
        from .test_package import some_module  # noqa: F401
        from .test_package.some_module import third_module  # noqa: F401
        for _import in _IMPORTS_TO_TEST:
            assert _import in sys.modules
    for _import in _IMPORTS_TO_TEST:
        assert _import not in sys.modules
