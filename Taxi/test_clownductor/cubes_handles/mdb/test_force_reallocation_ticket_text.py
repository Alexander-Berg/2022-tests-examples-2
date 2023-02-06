import pytest

SUMMARY_TEMPLATE = (
    'Экстренная реаллокация mdb {db_type} ' 'кластера: {cluster_name}'
)

DESCRIPTION_TEMPLATE = (
    'db_type: {db_type}, '
    'cluster_name: {cluster_name}, '
    'branch_link: {branch_link}, '
    'folder_id: {folder_id}, '
    'mdb_type: {mdb_type}, '
    'user: {user}, '
    'old_flavor: {old_flavor}, '
    'new_flavor: {new_flavor}, '
    'quota_change: {quota_change}'
)

SUMMARY_RESULT = 'Экстренная реаллокация mdb pgaas кластера: some-cluster'

DESCRIPTION_RESULT = (
    'db_type: pgaas, '
    'cluster_name: some-cluster, '
    'branch_link: /services/1/edit/1/branches/2, '
    'folder_id: some-folder-id, '
    'mdb_type: postgresql, '
    'user: karachevda, '
    'old_flavor: s2.micro, '
    'new_flavor: s2.large, '
    'quota_change: - ram: 12884901888 -> 13958643712\n- cpu: 1000 -> 2000'
)

TRANSLATIONS = {
    'tickets.mdb_force_reallocation_summary': {'ru': SUMMARY_TEMPLATE},
    'tickets.mdb_force_reallocation_description': {'ru': DESCRIPTION_TEMPLATE},
}


@pytest.mark.parametrize(
    'summary_text, description_text',
    [
        pytest.param(
            'tickets.mdb_force_reallocation_summary',
            'tickets.mdb_force_reallocation_description',
            id='without_translations',
        ),
        pytest.param(
            SUMMARY_RESULT,
            DESCRIPTION_RESULT,
            marks=pytest.mark.translations(clownductor=TRANSLATIONS),
            id='with_translations',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_force_reallocation_ticket_text(
        call_cube_handle, summary_text, description_text,
):
    await call_cube_handle(
        'MDBForceReallocationTicketText',
        {
            'content_expected': {
                'payload': {
                    'summary_text': summary_text,
                    'description_text': description_text,
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'cluster_name': 'some-cluster',
                    'db_type': 'pgaas',
                    'folder_id': 'some-folder-id',
                    'cluster_id': 'some-cluster-id',
                    'quota_fields': {
                        'flavor': {'old': 's2.micro', 'new': 's2.large'},
                        'cpu': {'old': 1000, 'new': 2000},
                        'ram': {'old': 12884901888, 'new': 13958643712},
                    },
                    'branch_id': 2,
                    'user': 'karachevda',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
