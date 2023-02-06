from dmp_suite.maintenance.raw_ctl_updater.updater import make_raw_ctl_updater


ctl_task = make_raw_ctl_updater()


if __name__ == '__main__':
    # Debug only
    from dmp_suite.task.execution import run_task
    run_task(ctl_task)
