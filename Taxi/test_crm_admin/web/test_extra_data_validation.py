# pylint: disable=protected-access
import pytest

from crm_admin.utils.validation import extra_data_validators
from test_crm_admin.utils import blank_entities
from test_crm_admin.web import test_validators


@pytest.mark.yt(static_table_data=['yt_extra_data_sample.yaml'])
async def test_table_exists_check(yt_apply, yt_client, web_context, patch):
    yt_client = web_context.yt_wrapper.hahn

    table_path = '//home/taxi-crm/robot-crm-admin/extra_data'
    val_errors = await extra_data_validators._validate_table_exists(
        yt_client=yt_client, yt_table_path=table_path,
    )

    assert not val_errors


@pytest.mark.yt(static_table_data=['yt_extra_data_sample.yaml'])
async def test_table_not_exists_check(yt_apply, yt_client, web_context, patch):
    yt_client = web_context.yt_wrapper.hahn
    non_existing_table_path = '//home/this/not/exists'
    val_errors = await extra_data_validators._validate_table_exists(
        yt_client=yt_client, yt_table_path=non_existing_table_path,
    )

    val_errors = [val_err.serialize_to_dict() for val_err in val_errors]
    assert val_errors == [
        {
            'code': 'extra_data_error',
            'details': {
                'reason': 'resource_not_exists',
                'entity_type': 'yt_table',
                'entity_id': non_existing_table_path,
            },
        },
    ]


@pytest.mark.yt(static_table_data=['yt_extra_data_sample.yaml'])
async def test_table_size_check(yt_apply, yt_client, web_context, patch):
    table_path = '//home/taxi-crm/robot-crm-admin/extra_data'

    yt_client = web_context.yt_wrapper.hahn

    val_errors = await extra_data_validators._validate_table_size(
        yt_client=yt_client, yt_table_path=table_path, max_size_bytes=1000000,
    )

    assert not val_errors


@pytest.mark.yt(static_table_data=['yt_extra_data_sample.yaml'])
async def test_table_size_check_fail(yt_apply, yt_client, web_context, patch):
    table_path = '//home/taxi-crm/robot-crm-admin/extra_data'

    yt_client = web_context.yt_wrapper.hahn

    val_errors = await extra_data_validators._validate_table_size(
        yt_client=yt_client, yt_table_path=table_path, max_size_bytes=10,
    )

    val_errors = [val_err.serialize_to_dict() for val_err in val_errors]
    assert val_errors == [
        {
            'code': 'extra_data_error',
            'details': {
                'entity_id': '//home/taxi-crm/robot-crm-admin/extra_data',
                'expected': 10,
                'got': 30,
                'reason': 'table_size_too_big',
            },
        },
    ]


@pytest.mark.yt(static_table_data=['yt_extra_data_sample.yaml'])
async def test_unicode_check(yt_apply, yt_client, web_context, patch):
    yt_client = web_context.yt_wrapper.hahn

    table_path = '//home/taxi-crm/robot-crm-admin/extra_data'
    val_errors = await extra_data_validators._validate_table_data_decodable(
        yt_client=yt_client, yt_table_path=table_path,
    )

    assert not val_errors
    # can't reasonably upload non-unicode test data, so no error case test here


@pytest.mark.yt(
    static_table_data=[
        'yt_extra_data_invalid_columns.yaml',
        'yt_segment_sample.yaml',
    ],
)
async def test_columns_check(yt_apply, yt_client, web_context, patch):
    yt_client = web_context.yt_wrapper.hahn

    table_path = '//home/taxi-crm/robot-crm-admin/extra_data_invalid'

    segment = blank_entities.get_blank_segment()
    segment.yt_table = 'home/taxi-crm/robot-crm-admin/segment_sample'

    val_errors = await extra_data_validators._validate_table_columns(
        yt_client=yt_client, yt_table_path=table_path, segment=segment,
    )

    val_errors = [val_err.serialize_to_dict() for val_err in val_errors]
    assert val_errors == [
        {
            'code': 'extra_data_error',
            'details': {
                'reason': 'unsupported_column_type',
                'entity_id': (
                    '//home/taxi-crm/' 'robot-crm-admin/extra_data_invalid'
                ),
                'entity_type': 'extra_data_table',
                'value': 'wrong_type',
                'got': 'any',
                'expected': ['string', 'int32', 'double'],
            },
        },
        {
            'code': 'extra_data_error',
            'details': {
                'reason': 'extra_data_column_already_in_segment',
                'value': 'control_flg',
                'entity_type': 'segment_table',
                'entity_id': '//home/taxi-crm/robot-crm-admin/segment_sample',
            },
        },
    ]


