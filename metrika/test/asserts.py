import allure
from hamcrest import has_entries, equal_to, contains_inanyorder, not_none, none, contains

import metrika.admin.python.cms.lib.agent.steps.state as steps_state


def _step_status(name, state):
    return has_entries(
        name=name,
        state=equal_to(state),
        started_at=not_none(),
        finished_at=not_none(),
    )


def _step_success(name):
    return _step_status(name, steps_state.State.SUCCESS)


def _step_fail(name):
    return _step_status(name, steps_state.State.FAIL)


class Assert:
    def __init__(self, verification_steps):
        self.verify = verification_steps

    @allure.step
    def host_status_is_success(self, host_status):
        self.verify(host_status, has_entries(
            state=equal_to(steps_state.State.SUCCESS),
            steps=contains_inanyorder(_step_success("running_operations"), _step_success("step_1"))
        ))

    @allure.step
    def host_status_is_fail(self, host_status):
        self.verify(host_status, has_entries(
            state=equal_to(steps_state.State.FAIL),
            steps=contains_inanyorder(_step_success("running_operations"), _step_fail("step_1"))
        ))

    @allure.step
    def host_status_is_fail_timeout(self, host_status):
        self.verify(host_status, has_entries(
            state=equal_to(steps_state.State.FAIL),
            steps=contains_inanyorder(_step_success("running_operations"), _step_status("step_1", steps_state.State.TIMEOUT))
        ))

    @allure.step
    def operation_is_not_started(self, operation_status):
        self.verify(operation_status, has_entries(
            state=equal_to(steps_state.State.NOT_STARTED),
            started_at=none(),
            finished_at=none(),
            steps=contains(
                has_entries(
                    name="step_1",
                    state=steps_state.State.NOT_STARTED,
                    started_at=none(),
                    finished_at=none(),
                )
            )
        ))

    @allure.step
    def loading_status_is_success(self, host_status):
        self.verify(host_status, has_entries(
            state=equal_to(steps_state.State.SUCCESS),
            steps=contains_inanyorder(_step_success("step_1"))
        ))

    @allure.step
    def loading_status_is_fail(self, host_status):
        self.verify(host_status, has_entries(
            state=equal_to(steps_state.State.FAIL),
            steps=contains_inanyorder(_step_fail("step_1"))
        ))

    @allure.step
    def loading_status_is_fail_timeout(self, host_status):
        self.verify(host_status, has_entries(
            state=equal_to(steps_state.State.FAIL),
            steps=contains_inanyorder(_step_status("step_1", steps_state.State.TIMEOUT))
        ))

    @allure.step
    def operation_is_success(self, operation_status):
        self.verify(operation_status, has_entries(
            state=equal_to(steps_state.State.SUCCESS),
            started_at=not_none(),
            finished_at=not_none(),
            steps=contains(
                has_entries(
                    name="step_1",
                    state=steps_state.State.SUCCESS,
                    started_at=not_none(),
                    finished_at=not_none(),
                )
            )
        ))

    @allure.step
    def operation_is_in_progress(self, operation_status):
        self.verify(operation_status, has_entries(
            state=equal_to(steps_state.State.IN_PROGRESS),
            started_at=not_none(),
            finished_at=none(),
            steps=contains(
                has_entries(
                    name="step_1",
                    state=steps_state.State.IN_PROGRESS,
                    started_at=not_none(),
                    finished_at=none(),
                )
            )
        ))
