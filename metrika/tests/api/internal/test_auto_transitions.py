import pytest

import metrika.admin.python.cms.lib.fsm.states as cms_fsm
from metrika.admin.python.cms.judge.lib import helpers as judge_helpers

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.usefixtures("noop_queue")
]


def test_auto_unload(steps):
    with steps.config.override({"auto_unload": True}):
        id = steps.make_task(cms_fsm.States.MAKING_DECISION)
        check_points = steps.make_transition(id, cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.UNLOADING,
                                                  expected_audit=[
                                                      (cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD),
                                                      (cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, cms_fsm.States.UNLOADING),
                                                  ],
                                                  **check_points)
        steps.verify()


def test_no_auto_unload(steps):
    with steps.config.override({"auto_unload": False}):
        id = steps.make_task(cms_fsm.States.MAKING_DECISION)
        check_points = steps.make_transition(id, cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD,
                                                  expected_audit=[
                                                      (cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD),
                                                  ],
                                                  **check_points)
        steps.verify()


def test_auto_unload_action(steps):
    with steps.config.override({"auto_unload": False, "auto_unload_per_action": {"change-disk": True}}):
        id = steps.make_task(cms_fsm.States.MAKING_DECISION, "change-disk")
        check_points = steps.make_transition(id, cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.UNLOADING,
                                                  expected_audit=[
                                                      (cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD),
                                                      (cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, cms_fsm.States.UNLOADING),
                                                  ],
                                                  **check_points)
        steps.verify()


def test_no_auto_unload_action(steps):
    with steps.config.override({"auto_unload": False, "auto_unload_per_action": {"change-disk": True}}):
        id = steps.make_task(cms_fsm.States.MAKING_DECISION, "change-memory")
        check_points = steps.make_transition(id, cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD,
                                                  expected_audit=[
                                                      (cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD),
                                                  ],
                                                  **check_points)
        steps.verify()


def test_auto_approve(steps):
    with steps.config.override({"auto_approve": True}):
        id = steps.make_task(cms_fsm.States.UNLOADING)
        check_points = steps.make_transition(id, cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE,
                                                  expected_audit=[
                                                      (cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK),
                                                      (cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE),
                                                  ],
                                                  **check_points)
        steps.verify()


def test_no_auto_approve(steps):
    with steps.config.override({"auto_approve": False}):
        id = steps.make_task(cms_fsm.States.UNLOADING)
        check_points = steps.make_transition(id, cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.WAIT_FOR_APPROVAL_OK,
                                                  expected_audit=[
                                                      (cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK),
                                                  ],
                                                  **check_points)
        steps.verify()


def test_auto_approve_action(steps):
    with steps.config.override({"auto_approve": False, "auto_approve_per_action": {"change-disk": True}}):
        id = steps.make_task(cms_fsm.States.UNLOADING, "change-disk")
        check_points = steps.make_transition(id, cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE,
                                                  expected_audit=[
                                                      (cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK),
                                                      (cms_fsm.States.WAIT_FOR_APPROVAL_OK, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE),
                                                  ],
                                                  **check_points)

        steps.verify()


def test_no_auto_approve_action(steps):
    with steps.config.override({"auto_approve": False, "auto_approve_per_action": {"change-disk": True}}):
        id = steps.make_task(cms_fsm.States.UNLOADING, "change-memory")
        check_points = steps.make_transition(id, cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK)
        steps.assert_that.success_auto_transition(target_state=cms_fsm.States.WAIT_FOR_APPROVAL_OK,
                                                  expected_audit=[
                                                      (cms_fsm.States.UNLOADING, cms_fsm.States.WAIT_FOR_APPROVAL_OK),
                                                  ],
                                                  **check_points)
        steps.verify()


@pytest.mark.parametrize("skip_load, supported", [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_skip_unload(steps, monkeypatch, skip_load, supported):
    must_skip = skip_load and not supported
    monkeypatch.setattr(judge_helpers, "host_is_supported", lambda *args, **kwargs: supported)
    with steps.config.override({"skip_load_for_temporary_unreachable": skip_load}):
        id = steps.make_task(cms_fsm.States.MAKING_DECISION, "temporary-unreachable")
        check_points = steps.make_transition(id, cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD)
        steps.assert_that.success_auto_transition(
            target_state=cms_fsm.States.WAIT_FOR_APPROVAL_OK if must_skip else cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD,
            expected_audit=(
                [
                    (cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD),
                    (cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD, cms_fsm.States.WAIT_FOR_APPROVAL_OK)
                ]
                if must_skip else
                [
                    (cms_fsm.States.MAKING_DECISION, cms_fsm.States.WAIT_FOR_APPROVAL_UNLOAD)
                ]
            ),
            **check_points
        )
        steps.verify()


@pytest.mark.parametrize("skip_load, supported", [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
def test_skip_load(steps, monkeypatch, skip_load, supported):
    must_skip = skip_load and not supported
    monkeypatch.setattr(judge_helpers, "host_is_supported", lambda *args, **kwargs: supported)
    with steps.config.override({"skip_load_for_temporary_unreachable": skip_load}):
        id = steps.make_task(cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, "temporary-unreachable")
        check_points = steps.make_transition(id, cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, cms_fsm.States.INITIATE_LOADING)
        steps.assert_that.success_auto_transition(
            target_state=cms_fsm.States.COMPLETED if must_skip else cms_fsm.States.INITIATE_LOADING,
            expected_audit=(
                [
                    (cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, cms_fsm.States.INITIATE_LOADING),
                    (cms_fsm.States.INITIATE_LOADING, cms_fsm.States.COMPLETED)
                ]
                if must_skip else
                [
                    (cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE, cms_fsm.States.INITIATE_LOADING)
                ]
            ),
            **check_points,
            is_walle_deleted=True
        )
        steps.verify()
