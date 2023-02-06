from crm_admin import entity
from crm_admin import settings
from crm_admin import storage
from crm_admin.generated.service.swagger import models
from crm_admin.generated.web import web_context as web


class CampaignUtils:
    @staticmethod
    async def create_campaign(
            web_context: web.Context, **kwargs,
    ) -> entity.BatchCampaign:
        db_campaign = storage.DbCampaign(web_context)

        data = models.api.CampaignInfo(
            name=kwargs.pop('name', 'name'),
            specification=kwargs.pop('specification', 'specification'),
            entity=kwargs.pop('entity', 'Driver'),
            trend=kwargs.pop('trend', 'trend'),
            kind=kwargs.pop('kind', 'other_kind'),
            discount=kwargs.pop('discount', False),
        )

        campaign = await db_campaign.create(data, 'pytest')
        campaign.segment_id = kwargs.pop('segment_id', None)
        campaign.ticket = kwargs.pop('ticket', None)
        campaign.ticket_status = kwargs.pop('ticket_status', None)
        campaign.state = kwargs.pop('state', settings.NEW_CAMPAIGN)
        campaign.is_regular = kwargs.pop('is_regular', False)
        campaign.is_active = kwargs.pop('is_active', None)

        campaign_settings = []
        newcomer = kwargs.pop('newcomer', None)
        if newcomer:
            campaign_settings.append(
                models.api.FilterFieldInfo(
                    field_id='newcomer', value=newcomer,
                ),
            )

        country = kwargs.pop('country', None)
        if country:
            if isinstance(country, str):
                country = [country]
            campaign_settings.append(
                models.api.FilterFieldInfo(field_id='country', value=country),
            )

        campaign.settings = campaign_settings or None

        await db_campaign.update(campaign)
        await db_campaign.update_state(campaign)

        return campaign

    @staticmethod
    async def fetch_campaign(
            web_context: web.Context, campaign_id: int,
    ) -> entity.BatchCampaign:
        db_campaign = storage.DbCampaign(web_context)
        return await db_campaign.fetch(campaign_id)
