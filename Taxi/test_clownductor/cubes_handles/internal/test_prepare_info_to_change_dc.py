import typing

import pytest


class MockedData:
    def __init__(
            self,
            pre_man: int = 0,
            pre_sas: int = 0,
            pre_vla: int = 0,
            st_man: int = 0,
            st_sas: int = 0,
            st_vla: int = 0,
    ):
        self.pre_man = pre_man
        self.pre_sas = pre_sas
        self.pre_vla = pre_vla
        self.st_man = st_man
        self.st_sas = st_sas
        self.st_vla = st_vla

    def expected_payload(self) -> dict:
        active_regions = []
        if self.pre_sas:
            active_regions.append('sas')
        if self.pre_man:
            active_regions.append('man')
        if self.pre_vla:
            active_regions.append('vla')
        active_regions.sort()

        return {
            'pre_nanny_name': 'prestable_nanny_name',
            'pre_branch_id': 2,
            'pre_man_instances': self.pre_man,
            'pre_sas_instances': self.pre_sas,
            'pre_vla_instances': self.pre_vla,
            'pre_new_active_regions': active_regions,
            'stable_nanny_name': 'stable_nanny_name',
            'stable_branch_id': 1,
            'stable_man_instances': self.st_man,
            'stable_sas_instances': self.st_sas,
            'stable_vla_instances': self.st_vla,
        }


def nanny_yp_list_pods(mockserver, mock_data: MockedData):
    def make_pod(pod_id: str, state: str = 'ACTIVE'):
        return {
            'status': {
                'agent': {'iss': {'currentStates': [{'currentState': state}]}},
            },
            'meta': {'creationTime': '1628931000883990', 'id': pod_id},
        }

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        data = request.json
        cluster = data['cluster']
        nanny_name = data['serviceId']
        assert cluster in ['MAN', 'VLA', 'SAS']
        count_pods = 0

        if nanny_name.startswith('prestable'):
            if cluster == 'MAN':
                count_pods = mock_data.pre_man
            if cluster == 'SAS':
                count_pods = mock_data.pre_sas
            if cluster == 'VLA':
                count_pods = mock_data.pre_vla

        if nanny_name.startswith('stable'):
            if cluster == 'MAN':
                count_pods = mock_data.st_man
            if cluster == 'SAS':
                count_pods = mock_data.st_sas
            if cluster == 'VLA':
                count_pods = mock_data.st_vla
        pods = []
        for i in range(count_pods):
            pods.append(make_pod(f'{nanny_name}_pod_service_{i}'))
        return {'total': count_pods, 'pods': pods}

    return _handler


