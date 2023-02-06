import os
import textwrap

import pytest

import run_import_hook
import yalibrary.makelists

from sandbox.tasks.tests import lib


@pytest.fixture()
def sample_yamake(tmpdir):
    yamake_contents = textwrap.dedent(
        """
        PY2_LIBRARY()
        OWNER(g:sandbox-dev)
        PEERDIR(
            contrib/python/mock
        )
        END()
        """
    )

    target = os.path.join(str(tmpdir), "ya.make")
    with open(target, "w") as fd:
        fd.write(yamake_contents)

    return yalibrary.makelists.from_file(target)


class TestImportGuard(object):
    def test__import_allowed_regular_module(self, sample_yamake):
        with lib.BinaryImportGuard(run_import_hook.importer, sample_yamake):
            import mock  # noqa

    def test__import_disallowed_regular_module(self, sample_yamake):
        with lib.BinaryImportGuard(run_import_hook.importer, sample_yamake):
            with pytest.raises(ImportError) as exc:
                import arrow  # noqa

            # part of lib.BinaryImportGuard.ERROR_TEMPLATE
            assert "is forbidden to be imported on the top level" in str(exc)

    def test_import_allowed_builtin_module(self, sample_yamake):
        with lib.BinaryImportGuard(run_import_hook.importer, sample_yamake):
            import os  # noqa
            import subprocess  # noqa

    def test_import_disallowed_builtin_module(self, sample_yamake):
        with lib.BinaryImportGuard(run_import_hook.importer, sample_yamake):
            with pytest.raises(ImportError) as exc:
                import cityhash  # noqa

            # part of lib.BinaryImportGuard.ERROR_TEMPLATE
            assert "is forbidden to be imported on the top level" in str(exc)
