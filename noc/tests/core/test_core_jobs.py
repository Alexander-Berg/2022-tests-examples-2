import pytest

from checkist.ann.revision import Revision, RevisionState
from checkist.models.job import Job, JobGroup, JobKind, JobStatus
from checkist.utils.iterables import async_next


@pytest.mark.parametrize("job_kwgs, revs_kwgs, must_be_finalized, jobs_pred, revs_pred", (
    (  # empty jobs are finalized
        None,  # job_kwgs
        None,  # revs_kwgs
        True,  # must_be_finalized
        None,  # jobs_pred
        None,  # revs_pred
    ),

    (  # pending stays pending
        [  # job_kwgs
            {
                "job": JobKind.GENERATE_CONFIGS,
                "status": JobStatus.PENDING,
                "payload": {"device_names": ["device1", "device2"], "rev_id": "123"},
            },
        ],
        [  # revs_kwgs
            {
                "id": "123",
                "state": "cooking",
            },
        ],
        False,  # must_be_finalized
        lambda jobs: len(jobs) == 1 and jobs[0].status == JobStatus.PENDING,  # jobs_pred
        lambda revs: len(revs) == 1 and revs[0].state == RevisionState.cooking,  # revs_pred
    ),

    (  # one failed job marks other as failed (if not regression tests)
        [  # job_kwgs
            {
                "job": JobKind.GENERATE_CONFIGS,
                "status": JobStatus.PENDING,
                "payload": {"device_names": ["device1", "device2"], "rev_id": "123"},
            },
            {
                "job": JobKind.GENERATE_CONFIGS,
                "status": JobStatus.FAILED,
                "payload": {"device_names": ["device3", "device4"], "rev_id": "123"},
            },
        ],
        [  # revs_kwgs
            {
                "id": "123",
                "state": "cooking",
            },
        ],
        True,  # must_be_finalized
        lambda jobs: all(j.status == JobStatus.FAILED for j in jobs),  # jobs_pred
        lambda revs: len(revs) == 1 and revs[0].state == RevisionState.failed,  # revs_pred
    ),

    (  # one failed job is ok (if regression tests)
        [  # job_kwgs
            {
                "job": JobKind.TEST_REGRESSION,
                "status": JobStatus.PENDING,
                "payload": {"device_names": ["device1", "device2"], "test_id": "123"},
            },
            {
                "job": JobKind.TEST_REGRESSION,
                "status": JobStatus.FAILED,
                "payload": {"device_names": ["device3", "device4"], "test_id": "123"},
            },
        ],
        None,  # revs_kwgs
        False,  # must_be_finalized
        lambda jobs: jobs[0].status == JobStatus.PENDING and jobs[1].status == JobStatus.FAILED,  # jobs_pred
        None,  # revs_pred
    ),

    (  # all jobs are finished, revision is ready
        [  # job_kwgs
            {
                "job": JobKind.GENERATE_CONFIGS,
                "status": JobStatus.FINISHED,
                "payload": {"device_names": ["device1", "device2"], "rev_id": "123"},
            },
        ],
        [  # revs_kwgs
            {
                "id": "123",
                "state": "cooking",
                "is_approved": False,
                "auto_approve": True,
            },
        ],
        True,  # must_be_finalized
        lambda jobs: len(jobs) == 1 and jobs[0].status == JobStatus.FINISHED,  # jobs_pred
        lambda revs:  len(revs) == 1 and revs[0].state == RevisionState.ready and revs[0].is_approved,  # revs_pred
    ),

    (  # test regenerate
        [  # job_kwgs
            {
                "job": JobKind.REGENERATE_REVISION,
                "status": JobStatus.FINISHED,
                "payload": {"device_names": ["device1", "device2"], "rev_id": "123", "old_rev_id": "345"},
            },
        ],
        [  # revs_kwgs
            {
                "id": "123",
                "state": "cooking",
                "ttl": None,
            },
            {
                "id": "345",
                "state": "ready",
                "is_approved": True,
            },
        ],
        True,  # must_be_finalized
        lambda jobs: len(jobs) == 1 and jobs[0].status == JobStatus.FINISHED,  # jobs_pred
        lambda revs:  len(revs) == 2 and revs[0].state == RevisionState.ready and revs[0].ttl == 30,  # revs_pred
    ),

    (  # exception are handled, but job group is not finalized
        [  # job_kwgs
            {
                "job": JobKind.GENERATE_CONFIGS,
                "status": JobStatus.FINISHED,
                "payload": {"device_names": ["device1", "device2"], "rev_id": "INVALID"},
            },
        ],
        None,  # revs_kwgs
        False,  # must_be_finalized
        lambda jobs: len(jobs) == 1 and jobs[0].status == JobStatus.FINISHED,  # jobs_pred
        None,  # revs_pred
    ),
))
@pytest.mark.asyncio
async def test_finalize_rev_task_workers(job_kwgs, revs_kwgs, must_be_finalized, jobs_pred, revs_pred, core):
    group = JobGroup(core)
    await group.save()

    job_ids = []
    for kwargs in (job_kwgs or []):
        job = Job(core, group_id=group.id, **kwargs)
        await job.save()
        job_ids.append(job.id)

    rev_ids = []
    for kwargs in (revs_kwgs or []):
        rev = Revision(core, **kwargs)
        await rev.save()
        rev_ids.append(rev.id)

    await core.finalize_rev_task_workers()

    group = await async_next(JobGroup.find_by_query(core, {"_id": group.id}))
    assert group.finalized == must_be_finalized

    for cls, ids, pred in ((Job, job_ids, jobs_pred),
                           (Revision, rev_ids, revs_pred)):
        if not pred or not ids:
            continue

        by_id = {}
        async for obj in cls.find_by_query(core, {}):
            by_id[obj.id] = obj

        objs = []
        for id_ in ids:
            objs.append(by_id[id_])

        assert pred(objs)
