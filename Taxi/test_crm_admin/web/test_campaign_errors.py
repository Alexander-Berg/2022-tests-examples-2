# pylint: disable=unused-variable,
import asyncio
import json

import pytest

from taxi.util import dates

from crm_admin import error_codes
from crm_admin import settings
from crm_admin.generated.service.swagger import responses
from crm_admin.utils.state import state
from crm_admin.utils.validation import campaign_validators
from crm_admin.utils.validation import serializers
from test_crm_admin.utils import campaign as cutils
from test_crm_admin.utils import campaign_errors as cerrors_utils


@pytest.mark.now('2021-12-12 12:12:12')
@pytest.mark.parametrize(
    'new_state',
    (settings.SEGMENT_ERROR, settings.GROUPS_ERROR, settings.SENDING_ERROR),
)
async def test_create_error_on_change_status(web_context, patch, new_state):
    campaign = await cutils.CampaignUtils.create_campaign(web_context)

    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    await state.cstate_try_update_without_save(
        context=web_context,
        campaign=campaign,
        expected_states=[],
        new_state=new_state,
        error_code=error_codes.HUB_ERROR,
        error_description={'some': 'something'},
    )

    get_raw_cerror_by_id = cerrors_utils.CampaignErrors.get_raw_cerror_by_id
    raw_campaign_error = await get_raw_cerror_by_id(web_context, 1)
    assert raw_campaign_error['error_code'] == error_codes.HUB_ERROR
    assert raw_campaign_error['user_login'] is None
    assert raw_campaign_error['occurred_at'] == dates.utcnow()


@pytest.mark.now('2020-1-10 00:00:00')
async def test_create_error_on_validation(web_context):
    campaign = await cutils.CampaignUtils.create_campaign(web_context)
    user_login = 'test'

    validation_errors = await campaign_validators.campaign_efficiency(
        campaign=campaign, context=web_context,
    )
    await serializers.process_campaign_errors(
        context=web_context,
        campaign_id=campaign.campaign_id,
        user_login=user_login,
        response_class=responses.ProcessSending400,
        validation_errors=validation_errors,
    )

    cerrors_class = cerrors_utils.CampaignErrors
    raw_campaign_errors = await asyncio.gather(
        cerrors_class.get_raw_cerror_by_id(web_context, 1),
        cerrors_class.get_raw_cerror_by_id(web_context, 2),
    )

    expected_errors = list(
        map(lambda x: x.serialize_to_web(), validation_errors),
    )

    assert await cerrors_class.get_campaign_errors_number(web_context) == 2
    for index, raw_cerror in enumerate(raw_campaign_errors):
        error_description = json.loads(raw_cerror['error_description'])
        expected_error = expected_errors[index]

        assert raw_cerror['user_login'] == user_login
        assert raw_cerror['error_code'] == expected_error.code
        assert error_description == expected_error.details
