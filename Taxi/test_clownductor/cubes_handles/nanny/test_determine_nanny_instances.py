import pytest


@pytest.mark.parametrize(
    [
        'instances_count',
        'datacenters_count',
        'datacenters_regions',
        'update_request',
        'update_response',
    ],
    [
        (
            2,
            3,
            None,
            {},
            {'man_instances': 2, 'sas_instances': 2, 'vla_instances': 2},
        ),
        (
            3,
            3,
            None,
            {'man_pod_ids': ['a1', 'a2'], 'sas_pod_ids': ['b1', 'b2']},
            {'man_instances': 3, 'sas_instances': 3, 'vla_instances': 3},
        ),
        (2, 2, None, {}, {'man_instances': 2, 'vla_instances': 2}),
        (
            2,
            2,
            None,
            {'man_pod_ids': ['a1'], 'sas_pod_ids': ['b1']},
            {'man_instances': 2, 'sas_instances': 2},
        ),
        (
            2,
            2,
            None,
            {
                'man_pod_ids': ['a1'],
                'sas_pod_ids': ['b1'],
                'vla_pod_ids': ['c1'],
            },
            {'man_instances': 2, 'vla_instances': 2},
        ),
        (
            2,
            3,
            None,
            {'pre_man_pod_ids': ['a1'], 'man_pod_ids': ['a2']},
            {
                'pre_man_instances': 1,
                'man_instances': 1,
                'sas_instances': 2,
                'vla_instances': 2,
            },
        ),
        (
            1,
            3,
            None,
            {'pre_man_pod_ids': ['a1'], 'man_pod_ids': ['a2']},
            {
                'pre_man_instances': 1,
                'man_instances': 0,
                'sas_instances': 1,
                'vla_instances': 1,
            },
        ),
        (
            3,
            3,
            None,
            {
                'man_pod_ids': ['a1', 'a2'],
                'sas_pod_ids': ['b1', 'b2'],
                'pre_vla_pod_ids': ['c1'],
            },
            {
                'man_instances': 3,
                'sas_instances': 3,
                'vla_instances': 2,
                'pre_vla_instances': 1,
            },
        ),
        (
            2,
            2,
            None,
            {'pre_vla_pod_ids': ['c1']},
            {'man_instances': 2, 'vla_instances': 1, 'pre_vla_instances': 1},
        ),
        (
            1,
            2,
            None,
            {'man_pod_ids': ['a1'], 'pre_sas_pod_ids': ['b2']},
            {'man_instances': 1, 'sas_instances': 0, 'pre_sas_instances': 1},
        ),
        (
            3,
            2,
            None,
            {
                'man_pod_ids': ['a1'],
                'sas_pod_ids': ['b1'],
                'vla_pod_ids': ['c1'],
                'pre_vla_pod_ids': ['c1'],
            },
            {'vla_instances': 2, 'pre_vla_instances': 1, 'man_instances': 3},
        ),
        (
            None,
            None,
            None,
            {
                'man_pod_ids': ['a1', 'a2'],
                'sas_pod_ids': ['b1'],
                'vla_pod_ids': ['c1', 'c2', 'c3'],
                'pre_vla_pod_ids': ['c1'],
            },
            {
                'vla_instances': 3,
                'pre_vla_instances': 1,
                'sas_instances': 1,
                'man_instances': 2,
            },
        ),
        (
            2,
            None,
            None,
            {
                'man_pod_ids': ['a1', 'a2'],
                'sas_pod_ids': ['b1'],
                'vla_pod_ids': ['c1', 'c2', 'c3'],
                'pre_vla_pod_ids': ['c1'],
            },
            {
                'vla_instances': 1,
                'pre_vla_instances': 1,
                'sas_instances': 2,
                'man_instances': 2,
            },
        ),
        (
            None,
            2,
            None,
            {
                'man_pod_ids': ['a1', 'a2'],
                'vla_pod_ids': ['b1'],
                'sas_pod_ids': ['c1', 'c2', 'c3'],
                'pre_sas_pod_ids': ['c1'],
            },
            {'vla_instances': 1, 'pre_sas_instances': 1, 'sas_instances': 3},
        ),
        (
            None,
            3,
            None,
            {'man_pod_ids': ['a1'], 'pre_sas_pod_ids': ['c1']},
            {'vla_instances': 1, 'pre_sas_instances': 1, 'man_instances': 1},
        ),
        (
            5,
            2,
            ['vla', 'sas'],
            {
                'man_pod_ids': ['m1', 'm2', 'm3'],
                'vla_pod_ids': ['v1', 'v2', 'v3'],
                'sas_pod_ids': ['s2', 's3'],
                'pre_sas_pod_ids': ['s1'],
            },
            {
                'man_instances': 0,
                'vla_instances': 5,
                'sas_instances': 4,
                'pre_sas_instances': 1,
            },
        ),
        (
            None,
            None,
            None,
            {
                'man_pod_ids': ['m1', 'm2'],
                'sas_pod_ids': ['s2'],
                'vla_pod_ids': ['v1', 'v2'],
                'pre_sas_pod_ids': ['s1'],
            },
            {
                'vla_instances': 2,
                'man_instances': 2,
                'sas_instances': 1,
                'pre_sas_instances': 1,
            },
        ),
        pytest.param(
            4,
            2,
            ['vla', 'sas'],
            {
                'man_pod_ids': ['m1', 'm2', 'm3'],
                'sas_pod_ids': ['s2', 's3'],
                'pre_sas_pod_ids': ['s1'],
            },
            {
                'man_instances': 0,
                'vla_instances': 4,
                'sas_instances': 3,
                'pre_sas_instances': 1,
            },
            id='moving-out-from-man-to-vla',
        ),
        pytest.param(
            4,
            2,
            ['vla', 'sas'],
            {
                'pod_ids_by_region': {
                    'man': ['m1', 'm2', 'm3'],
                    'sas': ['s2', 's3'],
                },
                'pre_pod_ids_by_region': {'sas': ['s1']},
            },
            {
                'man_instances': 0,
                'vla_instances': 4,
                'sas_instances': 3,
                'pre_sas_instances': 1,
            },
            id='moving-out-from-man-to-vla-new',
        ),
        pytest.param(
            4,
            2,
            ['vla', 'man'],
            {
                'man_pod_ids': ['m1', 'm2', 'm3'],
                'sas_pod_ids': ['s2', 's3'],
                'pre_sas_pod_ids': ['s1'],
            },
            {
                'man_instances': 4,
                'vla_instances': 3,
                'sas_instances': 0,
                'pre_vla_instances': 1,
            },
            id='moving-out-from-sas-to-vla',
        ),
        pytest.param(
            3,
            2,
            ['vla', 'man'],
            {
                'man_pod_ids': ['m1', 'm2', 'm3'],
                'vla_pod_ids': ['v1', 'v2', 'v3'],
                'sas_pod_ids': ['s2', 's3'],
                'pre_sas_pod_ids': ['s1'],
            },
            {
                'man_instances': 3,
                'vla_instances': 2,
                'sas_instances': 0,
                'pre_vla_instances': 1,
            },
            id='moving-out-of-sas',
        ),
        pytest.param(
            3,
            3,
            ['vla', 'man', 'sas'],
            {
                'man_pod_ids': ['m1', 'm2', 'm3'],
                'vla_pod_ids': ['v2', 'v3'],
                'pre_vla_pod_ids': ['v1'],
            },
            {
                'man_instances': 3,
                'vla_instances': 2,
                'sas_instances': 3,
                'pre_vla_instances': 1,
            },
            id='moving-in-to-sas',
        ),
        pytest.param(
            1,
            2,
            ['vla', 'man'],
            {
                'man_pod_ids': ['m1', 'm2', 'm3'],
                'vla_pod_ids': ['v1', 'v2', 'v3'],
                'sas_pod_ids': ['s2', 's3'],
                'pre_sas_pod_ids': ['s1'],
            },
            {
                'man_instances': 1,
                'vla_instances': 0,
                'sas_instances': 0,
                'pre_vla_instances': 1,
            },
            id='moving-out-of-sas-single-pod',
        ),
        pytest.param(
            1,
            3,
            ['vla', 'man', 'sas'],
            {'man_pod_ids': ['m1'], 'pre_vla_pod_ids': ['v1']},
            {
                'man_instances': 1,
                'vla_instances': 0,
                'sas_instances': 1,
                'pre_vla_instances': 1,
            },
            id='moving-in-to-sas-single-pod',
        ),
        pytest.param(
            5,
            2,
            ['sas', 'man'],
            {'man_pod_ids': ['m1'], 'pre_sas_pod_ids': ['s1']},
            {'man_instances': 5, 'sas_instances': 4, 'pre_sas_instances': 1},
            id='massive-increase-of-instances-in-2-dc',
        ),
        pytest.param(
            5,
            3,
            ['vla', 'man', 'sas'],
            {'man_pod_ids': ['m1'], 'pre_vla_pod_ids': ['v1']},
            {
                'man_instances': 5,
                'vla_instances': 4,
                'sas_instances': 5,
                'pre_vla_instances': 1,
            },
            id='massive-increase-of-instances-and-adding-a-dc',
        ),
        pytest.param(
            5,
            2,
            ['man', 'sas'],
            {'man_pod_ids': ['m1'], 'pre_vla_pod_ids': ['v1']},
            {'man_instances': 5, 'sas_instances': 4, 'pre_sas_instances': 1},
            id='massive-increase-of-instances-and-moving-pre',
        ),
        pytest.param(
            3,
            None,
            None,
            {
                'man_pod_ids': [],
                'vla_pod_ids': ['v-1', 'v-2', 'v-3', 'v-4'],
                'sas_pod_ids': ['s-1', 's-2', 's-3', 's-4', 's-5'],
                'pre_man_pod_ids': [],
                'pre_vla_pod_ids': ['pre-v-1'],
                'pre_sas_pod_ids': [],
            },
            {
                'man_instances': 0,
                'sas_instances': 3,
                'vla_instances': 2,
                'pre_vla_instances': 1,
            },
            id='0-5-4_plus_pre_reallocate_to_3_inst_in_same_dc\'s',
        ),
        pytest.param(
            None,
            2,
            ['myt', 'vla'],
            {
                'service_name': 'service_name',
                'project_name': 'project_name',
                'man_pod_ids': [],
                'vla_pod_ids': [],
                'sas_pod_ids': ['sas-pod-1'],
                'pre_man_pod_ids': [],
                'pre_vla_pod_ids': ['pre-vla-1'],
                'pre_sas_pod_ids': [],
                'pod_ids_by_region': {
                    'vla': [],
                    'man': [],
                    'sas': ['sas-pod-1'],
                    'myt': [],
                    'iva': [],
                },
                'pre_pod_ids_by_region': {
                    'vla': ['pre-vla-1'],
                    'man': [],
                    'sas': [],
                    'myt': [],
                    'iva': [],
                },
            },
            {
                'man_instances': 0,
                'sas_instances': 0,
                'vla_instances': 0,
                'pre_vla_instances': 1,
                'pre_instances_by_region': {
                    'vla': 1,
                    'man': 0,
                    'sas': 0,
                    'myt': 0,
                    'iva': 0,
                },
                'instances_by_region': {
                    'vla': 0,
                    'man': 0,
                    'sas': 0,
                    'myt': 1,
                    'iva': 0,
                },
            },
            id='none-2-2-test-available-dc\'s',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
                        'projects': [
                            {
                                'datacenters': ['vla', 'sas'],
                                'name': '__default__',
                            },
                            {
                                'datacenters': ['vla', 'myt'],
                                'name': 'project_name',
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.features_on(
    'determine_new_regions', 'determine_amount_of_instances_new_flow',
)
async def test_determine_nanny_instances(
        nanny_mockserver,
        patch,
        nanny_yp_mockserver,
        instances_count,
        datacenters_regions,
        datacenters_count,
        update_request,
        update_response,
        call_cube_handle,
):
    nanny_yp_mockserver()

    request = {
        'man_pod_ids': None,
        'pre_man_pod_ids': None,
        'sas_pod_ids': None,
        'pre_sas_pod_ids': None,
        'vla_pod_ids': None,
        'pre_vla_pod_ids': None,
        'instances_count': instances_count,
        'datacenters_count': datacenters_count,
    }
    if datacenters_regions:
        request['datacenters_regions'] = datacenters_regions

    request.update(update_request)

    @patch('random.shuffle')
    def _shuffle(array):
        copy_array = array[:]
        array.clear()
        for elem in ['vla', 'man', 'sas', 'iva', 'myt']:
            if elem in copy_array:
                array.append(elem)
            if len(copy_array) == len(array):
                return

    instances_by_region = {'vla': 0, 'man': 0, 'sas': 0, 'myt': 0, 'iva': 0}
    pre_instances_by_region = instances_by_region.copy()
    response = {
        'pre_man_instances': 0,
        'pre_sas_instances': 0,
        'pre_vla_instances': 0,
        'man_instances': 0,
        'sas_instances': 0,
        'vla_instances': 0,
        'pre_instances_by_region': pre_instances_by_region,
        'instances_by_region': instances_by_region,
    }
    response.update(update_response)
    for region in ['man', 'vla', 'sas']:
        key = f'{region}_instances'
        pre_key = f'pre_{key}'
        if key in update_response:
            instances_by_region[region] = update_response[key]
        if pre_key in update_response:
            pre_instances_by_region[region] = update_response[pre_key]

    data = {
        'content_expected': {'payload': response, 'status': 'success'},
        'data_request': {
            'input_data': request,
            'job_id': 1,
            'retries': 0,
            'status': 'in_progress',
            'task_id': 1,
        },
    }
    await call_cube_handle('DetermineAmountOfInstances', data)
