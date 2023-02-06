"""Tests for rotate_s3_backups"""
from datetime import timedelta, datetime

from sandbox.projects.media.admins.MediaRotateS3Backups import BackupRotate, BackupItem, Policy

TPL = "backup/dbtype/dbname/%F"


def invalidate(bkp: BackupItem) -> BackupItem:
    bkp.state = BackupItem.NONE
    return bkp


def test_select_valid_by_policy():
    worker = BackupRotate(from_last=True, policy=None, s3client=None)
    policies = [
        {"daily": 1,  "weekly": 1,  "monthly": 1},
        {"daily": 3,  "weekly": 1,  "monthly": 1},
        {"daily": 1,  "weekly": 4,  "monthly": 1},
        {"daily": 5,  "weekly": 3,  "monthly": 2},
        {"daily": 9,  "weekly": 5,  "monthly": 2},
        {"daily": 9,  "weekly": 5,  "monthly": 9},
        {"daily": 0,  "weekly": 1,  "monthly": 1},
        {"daily": 1,  "weekly": 0,  "monthly": 1},
        {"daily": 1,  "weekly": 1,  "monthly": 0},
        {"daily": 12, "weekly": 1,  "monthly": 9},
        {"daily": 1,  "weekly": 12, "monthly": 9},
    ]

    for case in policies:
        print("Case: {}".format(case))
        policy = Policy(**case)
        all_backups = []
        rotation_ts = datetime.strptime("20201216", "%Y%m%d")
        for itr in range(1, 400):
            bkp_ts = rotation_ts - timedelta(days=itr - 1)
            bkp = BackupItem(path=bkp_ts.strftime(TPL))
            all_backups.append(bkp)

            backup_groups = worker.group_by_frequency(all_backups)
            worker.select_valid(backup_groups, rotation_ts, policy)

            desc = "itr"
            but_no_more_then = sum(policy._asdict().values())
            if itr < policy.daily:
                expect = itr
            elif itr < (policy.daily + policy.weekly * 7):
                desc = "daily"
                expect = policy.daily
            elif itr < (policy.daily + policy.weekly * 7 + policy.monthly * 30):
                desc = "daily + weekly"
                expect = policy.daily + policy.weekly
            else:
                desc = "daily + weekly + monthly"
                expect = sum(policy._asdict().values())

            # save only valid backups
            preserve = [b for b in all_backups if b.state != BackupItem.NONE]
            normal_backups = [b for b in preserve if b.state == BackupItem.NORMAL]
            n_normal = len(normal_backups)
            all_backups = [invalidate(b) for b in preserve]
            assert n_normal >= expect and n_normal <= but_no_more_then, (
                f"Iteration {itr}: case={case} expect({desc})>={expect}, "
                f" got={len(normal_backups)} -> {normal_backups}"
            )
