import json

import pytest

from taxi.util import dates

from crm_admin import entity
from crm_admin import storage
from test_crm_admin.utils import campaign_errors as cerrors_utils


@pytest.mark.now('2021-12-12 12:12:12')
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize('test_id', range(3))
async def test_create_error(web_context, load_json, test_id):
    test_data = load_json('correct_tests.json')
    params = test_data[test_id]

    campaign_errors_storage = storage.DbCampaignErrors(web_context)
    campaign_error_id = await campaign_errors_storage.create(
        campaign_id=params['campaign_id'],
        user_login=params.get('user_login'),
        error_code=params['error_code'],
        error_description=params['error_description'],
    )

    campaign_error = await cerrors_utils.CampaignErrors.get_raw_cerror_by_id(
        web_context, campaign_error_id,
    )

    error_description = json.loads(campaign_error['error_description'])
    assert campaign_error['id'] == campaign_error_id
    assert campaign_error['campaign_id'] == params['campaign_id']
    assert campaign_error['user_login'] == params.get('user_login')
    assert campaign_error['error_code'] == params['error_code']
    assert campaign_error['occurred_at'] == dates.utcnow()
    assert error_description == params['error_description']


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize('test_id', range(3))
async def test_create_incorrect_error(web_context, load_json, test_id):
    test_data = load_json('incorrect_tests.json')
    params = test_data[test_id]

    campaign_errors_storage = storage.DbCampaignErrors(web_context)
    with pytest.raises((entity.EntityNotFound, entity.InvalidDataFields)):
        await campaign_errors_storage.create(
            campaign_id=params['campaign_id'],
            user_login=params.get('user_login'),
            error_code=params['error_code'],
            error_description=params['error_description'],
        )


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.now('2021-12-12 12:12:12')
async def test_bulk_creation(web_context, load_json):
    test_data = load_json('correct_tests.json')
    test_data = [{**v, 'occurred_at': dates.utcnow()} for v in test_data]

    campaign_errors_storage = storage.DbCampaignErrors(web_context)
    ids = await campaign_errors_storage.bulk_creation(
        campaign_errors=test_data,
    )

    assert len(ids) == len(test_data)
    for campaign_error in test_data:
        db_error = await cerrors_utils.CampaignErrors.get_raw_cerror_by_id(
            web_context, campaign_error['id'],
        )

        error_description = json.loads(db_error['error_description'])
        assert db_error['id'] == campaign_error['id']
        assert db_error['campaign_id'] == campaign_error['campaign_id']
        assert db_error['user_login'] == campaign_error.get('user_login')
        assert db_error['error_code'] == campaign_error['error_code']
        assert db_error['occurred_at'] == dates.utcnow()
        assert error_description == campaign_error['error_description']


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_bulk_creation_incorrect_error(web_context, load_json):
    test_data = load_json('incorrect_tests.json')
    test_data = [{**v, 'occurred_at': dates.utcnow()} for v in test_data]

    campaign_errors_storage = storage.DbCampaignErrors(web_context)
    with pytest.raises((entity.EntityNotFound, entity.InvalidDataFields)):
        await campaign_errors_storage.bulk_creation(test_data)
