import metrika.admin.python.cms.test.lib.mock_cluster_api as mock_cluster_api


def test_not_making_decision(steps):
    steps.input.setup_cluster_api(
        [
            mock_cluster_api.MockRecord(handle="/get", params={"fqdn": "shady-host"},
                                        response=[{'type': "test-cluster-always-inprogress", 'shard_id': "test-cluster-always-inprogress-unit-testing", 'environment': "unit-testing"}]),
            mock_cluster_api.MockRecord(handle="/list/fqdn", response=[])
        ]
    )

    walle_id = steps.input.create_walle_task_not_making_decision("shady-host")

    steps.output.wait_until_audit(walle_id, message="Finish processing", success=True)
    steps.output.wait_until_queue_task_processed(walle_id)

    steps.assert_that.task_is_processed(walle_id)
