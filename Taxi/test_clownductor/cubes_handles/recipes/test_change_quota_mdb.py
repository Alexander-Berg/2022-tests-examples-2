import pytest

from testsuite.utils import matching


SSD_QUOTA = 96636764160
CPU_QUOTA = 4500
RAM_QUOTA = 9663676416
SERVICE_ID = 2
DEPARTMENTS = [
    {'department_id': 4171, 'role_id': 16},
    {'department_id': 9293, 'role_id': 1258},
]


def _assert_quotas(mock, value):
    assert mock.times_called == 2
    assert mock.next_call()['request'].json['maxValue'] == value
    assert mock.next_call()['request'].json['maxValue'] == 0


@pytest.fixture(name='assert_abc_mock')
def _assert_abc_mock(assert_mock_calls):
    def _wrapper(mock):
        return assert_mock_calls(mock, 'expected_abc_calls.json')

    return _wrapper


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_change_quota_mdb(
        load_yaml,
        task_processor,
        run_job_common,
        mdb_mockserver,
        dispenser_ram_quota,
        dispenser_cpu_quota,
        dispenser_ssd_quota,
        dispenser_get_quotas,
        get_job_from_internal,
        get_service,
        abc_mockserver,
        assert_abc_mock,
):
    abc_mock = abc_mockserver(services=['abc-old', 'abc-new'])
    mdb_mock = mdb_mockserver(slug='abc-new')

    recipe = task_processor.load_recipe(
        load_yaml('recipes/ChangeQuotaMDB.yaml')['data'],
    )
    task_processor.load_recipe(
        load_yaml('recipes/ChangeQuotaBranchMDB.yaml')['data'],
    )

    async def _check_second_job(task):
        if task.cube.name != 'MDBStartChangeQuotaBranches':
            return
        job_ids = task.payload['job_ids']
        assert job_ids == [1, 2]
        internal_jobs = [
            await get_job_from_internal(job_id) for job_id in job_ids
        ]
        for internal_job in internal_jobs:
            await run_job_common(internal_job)
            expected = {
                'db_type': 'pgaas',
                'destination_folder_id': 'abc-new',
                'operation_id': 'mdbq9ue8i0gdv0grghrj',
                'service_id': SERVICE_ID,
                'user': 'karachevda',
                'uuid_token': matching.uuid_string,
            }
            if internal_job.change_doc_id == 'ChangeQuotaBranchMDB_5':
                expected['branch_id'] = 5
                expected['cluster_id'] = 'stable_cluster_id'
            elif internal_job.change_doc_id == 'ChangeQuotaBranchMDB_4':
                expected['branch_id'] = 4
                expected['cluster_id'] = 'testing_cluster_id'
            else:
                raise ValueError(
                    f'Bad change doc id {internal_job.change_doc_id}',
                )

            assert internal_job.job_vars == expected

    job = await recipe.start_job(
        job_vars={
            'service_id': SERVICE_ID,
            'db_type': 'pgaas',
            'service_abc_old': 'abc-old',
            'service_abc_new': 'abc-new',
            'st_ticket': None,
            'project_id': 1,
            'user': 'karachevda',
            'end_comment_description': {'ru': 'Комментарий', 'en': 'Comment'},
            'abc_move_role_ids': [8, 16, 1258],
        },
        initiator='clownductor',
    )
    await run_job_common(job, _check_second_job)
    assert_abc_mock(abc_mock)
    assert mdb_mock.times_called == 7
    assert dispenser_get_quotas.times_called == 2
    _assert_quotas(dispenser_ssd_quota, SSD_QUOTA * 2)
    _assert_quotas(dispenser_cpu_quota, CPU_QUOTA * 2)
    _assert_quotas(dispenser_ram_quota, RAM_QUOTA * 2)
    service = await get_service(SERVICE_ID)
    assert service['direct_link'] == 'abc-new'
    assert service['abc_service'] == 'abc-new'

    assert job.job_vars == {
        'abc_move_role_ids': [8, 16, 1258],
        'cpu_quota': CPU_QUOTA * 2,
        'new_cpu_quota': CPU_QUOTA,
        'old_cpu_quota': CPU_QUOTA,
        'db_type': 'pgaas',
        'job_ids': [1, 2],
        'end_comment_description': {'en': 'Comment', 'ru': 'Комментарий'},
        'members_to_add': [
            {'login': 'isharov', 'role_id': 8},
            {'login': 'nikslim', 'role_id': 8},
        ],
        'new_cloud_id': 'abc-new',
        'new_folder_id': 'abc-new',
        'departments_to_add': DEPARTMENTS,
        'old_departments': DEPARTMENTS,
        'old_members': [
            {'login': 'isharov', 'role_id': 8},
            {'login': 'nikslim', 'role_id': 8},
            {
                'linked_department': (
                    'yandex_distproducts_browserdev_mobile_taxi_mnt'
                ),
                'login': 'eatroshkin',
                'role_id': 16,
            },
        ],
        'project_id': 1,
        'ram_quota': RAM_QUOTA * 2,
        'new_ram_quota': RAM_QUOTA,
        'old_ram_quota': RAM_QUOTA,
        'service_abc_new': 'abc-new',
        'service_abc_old': 'abc-old',
        'service_id': 2,
        'ssd_quota': SSD_QUOTA * 2,
        'new_ssd_quota': SSD_QUOTA,
        'old_ssd_quota': SSD_QUOTA,
        'st_ticket': None,
        'user': 'karachevda',
    }
