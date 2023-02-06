import pytest

import metrika.admin.python.cms.lib.fsm.states as cms_fsm

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.parametrize('internal_status',
                         [
                             cms_fsm.States.OK_WAIT_FOR_WALLE_DELETE,
                             cms_fsm.States.REJECT_WAIT_FOR_WALLE_DELETE,
                         ])
def test_walle_delete_expected(steps, internal_status):
    id = steps.make_task(internal_status)
    steps.assert_that_walle_task_exists(id)
    delete_response = steps.walle_delete(id)
    steps.assert_that.check_response_code(delete_response, 204)
    steps.assert_that_walle_task_does_not_exist(id)
    audit_response = steps.get_audit(id)
    steps.assert_that.audit_contains(audit_response, {"success": True})
    steps.verify()


@pytest.mark.parametrize('internal_status', cms_fsm.States.walle_can_delete_unexpected)
def test_walle_delete_unexpected(steps, internal_status):
    id = steps.make_task(internal_status)
    steps.assert_that_walle_task_exists(id)
    delete_response = steps.walle_delete(id)
    steps.assert_that.check_response_code(delete_response, 204)
    steps.assert_that_walle_task_does_not_exist(id)
    audit = steps.get_audit(id)
    steps.assert_that.audit_contains(audit, {"success": True, "message": "Wall-E deleted task unexpectedly"})
    steps.verify()


@pytest.mark.parametrize('internal_status',
                         [
                             cms_fsm.States.INITIATE_LOADING,
                             cms_fsm.States.WAIT_FOR_LOADING_COMPLETE,
                             cms_fsm.States.FINALIZE_LOADING,
                             cms_fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD,
                             cms_fsm.States.COMPLETED,
                         ])
def test_walle_no_delete(steps, internal_status):
    id = steps.make_task(internal_status)
    steps.assert_that_walle_task_does_not_exist(id)
    delete_response = steps.walle_delete(id)
    steps.assert_that.check_response_code(delete_response, 404)
    steps.assert_that_walle_task_does_not_exist(id)
    audit = steps.get_audit(id)
    steps.assert_that.has_no_audit(audit)
    steps.verify()
