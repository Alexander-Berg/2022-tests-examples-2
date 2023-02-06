import metrika.admin.python.cms.lib.fsm.states as fsm_states
import metrika.admin.python.cms.test.lib.mock_cluster_api as mock_cluster_api


def test_default_decider(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "default-cluster", 'shard_id': "default-cluster-non-existent-environment", 'environment': "non-existent-environment"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )

    walle_id = steps.input.create_walle_task("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.MAKING_DECISION, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_too_old_task(steps):
    walle_id = steps.input.create_walle_task_in_past("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.MAKING_DECISION, fsm_states.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_reject_task_with_many_hosts(steps):
    walle_id = steps.input.create_walle_task("shady-host", "cloudy-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.MAKING_DECISION, fsm_states.States.WAIT_FOR_APPROVAL_REJECT)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_always_reject(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "test-cluster-always-reject", 'shard_id': "test-cluster-always-reject-unit-testing", 'environment': "unit-testing"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )

    walle_id = steps.input.create_walle_task("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.MAKING_DECISION, fsm_states.States.WAIT_FOR_APPROVAL_REJECT)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_always_ok(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "test-cluster-always-ok", 'shard_id': "test-cluster-always-ok-unit-testing", 'environment': "unit-testing"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )

    walle_id = steps.input.create_walle_task("shady-host")

    steps.output.wait_until_transition(walle_id, fsm_states.States.MAKING_DECISION, fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_always_inprogress(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "test-cluster-always-inprogress", 'shard_id': "test-cluster-always-inprogress-unit-testing", 'environment': "unit-testing"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )

    walle_id = steps.input.create_walle_task("shady-host")

    steps.output.wait_until_audit(walle_id, message="Unable to make decision. Will try later")

    steps.assert_that.task_is_not_processed(walle_id)


def test_walle_unexpectedly_deleted_task(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "test-cluster-always-ok", 'shard_id': "test-cluster-always-ok-unit-testing", 'environment': "unit-testing"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )

    walle_id = steps.input.create_walle_task_and_delete_before_handling("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)


def test_default_decider_temporary_unreachable_task_host_in_allowlist(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "default-cluster", 'shard_id': "default-cluster-non-existent-environment", 'environment': "non-existent-environment"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )
    steps.config.decider.temporary_unreachable_allowdict = {"default-cluster": ["non-existent-environment"]}

    walle_id = steps.input.create_walle_task("shady-host", action="temporary-unreachable")

    steps.output.wait_until_transition(walle_id, fsm_states.States.MAKING_DECISION, fsm_states.States.WAIT_FOR_APPROVAL_UNLOAD)
    steps.output.wait_until_audit(walle_id, message="Finish processing")
    steps.output.wait_until_queue_task_processed(walle_id)
    steps.assert_that.task_is_processed(walle_id)


def test_default_decider_temporary_unreachable_task_host_not_in_allowlist(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "default-cluster", 'shard_id': "default-cluster-non-existent-environment", 'environment': "non-existent-environment"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )
    steps.config.decider.temporary_unreachable_allowdict = {}

    walle_id = steps.input.create_walle_task("shady-host", action="temporary-unreachable")

    steps.output.wait_until_audit(walle_id, message="Unable to make decision. Will try later")
    steps.assert_that.task_is_not_processed(walle_id)
