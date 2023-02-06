"""Tests for rotate_s3_backups"""
import logging as log
from typing import List, NamedTuple, Dict, Tuple, Optional
from types import SimpleNamespace
from pytest_mock import MockFixture
from datetime import timedelta, datetime

from sandbox.projects.media.admins.MediaRotateS3Backups import (BackupRotate,
                                                                BackupMonitoring,
                                                                BackupItem,
                                                                Policy,
                                                                S3Client,
                                                                JugglerStatus,
                                                                JugglerEvent,
                                                                )

TPL = "backup/mysql/maindb/%F"


def test_select_valid():
    worker = BackupRotate(from_last=True, policy=None, s3client=None)
    now_ts = datetime.now() - timedelta(days=666)
    DAYS = 393

    backups_list = []
    for delta in range(DAYS):
        path = (now_ts + timedelta(days=delta)).strftime(TPL)
        backups_list.append(BackupItem(path=path))

    expected_rotation_ts = backups_list[-1].timestamp

    assert len(backups_list) == DAYS

    worker.rotate_from_last_backup = True
    rotation_ts = worker.get_now_timestamp(backups_list)

    assert expected_rotation_ts == rotation_ts

    backup_groups = worker.group_by_frequency(backups_list)
    policy = Policy(daily=5, weekly=1, monthly=1)
    worker.select_valid(backup_groups, rotation_ts, policy)

    valid_backups = [b for b in backups_list if b.state == BackupItem.NORMAL]
    expect_by_policy = sum(policy._asdict().values())
    assert len(valid_backups) == expect_by_policy


def test_removed(mocker: MockFixture):
    backups_count = 60

    ts = datetime.strptime("20201216", "%Y%m%d")

    backups = [
        BackupItem((ts - timedelta(days=i)).strftime(TPL))
        for i in range(backups_count)
    ]

    def ls(_self, _prefix: str = None) -> List[BackupItem]:
        # reset backup state
        for b in backups:
            b.state = BackupItem.NONE
        return backups
    mocker.patch(
        'sandbox.projects.media.admins.MediaRotateS3Backups.S3Client.list_backups',
        ls
    )

    def init(self: S3Client, *_args, **_kwargs):
        self.dry_run = True
        self.check_path_len = True
        self.check_completed_re = True
    mocker.patch(
        'sandbox.projects.media.admins.MediaRotateS3Backups.S3Client.__init__',
        init
    )

    s3cli = S3Client(path="", access_key="", secret_key="", dry_run=True)
    s3cli.check_path_len = True

    policies = [
        (3,  55, Policy(daily=1,  weekly=1,  monthly=1)),
        (5,  54, Policy(daily=3,  weekly=1,  monthly=1)),
        (6,  52, Policy(daily=1,  weekly=4,  monthly=1)),
        (10, 49, Policy(daily=5,  weekly=3,  monthly=2)),
        (15, 42, Policy(daily=9,  weekly=5,  monthly=2)),
        (15, 42, Policy(daily=9,  weekly=5,  monthly=9)),
        (2,  57, Policy(daily=0,  weekly=1,  monthly=1)),
        (2,  56, Policy(daily=1,  weekly=0,  monthly=1)),
        (2,  56, Policy(daily=1,  weekly=1,  monthly=0)),
        (15, 44, Policy(daily=12, weekly=1,  monthly=9)),
        (10, 47, Policy(daily=1,  weekly=12, monthly=9)),
    ]

    for idx, (e_normal, e_removed, policy) in enumerate(policies):
        worker = BackupRotate(from_last=True, policy=policy, s3client=s3cli)
        removed = worker.run()
        log.info(f"Test case #{idx} {policy}")
        assert e_normal == sum(1 for b in backups if b.state == BackupItem.NORMAL)
        assert e_removed == removed


BackupStats = NamedTuple("BackupStats", [("size", int), ("completed", bool)])
MonitoringTestCaseItem = NamedTuple("MonitoringTestCaseItem", [
    ("now", Optional[datetime]),
    ("policy", Policy),
    ("events", List[JugglerEvent]),
    ("backups", Dict[BackupItem, BackupStats]),
    ("skip_size_check_for_names", List[str]),
    ("skip_count_check", bool),
])


BUCKET = "music"


def jevent(service: str, status: JugglerStatus) -> JugglerEvent:
    return JugglerEvent(
        host=f"{BUCKET}-s3-backups",
        service=service,
        status=status,
        description=f"{status}",
        tags=BackupMonitoring.build_juggler_tags(BUCKET)
    )


def jevents_equal(left: JugglerEvent, right: JugglerEvent) -> bool:
    le = JugglerEvent(**{**left._asdict(),  "description": f"{left.status}"})
    re = JugglerEvent(**{**right._asdict(), "description": f"{right.status}"})
    return le == re


