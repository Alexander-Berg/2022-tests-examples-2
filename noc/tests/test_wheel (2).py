import os

import test.tests.common as tests_common
import yatest.common


def test_create_wheel():
    res = tests_common.run_ya_package(
        packages=[yatest.common.test_source_path("../wheel.json")],
        args=["--wheel", "--wheel-python3"],
        source_root="../../",
    )
    assert res.exit_code == 0

    pkg_path = os.path.join(res.output_root, "rtapi-0.13-py3-none-any.whl")
    assert os.path.exists(pkg_path)

    pack_dir = os.path.join(res.output_root, "unzipped_package")
    os.makedirs(pack_dir)
    import zipfile

    with zipfile.ZipFile(pkg_path, "r") as zip_ref:
        zip_ref.extractall(pack_dir)

    yatest.common.execute(["python3", "-c", "import aiortapi"], cwd=pack_dir)
    yatest.common.execute(["python3", "-c", "import aiosshagent"], cwd=pack_dir)
    yatest.common.execute(["python3", "-c", "import rtapi"], cwd=pack_dir)
    yatest.common.execute(["python3", "-c", "import sshagent"], cwd=pack_dir)
