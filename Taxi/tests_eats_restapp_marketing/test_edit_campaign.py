import dataclasses
import datetime
import enum
from ntpath import join

from dateutil import parser
import pytest
import pytz

from testsuite.utils import matching

import pytest

from tests_eats_restapp_marketing import sql


class BudgetAllocation(str, enum.Enum):
    ALL_PERIOD = 'all_period'
    WEEKLY = 'weekly'


PASSPORT_ID = 1229582676


@dataclasses.dataclass
class Request:
    campaign_id: str
    averagecpm: float = 100
    spend_limit: float = 10000
    budget_allocation: BudgetAllocation = BudgetAllocation.WEEKLY
    start_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc,
    )
    finish_date: datetime.datetime = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=30)
    )

    def asdict(self) -> dict:
        return {
            'campaign_id': self.campaign_id,
            'averagecpm': self.averagecpm,
            'spend_limit': self.spend_limit,
            'budget_allocation': self.budget_allocation,
            'start_date': self.start_date.isoformat(),
            'finish_date': self.finish_date.isoformat(),
        }


def insert_tokens(pgsql, passport_id):
    cursor = pgsql.cursor()
    cursor.execute(
        """
INSERT INTO eats_tokens.tokens
(token_id,
 token,
 passport_id,
 created_at)
VALUES (default,
        'c30d0407030244eba8f66626cdf66bd23601abb2c450c0e16228dd5687c0c0010149f2b7877894be1642d80ea02f3372496ee5648d4979aca9bc76c1d94bb04c778cbae113511d',
        111111,
        '2020-11-25T18:25:43Z'),
       (default,
        'c30d0407030244eba8f66626cdf66bd23601abb2c450c0e16228dd5687c0c0010149f2b7877894be1642d80ea02f3372496ee5648d4979aca9bc76c1d94bb04c778cbae113511d',
        %s,
        '2020-11-25T18:25:43Z');
    """
        % passport_id,
    )


@pytest.fixture(name='cpm_edit_campaign')
def _cpm_edit_campaign(taxi_eats_restapp_marketing):
    """
    Фикстура для запросов в ручку
    `/4.0/restapp-front/marketing/v1/ad/cpm/edit_campaign`
    """

    url = '/4.0/restapp-front/marketing/v1/ad/cpm/edit_campaign'

    async def post(body: Request, partner_id: int = 1):
        headers = {
            'X-YaEda-PartnerId': str(partner_id),
            'Content-type': 'application/json',
            'Authorization': 'token',
            'X-Remote-IP': '127.0.0.1',
        }
        return await taxi_eats_restapp_marketing.post(
            url, headers=headers, json=body.asdict(),
        )

    return post


start_date = (
    parser.parse('2022-05-04T12:00:00+03:00').astimezone(pytz.UTC).isoformat()
)
finish_date = (
    parser.parse('2022-06-04T12:00:00+03:00').astimezone(pytz.UTC).isoformat()
)


def init_table(eats_restapp_marketing_db):
    campaign = sql.Campaign(
        id='1',
        status=sql.CampaignStatus.NOT_CREATED,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=PASSPORT_ID,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': start_date,
            'finish_date': finish_date,
        },
    )

    sql.insert_campaign(eats_restapp_marketing_db, campaign)
    campaign.id = '2'
    campaign.status = sql.CampaignStatus.ACTIVE
    sql.insert_campaign(eats_restapp_marketing_db, campaign)
    campaign.id = '3'
    campaign.status = sql.CampaignStatus.SUSPENDED
    sql.insert_campaign(eats_restapp_marketing_db, campaign)
    campaign.id = '4'
    campaign.status = sql.CampaignStatus.ENDED
    sql.insert_campaign(eats_restapp_marketing_db, campaign)
    campaign.id = '6'
    campaign.passport_id = 1
    sql.insert_campaign(eats_restapp_marketing_db, campaign)


@pytest.mark.parametrize(
    'cpm_request, status_code, expected_status,passport_id',
    [
        pytest.param(
            Request(campaign_id='1'),
            204,
            sql.CampaignStatus.NOT_CREATED,
            PASSPORT_ID,
            id='ok, not changed "not created"',
        ),
        pytest.param(
            Request(campaign_id='2'),
            204,
            sql.CampaignStatus.UPDATING,
            PASSPORT_ID,
            id='ok, changed "active"',
        ),
        pytest.param(
            Request(campaign_id='3'),
            204,
            sql.CampaignStatus.UPDATING,
            PASSPORT_ID,
            id='ok, changed "suspended"',
        ),
        pytest.param(
            Request(campaign_id='4'),
            400,
            sql.CampaignStatus.ENDED,
            PASSPORT_ID,
            id='bad request',
        ),
        pytest.param(
            Request(campaign_id='5'),
            404,
            sql.CampaignStatus.ACTIVE,
            PASSPORT_ID,
            id='no campaign',
        ),
        pytest.param(
            Request(campaign_id='6'),
            403,
            sql.CampaignStatus.ACTIVE,
            PASSPORT_ID,
            id='different passport_id',
        ),
        pytest.param(
            Request(
                campaign_id='2',
                averagecpm=2,
                spend_limit=100,
                budget_allocation=BudgetAllocation.WEEKLY,
                start_date=parser.parse('2022-05-04T12:00:00+03:00'),
                finish_date=parser.parse('2022-06-04T12:00:00+03:00'),
            ),
            204,
            sql.CampaignStatus.ACTIVE,
            PASSPORT_ID,
            id='same request, no change',
        ),
    ],
)
async def test_edit_campaign(
        cpm_edit_campaign,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        cpm_request,
        status_code,
        expected_status,
        pgsql,
        passport_id,
):
    insert_tokens(pgsql['eats_tokens'], passport_id)
    init_table(eats_restapp_marketing_db)
    campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    response = await cpm_edit_campaign(cpm_request)
    assert response.status_code == status_code

    if status_code == 204:
        campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
        result = list(
            filter(lambda x: x.id == cpm_request.campaign_id, campaigns),
        )
        assert len(result) == 1
        res_camp = result[0]
        assert res_camp.id == cpm_request.campaign_id
        assert res_camp.status == expected_status
        assert res_camp.campaign_type == sql.CampaignType.CPM_BANNER_CAMPAIGN
        assert res_camp.passport_id == PASSPORT_ID

        assert res_camp.parameters['averagecpm'] == cpm_request.averagecpm
        assert res_camp.parameters['spend_limit'] == cpm_request.spend_limit
        assert res_camp.parameters['strategy_type'] == 'kWbMaximumImpressions'


@pytest.mark.parametrize(
    'cpm_request', [pytest.param(Request(campaign_id='1'), id='403')],
)
async def test_forbidden_access(
        cpm_edit_campaign,
        eats_restapp_marketing_db,
        cpm_request,
        pgsql,
        mock_blackbox_400,
):

    insert_tokens(pgsql['eats_tokens'], PASSPORT_ID)
    init_table(eats_restapp_marketing_db)
    response = await cpm_edit_campaign(cpm_request, partner_id=11111)
    assert response.status_code == 403
