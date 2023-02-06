from crm_admin import entity
from crm_admin import storage
from crm_admin.generated.service.swagger import models
from crm_admin.generated.service.swagger import requests
from crm_admin.generated.service.swagger import responses
from crm_admin.generated.web import web_context
from crm_admin.utils.validation import errors as validation_errors
from crm_admin.utils.validation import serializers


MAX_TEST_USERS = 5


async def handle(
        request: requests.UpdateTestUsers, context: web_context.Context,
) -> responses.UPDATE_TEST_USERS_RESPONSES:
    try:
        if len(request.body) > MAX_TEST_USERS:
            return await serializers.process_campaign_errors(
                context=context,
                campaign_id=request.id,
                response_class=responses.UpdateTestUsers400,
                user_login=None,
                validation_errors=[
                    validation_errors.TooManyTestUsers(
                        test_users_limit=MAX_TEST_USERS,
                    ),
                ],
            )

        campaign_storage = storage.DbCampaign(context)
        campaign = await campaign_storage.fetch(request.id)
        campaign.test_users = request.body

        await campaign_storage.update(campaign=campaign)
        return responses.UpdateTestUsers200()
    except entity.EntityNotFound as exc:
        return responses.UpdateTestUsers404(models.api.ErrorResponse(str(exc)))
