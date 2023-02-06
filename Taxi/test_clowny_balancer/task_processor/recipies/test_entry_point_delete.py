import pytest

from testsuite.utils import http


def _clean_nones(values: dict) -> dict:
    return {key: val for key, val in values.items() if val is not None}


class NotFound(Exception):
    pass


@pytest.fixture(name='awacs_mock')
def _awacs_mock(load_yaml, awacs_mock):
    return awacs_mock(load_yaml('awacs_data.yaml'))


class _L3MgrMock:
    _services = [{'vs': [{'ip': '2a02:6b8:0:3400:0:71d:0:4af'}], 'id': 1}]

    def __init__(self, mockserver):
        @mockserver.json_handler(
            r'^/l3mgr/service/(?P<srv_id>\d+)$', regex=True,
        )
        def _handler(_, srv_id):
            for srv in self._services:
                if str(srv['id']) == srv_id:
                    return srv
            return http.make_response(status=404)


@pytest.fixture(name='l3mgr_mock')
def _l3mgr_mock(mockserver):
    return _L3MgrMock(mockserver)


class _DNSMock:
    def __init__(self, mockserver, records):
        self._records = records

        @mockserver.json_handler('/dns_api/robot-taxi-clown/primitives')
        def _handler(request):
            ops = request.json['primitives']
            for _op in ops:
                if _op['operation'] == 'delete':
                    try:
                        self._remove(_op['name'], _op['data'], _op['type'])
                    except NotFound:
                        return http.make_response(status=404)
                else:
                    assert False, f'unsupported operation "{_op["operation"]}"'
            return {}

    def _find(self, left, right, type_):
        for record in self._records:
            if record == (left, right, type_):
                return record
        return None

    def _remove(self, left, right, type_):
        record = self._find(left, right, type_)
        if not record:
            raise NotFound()
        return {}


@pytest.fixture(name='dns_mock')
def _dns_mock(mockserver):
    return _DNSMock(
        mockserver, [('fqdn.net', '2a02:6b8:0:3400:0:71d:0:4af', 'AAAA')],
    )


@pytest.mark.usefixtures('l3mgr_mock', 'dns_mock', 'mock_clownductor_handlers')
@pytest.mark.parametrize('use_draft', [True, False])
@pytest.mark.parametrize(
    'request_data, non_deleted_counts',
    [({'id': 1}, {'certificate': 1, 'l3_balancer': 1, 'balancer': 1})],
)
async def test_recipe(
        load_yaml,
        task_processor,
        taxi_clowny_balancer_web,
        awacs_mock,
        use_draft,
        request_data,
        non_deleted_counts,
):
    task_processor.load_recipe(
        load_yaml('RemoveEntryPointWrapper.yaml')['data'],
    )
    task_processor.load_recipe(load_yaml('EntryPointRemove.yaml')['data'])

    if use_draft:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/delete/check/', json=request_data,
        )
        assert response.status == 200, await response.text()
        result = await response.json()
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/delete/apply/', json=result['data'],
        )
        assert response.status == 200, await response.text()
        result = await response.json()
        job_id = result['job_id']
    else:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/delete/', json=request_data,
        )
        assert response.status == 200, await response.text()
        result = await response.json()
        job_id = result['job_id']

    wrapper_job = task_processor.job(job_id)
    task, _ = await wrapper_job.step()
    while True:
        task, _ = await wrapper_job.step()
        if not task.status.is_success:
            break
    assert task.cube.name == 'MetaCubeWaitForJobCommon'

    job_id = wrapper_job.job_vars['remove_job_id']
    job = task_processor.job(job_id)

    while not job.status.is_terminated:
        task, _ = await job.step()
        assert task.status.is_success if task else job.status.is_success
    assert {
        'awacs_backend_ids': ['b-1', 'b-2'],
        'awacs_certificate_ids': ['c-1'],
        'awacs_deleting_certificate_ids': ['c-1'],
        'awacs_domain_ids': ['d-1'],
        'awacs_namespace_id': 'ns-1',
        'awacs_upstream_ids': ['default'],
        'balancer_man': '',
        'balancer_sas': 'b-1',
        'balancer_vla': '',
        'deleted_awacs_backend_ids': ['b-1', 'b-2'],
        'deleted_awacs_upstream_ids': ['default'],
        'deleted_namespace': 'ns-1',
        'dns_name': 'fqdn.net',
        'entry_point_id': 1,
        'entry_point_ids': [1],
        'ipv6': '2a02:6b8:0:3400:0:71d:0:4af',
        'l3mgr_service_id': '1',
        'lock_name': 'fqdn.net:default',
        'namespace_can_be_deleted': True,
        'upstream_ids': [1, 2],
    } == job.job_vars

    for model_name, models in awacs_mock.models.items():
        assert len(models) == non_deleted_counts.get(model_name, 0), model_name
