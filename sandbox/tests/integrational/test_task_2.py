import json
import subprocess as sp

import pytest

from sandbox.common import system
import sandbox.common.types.task as ctt

TEST_SQUASHFS_IMAGE_RESOURCE_ID = 1772492881


@pytest.mark.skipif(not system.inside_the_binary(), reason="Binary required")
def test__binary_test_task_2_on_prod():
    import yatest.common
    task_binary = yatest.common.binary_path("sandbox/projects/sandbox/test_task_2/test_task_2_py2/test_task_2")
    payload = {
        "custom_fields": [
            {"name": "mount_image", "value": TEST_SQUASHFS_IMAGE_RESOURCE_ID},
        ],
        "requirements": {
            "caches": {},
            "client_tags": "LXC | PORTOD",
        },
    }
    cmd = [task_binary, "run", "--no-auth", "--wait", "-o", "OTHER", "--force", "--skynet", json.dumps(payload)]
    proc = sp.Popen(cmd, close_fds=True, stdout=sp.PIPE)
    out = proc.communicate()[0]
    assert json.loads(out)["task"]["execution_status"] == ctt.Status.SUCCESS
