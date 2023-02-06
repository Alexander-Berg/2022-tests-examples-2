import pytest

import metrika.admin.python.cms.frontend.tests.api.internal.data as test_data

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("noop_queue")
@pytest.mark.parametrize('source_state,target_state,walle_deleted', test_data.testdata_success)
def test_success_transition(steps, source_state, target_state, walle_deleted):
    id = steps.make_task(source_state)
    steps.assert_that.success(is_walle_deleted=walle_deleted, source_state=source_state, target_state=target_state,
                              **steps.make_transition(id, source_state, target_state))
    steps.verify()


@pytest.mark.parametrize('source_state,target_state,walle_deleted', test_data.testdata_fail)
def test_fail_transition(steps, source_state, target_state, walle_deleted):
    id = steps.make_task(source_state)
    steps.assert_that.fail_transition(is_walle_deleted=walle_deleted, source_state=source_state, target_state=target_state,
                                      **steps.make_transition(id, source_state, target_state))
    steps.verify()


@pytest.mark.parametrize('initial_state,source_state,target_state,walle_deleted', test_data.testdata_unexpected)
def test_unexpected_transition(steps, initial_state, source_state, target_state, walle_deleted):
    id = steps.make_task(initial_state)
    steps.assert_that.fail_unexpected_transition(is_walle_deleted=walle_deleted, initial_state=initial_state, source_state=source_state, target_state=target_state,
                                                 **steps.make_transition(id, source_state, target_state))
    steps.verify()


@pytest.mark.parametrize('initial_state,source_state,target_state,walle_deleted', test_data.testdata_invalid)
def test_invalid_choice(steps, initial_state, source_state, target_state, walle_deleted):
    id = steps.make_task(initial_state)
    steps.assert_that.fail_invalid_choice(is_walle_deleted=walle_deleted, initial_state=initial_state,
                                          **steps.make_transition(id, source_state, target_state))
    steps.verify()
