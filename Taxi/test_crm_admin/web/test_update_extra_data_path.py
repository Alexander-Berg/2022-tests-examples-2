# pylint: disable=unused-variable

import pytest

from crm_admin import storage


@pytest.mark.pgsql('crm_admin', files=['extra_data.sql'])
async def test_extra_table_not_found(web_app_client, web_context):
    campaing_id = 1

    response = await web_app_client.post(
        f'/v1/process/extra_data/path?id={campaing_id}',
        json={'path': '//bad_extra_path'},
    )
    assert response.status == 400
    response_data = await response.json()
    assert response_data == {
        'errors': [
            {
                'code': 'extra_data_error',
                'details': {
                    'entity_id': '//bad_extra_path',
                    'entity_type': 'yt_table',
                    'reason': 'resource_not_exists',
                },
            },
        ],
    }


@pytest.mark.yt(static_table_data=['yt_table.yaml'])
async def test_campaign_not_exist(yt_apply, yt_client, web_app_client):
    response = await web_app_client.post(
        f'/v1/process/extra_data/path?id=-1',
        json={'path': '//extra_data/path'},
    )
    assert response.status == 404
    response_data = await response.json()
    assert response_data == {'message': 'Campaign -1 was not found'}


@pytest.mark.pgsql('crm_admin', files=['extra_data.sql'])
async def test_success_1(
        yt_apply, yt_client, web_app_client, web_context, patch,
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

    # with empty campaign.extra_data['params']
    campaing_id = 1
    response = await web_app_client.post(
        f'/v1/process/extra_data/path?id={campaing_id}',
        json={'path': '//extra_data/path'},
    )
    assert response.status == 200

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id=campaing_id)
    assert campaign.extra_data_path == '//extra_data/path'


@pytest.mark.pgsql('crm_admin', files=['extra_data.sql'])
async def test_success_2(
        yt_apply, yt_client, web_app_client, web_context, patch,
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

    # with filled extra_data['params']
    campaing_id = 2
    response = await web_app_client.post(
        f'/v1/process/extra_data/path?id={campaing_id}',
        json={'path': '//extra_data/path'},
    )
    assert response.status == 200

    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id=campaing_id)
    assert campaign.extra_data_path == '//extra_data/path'


@pytest.mark.parametrize(
    'campaign_id, key_column, path, status, message',
    [
        (3, 'key', '//extra_data/path', 200, None),
        (
            3,
            'foo',
            '//extra_data/path',
            400,
            {
                'errors': [
                    {
                        'code': 'extra_data_error',
                        'details': {
                            'entity_id': '//extra_data/path',
                            'entity_type': 'extra_data_table',
                            'reason': 'extra_data_table_missing_key_column',
                            'value': 'foo',
                        },
                    },
                    {
                        'code': 'extra_data_error',
                        'details': {
                            'entity_id': '//segment3_yt_table',
                            'entity_type': 'segment_table',
                            'reason': 'segment_table_missing_key_column',
                            'value': 'foo',
                        },
                    },
                    {
                        'code': 'extra_data_error',
                        'details': {
                            'entity_id': '//segment3_yt_table',
                            'entity_type': 'segment_table',
                            'reason': 'extra_data_column_already_in_segment',
                            'value': 'key',
                        },
                    },
                ],
            },
        ),
        (
            3,
            'key',
            '//extra_data/path_2',
            400,
            {
                'errors': [
                    {
                        'code': 'extra_data_error',
                        'details': {
                            'reason': 'unsupported_column_type',
                            'entity_id': '//extra_data/path_2',
                            'entity_type': 'extra_data_table',
                            'value': 'value',
                            'got': 'boolean',
                            'expected': ['string', 'int32', 'double'],
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['extra_data.sql'])
async def test_key_column(
        yt_apply,
        web_app_client,
        campaign_id,
        key_column,
        path,
        status,
        message,
        patch,
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
        f'/v1/process/extra_data/path?id={campaign_id}',
        json={'path': path, 'key_column': key_column},
    )
    assert response.status == status

    if message:
        assert await response.json() == message
