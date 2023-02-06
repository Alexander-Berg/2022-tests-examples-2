# pylint: disable=unused-variable

import pytest


@pytest.mark.yt(static_table_data=['yt_segment_sample.yaml'])
@pytest.mark.pgsql('crm_admin', files=['invalid_regular_campaign.sql'])
@pytest.mark.now('2020-1-10 00:00:00')
async def test_process_sending_validation(web_app_client):
    body = {'group_ids': [1], 'final': True}
    response = await web_app_client.post(
        '/v1/process/send', params={'id': 1}, json=body,
    )
    assert response.status == 400
    body = await response.json()
    assert body == {
        'errors': [{'code': 'campaign_efficiency_stop_time_expired'}],
    }


@pytest.mark.yt(static_table_data=['yt_segment_sample.yaml'])
@pytest.mark.pgsql('crm_admin', files=['invalid_regular_campaign.sql'])
@pytest.mark.now('2020-1-10 00:00:00')
async def test_regular_campaign_start_validation(web_app_client):
    body = {'group_ids': [1], 'final': True}
    response = await web_app_client.post(
        '/v1/regular-campaigns/start', params={'campaign_id': 2}, json=body,
    )
    assert response.status == 400
    body = await response.json()
    assert body == {
        'errors': [
            {
                'code': 'missing_mandatory_parameter',
                'details': {'field': 'regular_start_time'},
            },
        ],
    }


@pytest.mark.yt(
    static_table_data=['yt_extra_data_invalid.yaml', 'yt_segment_sample.yaml'],
)
@pytest.mark.pgsql('crm_admin', files=['extra_data_campaign.sql'])
@pytest.mark.now('2020-1-10 00:00:00')
@pytest.mark.config(CRM_ADMIN_SETTINGS={})
async def test_summon_approver_validation(
        yt_apply, yt_client, web_app_client, patch,
):
    @patch(
        'crm_admin.utils.validation'
        '.extra_data_validators._validate_table_permissions',
    )
    async def permissions_mock(*args, **kwargs):
        return []

    @patch(
        'crm_admin.utils.validation'
        '.extra_data_validators._validate_table_duplicate_keys',
    )
    async def duplicates_mock(*args, **kwargs):
        return []

    response = await web_app_client.post(
        '/v1/process/summon_approver', params={'id': 1},
    )
    assert response.status == 400

    body = await response.json()
    assert body == {
        'errors': [
            {'code': 'campaign_efficiency_stop_time_expired'},
            {
                'code': 'extra_data_error',
                'details': {
                    'value': 'wrong_type',
                    'entity_id': (
                        '//home/taxi-crm/' 'robot-crm-admin/extra_data_invalid'
                    ),
                    'entity_type': 'extra_data_table',
                    'expected': ['string', 'int32', 'double'],
                    'got': 'any',
                    'reason': 'unsupported_column_type',
                },
            },
            {
                'code': 'extra_data_error',
                'details': {
                    'entity_id': (
                        '//home/taxi-crm/robot-crm-admin/segment_sample'
                    ),
                    'entity_type': 'segment_table',
                    'reason': 'extra_data_column_already_in_segment',
                    'value': 'control_flg',
                },
            },
        ],
    }


@pytest.mark.yt(
    static_table_data=['yt_extra_data_invalid.yaml', 'yt_segment_sample.yaml'],
)
@pytest.mark.pgsql('crm_admin', files=['extra_data_campaign.sql'])
@pytest.mark.now('2020-1-10 00:00:00')
@pytest.mark.config(CRM_ADMIN_SETTINGS={})
async def test_update_extra_data_path_validation(
        yt_apply, yt_client, web_app_client, patch,
):
    @patch(
        'crm_admin.utils.validation'
        '.extra_data_validators._validate_table_permissions',
    )
    async def permissions_mock(*args, **kwargs):
        return []

    @patch(
        'crm_admin.utils.validation'
        '.extra_data_validators._validate_table_duplicate_keys',
    )
    async def duplicates_mock(*args, **kwargs):
        return []

    body = {'path': '//home/taxi-crm/robot-crm-admin/extra_data_invalid'}

    response = await web_app_client.post(
        '/v1/process/extra_data/path', params={'id': 1}, json=body,
    )
    assert response.status == 400

    body = await response.json()
    assert body == {
        'errors': [
            {
                'code': 'extra_data_error',
                'details': {
                    'value': 'wrong_type',
                    'entity_id': (
                        '//home/taxi-crm/' 'robot-crm-admin/extra_data_invalid'
                    ),
                    'entity_type': 'extra_data_table',
                    'expected': ['string', 'int32', 'double'],
                    'got': 'any',
                    'reason': 'unsupported_column_type',
                },
            },
            {
                'code': 'extra_data_error',
                'details': {
                    'entity_id': (
                        '//home/taxi-crm/robot-crm-admin/segment_sample'
                    ),
                    'entity_type': 'segment_table',
                    'reason': 'extra_data_column_already_in_segment',
                    'value': 'control_flg',
                },
            },
        ],
    }
