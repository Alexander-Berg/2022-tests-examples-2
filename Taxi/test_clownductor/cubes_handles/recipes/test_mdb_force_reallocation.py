import pytest

from testsuite.utils import matching

SOURCE_CPU = 4500
NEW_CPU = 22500

SOURCE_RAM = 9663676416
NEW_RAM = 86973087744


@pytest.fixture(name='st_get_comments_value')
def _st_get_comments_value():
    def _wrapper(*args, **kwargs):
        return [
            {
                'id': 2,
                'self': 'url_to_comment',
                'createdBy': {'id': 'nikslim'},
                'createdAt': '2000-06-28T15:27:25.359+0000',
                'updatedAt': '2000-06-28T15:27:25.359+0000',
                'text': 'Rollback reallocation',
            },
        ]

    return _wrapper


def _assert_unit_change(mock, new, old, unit):
    assert mock.times_called == 2
    call = mock.next_call()['request']
    assert call.json == {'maxValue': new, 'unit': unit}
    call = mock.next_call()['request']
    assert call.json == {'maxValue': old, 'unit': unit}


@pytest.fixture(name='assert_mdb')
def _assert_mdb(assert_mock_calls):
    def _wrapper(mdb_mock):
        return assert_mock_calls(mdb_mock, 'expected_mdb_calls.json')

    return _wrapper


@pytest.mark.usefixtures(
    'st_get_myself',
    'st_create_comment',
    'st_create_ticket',
    'st_get_comments',
    'st_get_ticket',
    'st_execute_transaction',
    'dispenser_get_quotas',
    'abc_roles',
    'abc_members',
)
@pytest.mark.config(CLOWNDUCTOR_ABC_API_V4_USAGE={'get_members': 1})
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_mdb_force_reallocation(
        load_yaml,
        task_processor,
        run_job_common,
        mdb_mockserver,
        dispenser_ram_quota,
        dispenser_cpu_quota,
        assert_mdb,
):
    mdb_mock = mdb_mockserver()

    recipe = task_processor.load_recipe(
        load_yaml('recipes/MDBForceReallocation.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'cluster_id': 'mdbq9iqofu9vus91r2j9',
            'db_type': 'pgaas',
            'locale': 'ru',
            'abc_slug': 'some-abc',
            'flavor_change_level': 2,
            'user': 'karachevda',
            'branch_id': 2,
            'service_id': 1,
            'roles_ids_to_check': [1259, 1],
        },
        initiator='clownductor',
    )
    await run_job_common(job)

    _assert_unit_change(dispenser_ram_quota, NEW_RAM, SOURCE_RAM, 'BYTE')
    _assert_unit_change(
        dispenser_cpu_quota, NEW_CPU, SOURCE_CPU, 'PERMILLE_CORES',
    )
    assert_mdb(mdb_mock)

    assert job.job_vars == {
        'abc_slug': 'some-abc',
        'branch_id': 2,
        'cluster_id': 'mdbq9iqofu9vus91r2j9',
        'cluster_name': 'karachevda-test',
        'comment_props': {'summonees': ['karachevda']},
        'cpu_to_change': NEW_CPU,
        'db_type': 'pgaas',
        'end_comment': 'tickets.mdb_force_reallocation_end_comment',
        'flavor_change_level': 2,
        'flavor_to_change': 's2.medium',
        'folder_id': 'mdb-junk',
        'hosts_number': 3,
        'key_phrase': 'Rollback reallocation',
        'locale': 'ru',
        'new_ticket': 'TAXIADMIN-1',
        'quota_fields': {
            'cpu': {'new': NEW_CPU, 'old': SOURCE_CPU},
            'flavor': {'new': 's2.medium', 'old': 's2.micro'},
            'ram': {'new': NEW_RAM, 'old': SOURCE_RAM},
        },
        'ram_to_change': NEW_RAM,
        'roles_ids_to_check': [1259, 1],
        'rollback_comment': 'tickets.mdb_force_reallocation_rollback_comment',
        'service_id': 1,
        'shrink_operation_id': 'mdbq9ue8i0gdv0grghrj',
        'shrink_uuid_token': matching.uuid_string,
        'skip_cpu': False,
        'skip_ram': False,
        'source_cpu_quota': SOURCE_CPU,
        'source_flavor': 's2.micro',
        'source_ram_quota': SOURCE_RAM,
        'start_comment': 'tickets.mdb_force_reallocation_start_comment',
        'ticket_description': 'tickets.mdb_force_reallocation_description',
        'ticket_summary': 'tickets.mdb_force_reallocation_summary',
        'update_operation_id': 'mdbq9ue8i0gdv0grghrj',
        'update_uuid_token': matching.uuid_string,
        'user': 'karachevda',
    }