@pytest.mark.parametrize(
    'data_request, mocked_data, content_expected',
    [
        pytest.param(
            {
                'input_data': {'service_id': 1, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_man=2, st_sas=3, st_vla=3),
            {
                'payload': {
                    'pre_nanny_name': 'prestable_nanny_name',
                    'pre_branch_id': 2,
                    'pre_new_active_regions': ['sas'],
                    'stable_nanny_name': 'stable_nanny_name',
                    'stable_branch_id': 1,
                    'stable_new_active_regions': ['man', 'sas', 'vla'],
                    'stable_instances_by_region': {
                        'man': 3,
                        'sas': 2,
                        'vla': 3,
                    },
                    'pre_instances_by_region': {'sas': 1},
                },
                'status': 'success',
            },
            id='Stable 3*sas, 3*man, 2*vla',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 2, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_man=1, st_sas=2),
            {
                'payload': {
                    'pre_nanny_name': 'prestable_nanny_name_short',
                    'pre_branch_id': 5,
                    'pre_new_active_regions': ['sas'],
                    'stable_nanny_name': 'stable_nanny_name_short',
                    'stable_branch_id': 4,
                    'stable_new_active_regions': ['man', 'sas'],
                    'stable_instances_by_region': {'man': 2, 'sas': 1},
                    'pre_instances_by_region': {'sas': 1},
                },
                'status': 'success',
            },
            id='stable 1*man, 2*sas',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_sas=1),
            {
                'payload': {
                    'pre_nanny_name': 'prestable_nanny_name_single',
                    'pre_branch_id': 7,
                    'pre_new_active_regions': ['sas'],
                    'stable_nanny_name': 'stable_nanny_name_single',
                    'stable_branch_id': 6,
                    'stable_new_active_regions': ['man'],
                    'stable_instances_by_region': {'man': 1},
                    'pre_instances_by_region': {'sas': 1},
                },
                'status': 'success',
            },
            id='stable 1*sas',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_man=2, st_vla=3),
            {
                'payload': {
                    'pre_nanny_name': 'prestable_nanny_name_single',
                    'pre_branch_id': 7,
                    'pre_new_active_regions': ['vla'],
                    'stable_nanny_name': 'stable_nanny_name_single',
                    'stable_branch_id': 6,
                    'stable_new_active_regions': ['man', 'vla'],
                    'stable_instances_by_region': {'man': 3, 'vla': 2},
                    'pre_instances_by_region': {'vla': 1},
                },
                'status': 'success',
            },
            id='stable 2*man 3*vla',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_man=1, st_vla=2, st_sas=2),
            {
                'payload': {
                    'pre_nanny_name': 'prestable_nanny_name_single',
                    'pre_branch_id': 7,
                    'pre_new_active_regions': ['sas'],
                    'stable_nanny_name': 'stable_nanny_name_single',
                    'stable_branch_id': 6,
                    'stable_new_active_regions': ['man', 'sas', 'vla'],
                    'stable_instances_by_region': {
                        'man': 2,
                        'sas': 1,
                        'vla': 2,
                    },
                    'pre_instances_by_region': {'sas': 1},
                },
                'status': 'success',
            },
            id='stable 1*man 2*vla 2*sas',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_vla=1, st_sas=1),
            {
                'payload': {
                    'pre_nanny_name': 'prestable_nanny_name_single',
                    'pre_branch_id': 7,
                    'pre_new_active_regions': ['sas'],
                    'stable_nanny_name': 'stable_nanny_name_single',
                    'stable_branch_id': 6,
                    'stable_new_active_regions': ['man', 'vla'],
                    'stable_instances_by_region': {'man': 1, 'vla': 1},
                    'pre_instances_by_region': {'sas': 1},
                },
                'status': 'success',
            },
            id='stable 1*vla 1*sas',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, pre_sas=1, st_vla=1, st_sas=1),
            {
                'status': 'failed',
                'error_message': 'Prestable env hase more when one region',
            },
            id='prestable 1*man 1*sas',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=2, st_sas=2),
            {
                'payload': {
                    'pre_nanny_name': 'prestable_nanny_name_single',
                    'pre_branch_id': 7,
                    'pre_new_active_regions': ['sas'],
                    'stable_nanny_name': 'stable_nanny_name_single',
                    'stable_branch_id': 6,
                    'stable_new_active_regions': ['man'],
                    'stable_instances_by_region': {'man': 2},
                    'pre_instances_by_region': {'sas': 2},
                },
                'status': 'success',
            },
            id='prestable 2*man, stable: 2*sas',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_man=1),
            {
                'status': 'failed',
                'error_message': 'Identical stable and prestable regions',
            },
            id='prestable 1*man stable: 1*man',
        ),
        pytest.param(
            {
                'input_data': {'service_id': 3, 'pre_move_region': 'man'},
                'job_id': 44,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
            MockedData(pre_man=1, st_man=2, st_vla=3, st_sas=1),
            {'status': 'failed', 'error_message': 'Incorrect pods count'},
            id='check balance',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_prepare_info_to_change_dc(
        call_cube_handle,
        data_request,
        mocked_data,
        content_expected,
        patch,
        mockserver,
):
    nanny_yp_list_pods(mockserver, mocked_data)

    @patch(
        'clownductor.internal.tasks.cubes.internal.info.'
        'PrepareInfoToChangeDc.shuffle_regions',
    )
    def _shuffle_regions(regions: typing.List[str]):
        regions.sort()
        return regions

    await call_cube_handle(
        'PrepareInfoToChangeDc',
        {'data_request': data_request, 'content_expected': content_expected},
    )
