import asyncpg

from crm_admin.generated.web import web_context as web


class CampaignErrors:
    @staticmethod
    async def get_raw_cerror_by_id(
            web_context: web.Context, campaign_error_id: int,
    ) -> asyncpg.Record:
        query = (
            f'SELECT * '
            f'FROM crm_admin.campaign_errors '
            f'WHERE id = {campaign_error_id}'
        )

        async with web_context.pg.master_pool.acquire() as conn:
            return await conn.fetchrow(query)

    @staticmethod
    async def get_campaign_errors_number(web_context: web.Context) -> int:
        query = 'SELECT COUNT(id) FROM crm_admin.campaign_errors'
        async with web_context.pg.master_pool.acquire() as conn:
            return await conn.fetchval(query)