@pytest.mark.yt(
    static_table_data=[
        'yt_extra_data_invalid_columns.yaml',
        'yt_segment_sample.yaml',
    ],
)
async def test_columns_check_fail(yt_apply, yt_client, web_context, patch):
    yt_client = web_context.yt_wrapper.hahn

    table_path = '//home/taxi-crm/robot-crm-admin/extra_data_invalid'

    segment = blank_entities.get_blank_segment()
    segment.yt_table = 'home/taxi-crm/robot-crm-admin/segment_sample'

    val_errors = await extra_data_validators._validate_table_columns(
        yt_client=yt_client,
        yt_table_path=table_path,
        segment=segment,
        key_column='non_existing_column',
    )

    val_errors = [val_err.serialize_to_dict() for val_err in val_errors]
    assert val_errors == [
        {
            'code': 'extra_data_error',
            'details': {
                'reason': 'unsupported_column_type',
                'entity_id': (
                    '//home/taxi-crm/' 'robot-crm-admin/extra_data_invalid'
                ),
                'entity_type': 'extra_data_table',
                'value': 'wrong_type',
                'got': 'any',
                'expected': ['string', 'int32', 'double'],
            },
        },
        {
            'code': 'extra_data_error',
            'details': {
                'reason': 'extra_data_table_missing_key_column',
                'value': 'non_existing_column',
                'entity_type': 'extra_data_table',
                'entity_id': (
                    '//home/taxi-crm/robot-crm-admin' '/extra_data_invalid'
                ),
            },
        },
        {
            'code': 'extra_data_error',
            'details': {
                'reason': 'segment_table_missing_key_column',
                'value': 'non_existing_column',
                'entity_type': 'segment_table',
                'entity_id': '//home/taxi-crm/robot-crm-admin/segment_sample',
            },
        },
        {
            'code': 'extra_data_error',
            'details': {
                'reason': 'extra_data_column_already_in_segment',
                'value': 'city control_flg',
                'entity_type': 'segment_table',
                'entity_id': '//home/taxi-crm/robot-crm-admin/segment_sample',
            },
        },
    ]


@pytest.mark.yt(
    static_table_data=['yt_extra_data_sample.yaml', 'yt_segment_sample.yaml'],
)
async def test_personalization_params_check(
        yt_apply, yt_client, web_context, patch,
):
    yt_client = web_context.yt_wrapper.hahn

    campaign = test_validators.get_blank_campaign()
    campaign.entity_type = 'User'
    campaign.extra_data_path = '//home/taxi-crm/robot-crm-admin/extra_data'

    segment = blank_entities.get_blank_segment()
    segment.yt_table = 'home/taxi-crm/robot-crm-admin/segment_sample'

    valid_group = blank_entities.get_blank_group()
    valid_group.group_id = 1
    valid_group.params.channel = 'SMS'
    valid_group.params.content = '{city}{value}qwe'

    val_errors = await extra_data_validators.validate_personalization_params(
        context=web_context,
        yt_client=yt_client,
        campaign=campaign,
        segment=segment,
        groups=[valid_group],
    )

    assert not val_errors


@pytest.mark.yt(
    static_table_data=['yt_extra_data_sample.yaml', 'yt_segment_sample.yaml'],
)
async def test_personalization_params_check_fail(
        yt_apply, yt_client, web_context, patch,
):
    yt_client = web_context.yt_wrapper.hahn

    campaign = test_validators.get_blank_campaign()
    campaign.entity_type = 'User'
    campaign.extra_data_path = '//home/taxi-crm/robot-crm-admin/extra_data'

    segment = blank_entities.get_blank_segment()
    segment.yt_table = 'home/taxi-crm/robot-crm-admin/segment_sample'

    valid_group = blank_entities.get_blank_group()
    valid_group.group_id = 1
    valid_group.params.channel = 'SMS'
    valid_group.params.content = '{city}{value}qwe'

    invalid_group = blank_entities.get_blank_group()
    invalid_group.group_id = 2
    invalid_group.params.channel = 'PUSH'
    invalid_group.params.content = '{city} such {wow} much {fancy}'
    invalid_group.params.title = 'great {value} title {wat}'

    val_errors = await extra_data_validators.validate_personalization_params(
        context=web_context,
        yt_client=yt_client,
        campaign=campaign,
        segment=segment,
        groups=[valid_group, invalid_group],
    )

    val_errors = [val_err.serialize_to_dict() for val_err in val_errors]
    assert val_errors == [
        {
            'code': 'extra_data_error',
            'details': {
                'entity_id': '2',
                'entity_name': 'name',
                'entity_type': 'group',
                'reason': 'missing_personalization',
                'value': 'fancy wat wow',
            },
        },
    ]
