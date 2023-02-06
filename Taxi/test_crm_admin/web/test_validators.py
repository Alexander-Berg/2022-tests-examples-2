import datetime
import typing

import pytest

from crm_admin import entity
from crm_admin.utils.validation import campaign_validators
from crm_admin.utils.validation import errors
from crm_admin.utils.validation import group_validators
from test_crm_admin.utils import blank_entities


def get_blank_campaign() -> entity.BatchCampaign:
    # better place for this func is in blank_entities.py
    # but it's not moved there in this commit due to PR conflicts mess
    result = entity.BatchCampaign(
        campaign_id=1,
        name='whatever',
        specification=None,
        entity_type='whatever',
        trend='whatever',
        kind=None,
        subkind=None,
        discount=False,
        state='whatever',
        owner_name='whatever',
        ticket=None,
        ticket_status=None,
        settings=None,
        extra_data=None,
        extra_data_path=None,
        creative=None,
        segment_id=None,
        test_users=['whatever'],
        global_control=False,
        com_politic=False,
        efficiency=False,
        tasks=[0, 1, 2],
        planned_start_date=None,
        created_at=datetime.datetime(2000, 1, 1),
        root_id=1,
        parent_id=None,
        child_id=None,
        version_state='ACTUAL',
        target_metrics=[],
    )
    return result


def _errors_to_dict(
        errs: typing.List[errors.ValidationErrorBase],
) -> typing.List[dict]:
    return [error.serialize_to_dict() for error in errs]


@pytest.mark.now('2020-1-10 00:00:00')
async def test_campaign_efficiency(web_context):
    date_before_now = datetime.datetime(year=2020, month=1, day=1)
    date_after_now = datetime.datetime(year=2020, month=1, day=20)
    campaign = get_blank_campaign()

    campaign.is_regular = False

    campaign.efficiency_start_time = date_before_now
    campaign.efficiency_stop_time = date_after_now
    assert not await campaign_validators.campaign_efficiency(
        campaign=campaign, context=web_context,
    )

    campaign.efficiency_start_time = date_after_now
    campaign.efficiency_stop_time = date_before_now
    errs = _errors_to_dict(
        await campaign_validators.campaign_efficiency(
            campaign=campaign, context=web_context,
        ),
    )
    assert errs == [
        {'code': errors.ValidationErrorCode.CAMPAIGN_EFFICIENCY_EXPIRED},
    ]

    campaign.is_regular = True

    campaign.efficiency_start_time = None
    campaign.efficiency_stop_time = None
    assert not await campaign_validators.campaign_efficiency(
        campaign=campaign, context=web_context,
    )

    campaign.efficiency_start_time = date_before_now
    campaign.efficiency_stop_time = date_after_now
    assert not await campaign_validators.campaign_efficiency(
        campaign=campaign, context=web_context,
    )

    campaign.efficiency_start_time = date_after_now
    campaign.efficiency_stop_time = date_before_now
    errs = _errors_to_dict(
        await campaign_validators.campaign_efficiency(
            campaign=campaign, context=web_context,
        ),
    )
    assert errs == []


@pytest.mark.now('2020-1-10 00:00:00')
async def test_campaign_period():
    date_before_now = datetime.datetime(year=2020, month=1, day=1)
    date_after_now = datetime.datetime(year=2020, month=1, day=20)
    campaign = get_blank_campaign()

    campaign.is_regular = False
    campaign.regular_start_time = None
    campaign.regular_stop_time = None
    assert not await campaign_validators.campaign_period(campaign)

    campaign.is_regular = True
    errs = _errors_to_dict(await campaign_validators.campaign_period(campaign))
    assert errs == [
        {
            'code': errors.ValidationErrorCode.MISSING_MANDATORY_PARAMETER,
            'details': {'field': 'regular_start_time'},
        },
        {
            'code': errors.ValidationErrorCode.MISSING_MANDATORY_PARAMETER,
            'details': {'field': 'regular_stop_time'},
        },
    ]

    campaign.regular_start_time = date_before_now
    campaign.regular_stop_time = date_after_now
    assert not await campaign_validators.campaign_period(campaign)


@pytest.mark.now('2020-1-10 00:00:00')
async def test_groups_efficiency(web_context):
    valid_efficiency_date = ['2020-1-1', '2020-1-20']
    valid_efficiency_time = ['00:00', '23:59']

    invalid_group_1 = blank_entities.get_blank_group()
    invalid_group_2 = blank_entities.get_blank_group()
    invalid_group_2.group_id = 2

    valid_group_1 = blank_entities.get_blank_group()
    valid_group_1.params.efficiency_date = valid_efficiency_date
    valid_group_1.params.efficiency_time = valid_efficiency_time
    valid_group_2 = blank_entities.get_blank_group()
    valid_group_2.params.efficiency_date = valid_efficiency_date
    valid_group_2.params.efficiency_time = valid_efficiency_time

    campaign = get_blank_campaign()

    campaign.efficiency = False

    assert not await group_validators.groups_efficiency(
        campaign=campaign,
        groups=[
            invalid_group_1,
            invalid_group_2,
            valid_group_1,
            valid_group_2,
        ],
        context=web_context,
    )

    campaign.efficiency = True

    assert not await group_validators.groups_efficiency(
        campaign=campaign,
        groups=[valid_group_1, valid_group_2],
        context=web_context,
    )

    errs = _errors_to_dict(
        await group_validators.groups_efficiency(
            campaign=campaign,
            groups=[
                invalid_group_1,
                invalid_group_2,
                valid_group_1,
                valid_group_2,
            ],
            context=web_context,
        ),
    )

    assert errs == [
        {
            'code': errors.ValidationErrorCode.MISSING_MANDATORY_PARAMETER,
            'details': {
                'field': 'efficiency_time',
                'entity_id': '1',
                'entity_type': 'group',
                'entity_name': 'name',
            },
        },
        {
            'code': errors.ValidationErrorCode.MISSING_MANDATORY_PARAMETER,
            'details': {
                'field': 'efficiency_date',
                'entity_id': '1',
                'entity_type': 'group',
                'entity_name': 'name',
            },
        },
        {
            'code': errors.ValidationErrorCode.MISSING_MANDATORY_PARAMETER,
            'details': {
                'field': 'efficiency_time',
                'entity_id': '2',
                'entity_type': 'group',
                'entity_name': 'name',
            },
        },
        {
            'code': errors.ValidationErrorCode.MISSING_MANDATORY_PARAMETER,
            'details': {
                'field': 'efficiency_date',
                'entity_id': '2',
                'entity_type': 'group',
                'entity_name': 'name',
            },
        },
    ]