def test_monitoring(mocker: MockFixture):

    cases = {
        "all ok": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.OK)],
            backups={
                BackupItem("b/t/n/2017-09-04"): BackupStats(size=7, completed=True),
                BackupItem("b/t/n/2017-09-05"): BackupStats(size=7, completed=True),
                BackupItem("b/t/n/2017-09-06"): BackupStats(size=7, completed=True),
            },
            skip_size_check_for_names=[],
            skip_count_check=False,
        ),
        "all ok with size diff accepted": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.OK)],
            backups={
                BackupItem("b/t/n/2017-09-01"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-02"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-03"): BackupStats(size=90, completed=True),
            },
            skip_size_check_for_names=[],
            skip_count_check=False,
        ),
        "ok, but some backups too small": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.OK)],
            backups={
                BackupItem("b/t/n/2017-09-01"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-02"): BackupStats(size=50, completed=True),
                BackupItem("b/t/n/2017-09-03"): BackupStats(size=100, completed=True),
            },
            skip_size_check_for_names=[],
            skip_count_check=False,
        ),
        "ok and crit with size diff": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[
                jevent("t/n", JugglerStatus.OK),
                jevent("t/c", JugglerStatus.CRIT),
                jevent("t/b", JugglerStatus.CRIT),
            ],
            backups={
                BackupItem("b/t/n/2017-09-04"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-05"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-06"): BackupStats(size=90, completed=True),

                BackupItem("b/t/c/2017-09-04"): BackupStats(size=100, completed=True),
                BackupItem("b/t/c/2017-09-05"): BackupStats(size=100, completed=True),
                BackupItem("b/t/c/2017-09-06"): BackupStats(size=70, completed=True),

                BackupItem("b/t/b/2017-09-04"): BackupStats(size=100, completed=True),
                BackupItem("b/t/b/2017-09-05"): BackupStats(size=100, completed=True),
                BackupItem("b/t/b/2017-09-06"): BackupStats(size=201, completed=True),
            },
            skip_size_check_for_names=[],
            skip_count_check=False,
        ),
        "crit and ok, skip size check": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/m", JugglerStatus.CRIT), jevent("t/c", JugglerStatus.OK)],
            backups={
                BackupItem("b/t/m/2017-09-01"): BackupStats(size=100, completed=True),
                BackupItem("b/t/m/2017-09-02"): BackupStats(size=100, completed=True),
                BackupItem("b/t/m/2017-09-03"): BackupStats(size=10, completed=True),

                BackupItem("b/t/c/2017-09-01"): BackupStats(size=1, completed=True),
                BackupItem("b/t/c/2017-09-02"): BackupStats(size=1, completed=True),
                BackupItem("b/t/c/2017-09-03"): BackupStats(size=100, completed=True),
            },
            skip_size_check_for_names=["c"],
            skip_count_check=False,
        ),
        "crit missing last": MonitoringTestCaseItem(
            now=datetime(2017, 9, 4, 11, 1),
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.CRIT)],
            backups={
                BackupItem("b/t/n/2017-09-01"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-02"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-03"): BackupStats(size=100, completed=True),
            },
            skip_size_check_for_names=[],
            skip_count_check=False,
        ),
        "cirt last and prev incomplete": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.CRIT)],
            backups={
                BackupItem("b/t/n/2017-09-01"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-02"): BackupStats(size=100, completed=False),
                BackupItem("b/t/n/2017-09-03"): BackupStats(size=100, completed=False),
            },
            skip_size_check_for_names=[],
            skip_count_check=False,
        ),
        "ok, skip count check and last exists and complete": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.OK)],
            backups={
                BackupItem("b/t/n/2017-09-03"): BackupStats(size=100, completed=True),
            },
            skip_size_check_for_names=[],
            skip_count_check=True,
        ),
        "crit, skip count check but only last exists and complete": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.CRIT)],
            backups={
                BackupItem("b/t/n/2017-09-03"): BackupStats(size=100, completed=True),
            },
            skip_size_check_for_names=[],
            skip_count_check=False,
        ),
        "ok, skip count check, but last incomplete and prev complete": MonitoringTestCaseItem(
            now=None,
            policy=Policy(daily=3, weekly=0, monthly=0),
            events=[jevent("t/n", JugglerStatus.OK)],
            backups={
                BackupItem("b/t/n/2017-09-02"): BackupStats(size=100, completed=True),
                BackupItem("b/t/n/2017-09-03"): BackupStats(size=100, completed=False),
            },
            skip_size_check_for_names=[],
            skip_count_check=True,
        ),
    }

    def init(self: S3Client, *_args, **kwargs):
        self.prefix = kwargs["path"]
        self.check_path_len = True
        self.check_completed_re = True
        self.bucket = SimpleNamespace(name=BUCKET)
    mocker.patch('sandbox.projects.media.admins.MediaRotateS3Backups.S3Client.__init__', init)

    def ls(self, _prefix: str = None) -> List[BackupItem]:
        return list(cases[self.prefix].backups.keys())
    mocker.patch('sandbox.projects.media.admins.MediaRotateS3Backups.S3Client.list_backups', ls)

    def completed(self, backup: BackupItem) -> bool:
        return cases[self.prefix].backups[backup].completed
    mocker.patch('sandbox.projects.media.admins.MediaRotateS3Backups.S3Client.completed', completed)

    def du(self, backup: BackupItem) -> Tuple[int, int]:
        size = cases[self.prefix].backups[backup].size
        return (size, size)
    mocker.patch('sandbox.projects.media.admins.MediaRotateS3Backups.S3Client.du', du)

    for (name, case) in cases.items():
        now = case.now or sorted(x.timestamp for x in case.backups.keys())[-1]
        log.info(f"Case {name} now timestamp {now}")

        s3cli = S3Client(path=name, access_key="", secret_key="", dry_run=True)
        s3cli.check_path_len = True
        worker = BackupMonitoring(
            policy=case.policy,
            s3client=s3cli,
            skip_size_check=bool(case.skip_size_check_for_names),
            skip_names=case.skip_size_check_for_names,
            skip_count_check=case.skip_count_check,
            now=now,
        )
        events = worker.run()
        assert len(events) == len(case.events)
        for (got, want) in zip(events, case.events):
            assert jevents_equal(got, want)
