import asyncio
import json
import os
from unittest import mock

import pytest

import checkist.core
from checkist.ann import revision, instance
from checkist.models import job, device


@pytest.mark.asyncio
async def test_core_create_rev(core: checkist.core.CheckistCore, ann_instance):
    git_commit_id = "2895c0e07a88c46d24aa1bd121216f633727684c"
    git_remote = "http://localhost/nocdev/annushka"
    core.devices.get_devices_for_diff = mock.AsyncMock(return_value=[
        device.Device(1, 1, "device1", "device1.yndx.net", [], [], []),
        device.Device(1, 1, "device2", "device2.yndx.net", [], [], []),
    ])
    tasks = set(asyncio.all_tasks())
    await core.create_rev(git_commit_id, git_remote)
    tasks = set(asyncio.all_tasks()).difference(tasks)
    await asyncio.gather(*tasks)

    jobs = [x async for x in job.Job.find_by_query(core, {})]
    assert len(jobs) == 1
    assert jobs[0].job == "generate_configs"
    assert jobs[0].type == job.JobType.ANYONE
    assert jobs[0].status == job.JobStatus.PENDING
    assert jobs[0].payload == {'device_names': ['device1', 'device2'], 'rev_id': mock.ANY}


@pytest.mark.asyncio
async def test_core_run_rev_task_worker(core: checkist.core.CheckistCore, ann_instance: instance.AnnInstance):
    rev = await revision.Revision.create_new_rev(
        core,
        ann_instance,
    )
    job_group_id = "job_group_id_xxxxxx"
    spawn_stdout = json.dumps({"success": {}, "fail": {}})
    spawn_mock = mock.AsyncMock(return_value=(spawn_stdout, ""))
    rev_path = f'{core.settings.tmpdir}/rev_task_{job_group_id}'
    with mock.patch.object(instance.AnnInstance, "_spawn", new=spawn_mock):
        await core._run_rev_task_worker(rev.id, ["device1", "device2"], job_group_id)
        spawn_mock.assert_called_with(
            [
                f'{rev_path}/.venv/bin/python',
                f'{rev_path}/ann',
                'x-checkist-unified',
                '--expand-path',
                f'--parallel={os.cpu_count()}',
                '--acl-safe',
                f'--cache={rev_path}/.rtcache',
                '--excluded-gens=WhiteboxTacacs,vault',
                '--tolerate-fails',
                f'--config={rev_path}/.cfglister',
                '--fail-on-empty-config',
                'device1',
                'device2',
            ],
            {
                'COMOCUTOR_LOGIN': 'test-comocutor-login',
                'COMOCUTOR_PASSWORD': 'test-comocutor-password'
            },
        )


@pytest.mark.asyncio
async def test_do_job_generate_configs(core: checkist.core.CheckistCore):
    jobinst = job.Job(
        core=core,
        job="generate_configs",
        group_id='xxx-jobgroup-id',
        payload={'device_names': ['device1', 'device2'], 'rev_id': 'xxx-rev-id'},
    )
    run_rev_task_worker_mock = mock.AsyncMock(return_value=[])
    with mock.patch.object(checkist.core.CheckistCore, "_run_rev_task_worker", new=run_rev_task_worker_mock):
        await core._do_job(jobinst)
        run_rev_task_worker_mock.assert_called_with(
            rev_id='xxx-rev-id',
            device_names=['device1', 'device2'],
            job_group_id='xxx-jobgroup-id'
        )
