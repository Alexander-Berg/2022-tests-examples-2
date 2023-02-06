import metrika.admin.python.cms.agent.lib.steps.manager as manager
import metrika.admin.python.cms.agent.lib.steps.step as step


def create_checkpoints_manager(**kwargs):
    agent = kwargs.pop("agent")
    return manager.StepsManager(
        agent,
        step.check_running_operation(agent),
        step.check_shell(agent, "step_1", "Always OK checkpoint", ["true"])
    )


def create_unloading_manager(**kwargs):
    agent = kwargs.pop("agent")
    return manager.StepsManager(
        agent,
        step.check_shell(agent, "step_1", "Always OK unloading step", ["true"])
    )


def create_loading_initiate_manager(**kwargs):
    agent = kwargs.pop("agent")
    return manager.StepsManager(
        agent,
        step.check_shell(agent, "step_1", "Always OK loading initiate step", ["true"])
    )


def create_loading_finalize_manager(**kwargs):
    agent = kwargs.pop("agent")
    return manager.StepsManager(
        agent,
        step.check_shell(agent, "step_1", "Always OK loading finalize step", ["true"])
    )


def create_loading_poll_manager(**kwargs):
    agent = kwargs.pop("agent")
    return manager.StepsManager(
        agent,
        step.check_shell(agent, "step_1", "Always OK loading poll step", ["true"])
    )
