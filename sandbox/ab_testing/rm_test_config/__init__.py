from sandbox.projects.release_machine.core import const as rm_const


RESTART_POLICY = (
    # Restart attempt #1
    {
        "sleep_before_action": 0,  # min
        "default_action": rm_const.RestartPolicyActions.NOOP,
        "override_default_action": {
            "EXCEPTION": rm_const.RestartPolicyActions.RESTART,
            "FAILURE": rm_const.RestartPolicyActions.RECREATE,
            "TIMEOUT": rm_const.RestartPolicyActions.RESTART,
        },
    },
    # Restart attempt #2
    {
        "sleep_before_action": 5,  # min
        "default_action": rm_const.RestartPolicyActions.NOOP,
        "override_default_action": {
            "EXCEPTION": rm_const.RestartPolicyActions.RECREATE,
            "FAILURE": rm_const.RestartPolicyActions.RECREATE,
            "TIMEOUT": rm_const.RestartPolicyActions.RECREATE,
        },
    },
)


def job_params(**kwargs):
    result = {
        "cancel_fallbehind_runs_on_fix": False,
        "restart_policy": RESTART_POLICY,
    }
    result.update(**kwargs)
    return result
