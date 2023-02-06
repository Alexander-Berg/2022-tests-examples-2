import pytest

import metrika.admin.python.cms.frontend.tests.api.internal.data as test_data
import metrika.admin.python.cms.lib.fsm.states as cms_fsm

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.parametrize('subject,success,message,reason,obj', test_data.testdata_audit_positive)
def test_add_audit_positive(steps, subject, success, message, reason, obj):
    id = steps.make_task(cms_fsm.States.INITIAL)
    audit_response = steps.add_audit(id, subject, success, message, reason, obj)
    steps.assert_that.positive_audit(audit_response=audit_response)
    steps.verify()


@pytest.mark.parametrize('subject,success,message,reason,obj', test_data.testdata_audit_negative)
def test_add_audit_negative(steps, subject, success, message, reason, obj):
    id = steps.make_task(cms_fsm.States.INITIAL)
    audit_response = steps.add_audit(id, subject, success, message, reason, obj)
    steps.assert_that.negative_audit(audit_response=audit_response)
    steps.verify()


def test_get_audit(steps):
    id = steps.make_task(cms_fsm.States.INITIAL)
    steps.add_audit(id, "test", True, "Some message", "reason", {})
    audit_response = steps.get_audit(id)
    steps.assert_that.has_audit(audit_response)
    steps.verify()
