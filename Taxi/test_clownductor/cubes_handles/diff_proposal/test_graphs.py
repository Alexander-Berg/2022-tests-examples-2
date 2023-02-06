import pytest


EXPECTED_CHANGES_DATA_CFG_GRAPHS_GRAFANA = (
    """
clownductor_config: taxi-devops:clownductor:stable
http_hosts:
  - test.tst
layout:
  - system
  - rps_share
  - http
""".lstrip()
)

EXPECTED_CHANGES_DATA_CFG_GRAPHS_DORBLU = (
    """
group:
  type: rtc
  name: taxi-devops_clownductor_stable

graphs:
  Monitoring:
    vhost-500:
      Blacklist:
        - Equals: { request_url: "/ping" }
  test.tst:
    Equals: { http_host: "test.tst" }
    Options:
      CustomHttp:
        - 401
        - 403
        - 406
        - 409
        - 410
        - 429
""".lstrip()
)


@pytest.mark.parametrize(
    'cube_name, input_data, expected_payload',
    [
        pytest.param(
            'GenerateDeleteGraphDiffProposal',
            {'branch_id': 2},
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'junk/robot-taxi-clown-tst/infra-cfg-graphs',
                    'base': 'trunk',
                    'title': (
                        'feat clownductor: delete '
                        'infra-cfg-graphs config template'
                    ),
                    'comment': (
                        'Relates: [TICKET-1]'
                        '(https://st.yandex-team.ru/TICKET-1)'
                    ),
                    'changes': [
                        {
                            'filepath': (
                                'grafana/nanny_taxi-'
                                'devops_clownductor_stable.yaml'
                            ),
                            'state': 'deleting',
                            'data': '',
                        },
                    ],
                },
                'new_service_ticket': 'TICKET-1',
            },
            id='delete_graph_from_arcadia_is_on',
        ),
        pytest.param(
            'GenerateDeleteGraphDiffProposal',
            {'branch_id': 2, 'awacs_namespace': 'test_awacs_namespace'},
            {
                'diff_proposal': {
                    'user': 'arcadia',
                    'repo': 'junk/robot-taxi-clown-tst/infra-cfg-graphs',
                    'base': 'trunk',
                    'title': (
                        'feat clownductor: delete '
                        'infra-cfg-graphs config template'
                    ),
                    'comment': (
                        'Relates: [TICKET-1]'
                        '(https://st.yandex-team.ru/TICKET-1)'
                    ),
                    'changes': [
                        {
                            'filepath': (
                                'grafana/nanny_taxi-'
                                'devops_clownductor_stable.yaml'
                            ),
                            'state': 'deleting',
                            'data': '',
                        },
                        {
                            'filepath': (
                                'dorblu/taxi-devops/nanny.taxi-'
                                'devops_clownductor_stable.yaml'
                            ),
                            'state': 'deleting',
                            'data': '',
                        },
                    ],
                },
                'new_service_ticket': 'TICKET-1',
            },
            id='delete_graph_from_arcadia_awacs_namespace',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init.sql'])
async def test_merge_graph_diff_proposal_with_pr(
        mock_task_processor,
        mock_clowny_balancer,
        call_cube_handle,
        cube_name,
        input_data,
        expected_payload,
):
    @mock_task_processor('/v1/jobs/start/')
    def _jobs_start_handler(_):
        return {'job_id': 1}

    @mock_clowny_balancer('/balancers/v1/service/get/')
    def _balancer_get(_):
        return {
            'namespaces': [
                {
                    'id': 1,
                    'awacs_namespace': 'test-fqdn',
                    'env': 'testing',
                    'abc_quota_source': 'abc_quota_source',
                    'is_external': False,
                    'is_shared': False,
                    'entry_points': [],
                },
            ],
        }

    expected_content = {'status': 'success'}
    if expected_payload is not None:
        expected_content['payload'] = expected_payload
    await call_cube_handle(
        cube_name,
        {
            'data_request': {
                'input_data': input_data,
                'status': 'in_progress',
                'task_id': 1,
                'job_id': 1,
                'retries': 0,
            },
            'content_expected': expected_content,
        },
    )
