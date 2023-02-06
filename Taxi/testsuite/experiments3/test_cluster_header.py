import pytest


TASK_ID_YES = 'orange_herring'
TASK_ID_NO = 'red_moose'


@pytest.mark.config(
    TVM_RULES=[
        {'experiments3': 'stq-agent'},
        {'experiments3': 'stq-agent-taxi-critical'},
    ],
)
@pytest.mark.experiments3(filename='exp_match.json')
def test_experiments3_cluster_header(
        taxi_experiments3, now, taxi_config, mockserver,
):
    queue_name = 'experiments3_test'
    percent = 50
    taxi_config.set(
        STQ_AGENT_CLUSTER_SETTINGS={
            'stq-agent': {
                'url': mockserver.url('/stq-agent'),
                'tvm_name': 'stq-agent',
            },
            'stq-agent-taxi-critical': {
                'url': mockserver.url('/stq-agent-taxi-critical'),
                'tvm_name': 'stq-agent-taxi-critical',
                'queues_in_process_of_cluster_switching': {
                    queue_name: {'percent': percent},
                },
            },
        },
    )

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/add/' + queue_name,
    )
    def _mock_add_critical(request):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/add/' + queue_name)
    def _mock_add_base(request):
        return mockserver.make_response(
            status=200,
            response={},
            headers={'X-Redirect-Queue-Cluster': 'stq-agent-taxi-critical'},
        )

    request = {'task_id': TASK_ID_YES}
    _request(taxi_experiments3, mockserver, request, {})
    _mock_add_base.wait_call()

    request = {'task_id': TASK_ID_YES}
    _request(taxi_experiments3, mockserver, request, {})
    _mock_add_critical.wait_call()

    request = {'task_id': TASK_ID_NO}
    _request(taxi_experiments3, mockserver, request, {})
    _mock_add_base.wait_call()

    @mockserver.json_handler(
        '/stq-agent-taxi-critical/queues/api/add/' + queue_name,
    )
    def _mock_add_critical(request):
        return mockserver.make_response(
            status=200,
            response={},
            headers={'X-Redirect-Queue-Cluster': 'stq-agent'},
        )

    @mockserver.json_handler('/stq-agent/queues/api/add/' + queue_name)
    def _mock_add_base(request):
        return {}

    request = {'task_id': TASK_ID_YES}
    _request(taxi_experiments3, mockserver, request, {})
    _mock_add_critical.wait_call()

    request = {'task_id': TASK_ID_YES}
    _request(taxi_experiments3, mockserver, request, {})
    _mock_add_base.wait_call()

    request = {'task_id': TASK_ID_NO}
    _request(taxi_experiments3, mockserver, request, {})
    _mock_add_base.wait_call()


def _request(taxi_experiments3, mockserver, data, headers):
    taxi_experiments3.post('v1/test', data, headers={})
