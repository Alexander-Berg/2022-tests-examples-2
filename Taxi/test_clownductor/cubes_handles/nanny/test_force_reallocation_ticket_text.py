import pytest

SUMMARY_TEMPLATE = 'Summary: {nanny_name}'

DESCRIPTION_TEMPLATE = (
    'Description: {nanny_name}, '
    '{branch_link}, {reallocation_coefficient}, '
    '{user}, {request_fields_diff}'
)

SUMMARY_RESULT = 'Summary: test_service_stable'

DESCRIPTION_RESULT = (
    'Description: test_service_stable, '
    '/services/1/edit/1/branches/2, '
    '1.6, '
    'karachevda, '
    'rootBandwidthGuaranteeMegabytesPerSec: 5 -> 8\n'
    'rootBandwidthLimitMegabytesPerSec: 10 -> 16\n'
    'rootFsQuotaMegabytes: 20480 -> 32768\n'
    'workDirQuotaMegabytes: 512 -> 820\n'
    'vcpuGuarantee: 900 -> 1440\n'
    'vcpuLimit: 1000 -> 1600\n'
    'networkBandwidthGuaranteeMegabytesPerSec: 1 -> 2\n'
    'networkBandwidthLimitMegabytesPerSec: 1 -> 2\n'
    '<{persistentVolumes\n'
    '/cores.diskQuotaMegabytes: 20480 -> 32768\n'
    '/cores.bandwidthGuaranteeMegabytesPerSec: 12 -> 20\n'
    '/cores.bandwidthLimitMegabytesPerSec: 30 -> 48\n'
    '}>'
)

TRANSLATIONS = {
    'tickets.nanny_force_reallocation_summary': {'ru': SUMMARY_TEMPLATE},
    'tickets.nanny_force_reallocation_description': {
        'ru': DESCRIPTION_TEMPLATE,
    },
}


@pytest.mark.parametrize(
    'summary_text, description_text',
    [
        pytest.param(
            'tickets.nanny_force_reallocation_summary',
            'tickets.nanny_force_reallocation_description',
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
        call_cube_handle,
        original_allocation_request,
        prepared_allocation_request,
        summary_text,
        description_text,
):
    await call_cube_handle(
        'NannyForceReallocationTicketText',
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
                    'nanny_name': 'test_service_stable',
                    'original_allocation_request': original_allocation_request,
                    'prepared_allocation_request': prepared_allocation_request,
                    'reallocation_coefficient': 1.6,
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
