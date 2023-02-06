from unittest.mock import AsyncMock, Mock, patch

import pytest

from checkist.models.device import Device
from checkist.patches.patch import Patch, PatchFile


@pytest.mark.asyncio
@pytest.mark.parametrize("req, result, code, deploy_args", (
    (
        {
            "ticket": "NOCRFCS-1234",
            "patches": [
                {
                    "hostname": "noc-sas",
                    "patch": {"": "my patch"},
                    "run_config_hash": "5f8f42ebfb523b71fd7add7d",
                    "run_before": 123456,
                    "run_after": 654321,
                    "after": [],
                    "before": [],
                    "reloads": {},
                },
                {
                    "hostname": "noc-myt",
                    "patch": {
                        "/tmp/a": "bb",
                    },
                    "run_config_hash": "",
                    "before": ["etckeeper check"],
                    "after": ["etckeeper commitreload"],
                    "reloads": {"/tmp/a": ""},
                }
            ]
        },
        [
            {
                "hostname": "noc-sas",
                "job_id": "id1",
            },
            {
                "hostname": "noc-myt",
                "job_id": "id2",
            }
        ],
        200,
        (
            "robot-test",
            "NOCRFCS-1234",
            Patch(
                hostname='noc-sas',
                raw='my patch',
                files=[],
                config_md5='5f8f42ebfb523b71fd7add7d',
                run_before=123456,
                run_after=654321,
                object_id=666,
            ),
            Patch(
                hostname='noc-myt',
                raw='',
                files=[
                    PatchFile(
                        path="/tmp/a",
                        content="bb",
                        before=["etckeeper check"],
                        commands=["etckeeper commitreload"],
                    )
                ],
                config_md5='',
                run_before=None,
                run_after=None,
                object_id=777,
            ),
        ),
    ),
    (
        {
            "ticket": "NOCRFCS-1234",
            "patches": [
                {
                    "hostname": "noc-sas",
                    "patch_text": {"": "my patch"},
                    "run_config_hash": "5f8f42ebfb523b71fd7add7d",
                    "run_before": 123456,
                    "run_after": 654321,
                    "after": [],
                    "before": [],
                    "reloads": {},
                },
                {
                    "hostname": "noc-myt",
                    "patch_text": {
                        "/tmp/a": "bb",
                    },
                    "run_config_hash": "",
                    "after": [],
                    "before": [],
                    "reloads": {"/tmp/a": "service a restart"},
                }
            ]
        },
        [
            {
                "hostname": "noc-sas",
                "job_id": "id1",
            },
            {
                "hostname": "noc-myt",
                "job_id": "id2",
            }
        ],
        200,
        (
            "robot-test",
            "NOCRFCS-1234",
            Patch(
                hostname='noc-sas',
                raw='my patch',
                files=[],
                config_md5='5f8f42ebfb523b71fd7add7d',
                run_before=123456,
                run_after=654321,
                object_id=666,
            ),
            Patch(
                hostname='noc-myt',
                raw='',
                files=[
                    PatchFile(
                        path="/tmp/a",
                        content="bb",
                        before=[],
                        commands=["service a restart"],
                    )
                ],
                config_md5='',
                run_before=None,
                run_after=None,
                object_id=777,
            ),
        ),
    ),
    (
        {
            "patches": [],
        },
        None,
        400,
        (),
    ),
))
async def test_deploy_patch(req, result, code, deploy_args, aiohttp_client, app, core):
    core.patches.deploy = AsyncMock()
    core.patches.deploy.return_value = [Mock(hostname="noc-sas", job_id="id1"), Mock(hostname="noc-myt", job_id="id2")]
    core.devices.search = AsyncMock(return_value={
        666: Device(object_id=666, name="noc-sas", asset_no=None, fqdn=None, etags=None, itags=None, atags=None),
        777: Device(object_id=777, name="noc-myt", asset_no=None, fqdn=None, etags=None, itags=None, atags=None),
    })

    client = await aiohttp_client(app)

    with patch("checkist.api.v1.patches.get_username", return_value="robot-test"):
        resp = await client.post("/v1/patch/deploy", json=req)
    assert resp.status == code
    if result is not None:
        assert result == (await resp.json())["result"]
        core.patches.deploy.assert_called_once_with(*deploy_args)
