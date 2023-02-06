import datetime
import typing

from taxi.util import dates

from promotions.generated.service.swagger import requests
from promotions.generated.service.swagger import responses
from promotions.generated.service.swagger.models import api as api_models
from promotions.generated.web import web_context
from promotions.logic import context as ctx
from promotions.logic import default_responses
from promotions.logic import exceptions as logic_exc
from promotions.logic.admin import actions
from promotions.models import promo
from promotions.repositories import exceptions as repo_exc
from promotions.repositories import storage


RESPONSE_NOT_FOUND = responses.AdminTestPublish400(
    data=api_models.ErrorResponse.deserialize(
        {'code': 'not_found', 'message': 'Коммуникация не найдена'},
    ),
)
RESPONSE_TEST_PUBLISH_DISABLED = responses.AdminTestPublish400(
    data=api_models.ErrorResponse.deserialize(
        {
            'code': 'test_publish_disabled',
            'message': 'Тестовая публикация отключена конфигом',
        },
    ),
)
RESPONSE_TAXI_EXP_REMOTE_ERROR = responses.AdminTestPublish400(
    data=default_responses.taxi_exp_remote_error(),
)
RESPONSE_ALREADY_PUBLISHED = responses.AdminTestPublish409(
    data=api_models.ErrorResponse.deserialize(
        {
            'code': 'already_published',
            'message': 'Коммуникация уже опубликована',
        },
    ),
)


def _create_response_taxi_exp_request_error(
        exception: logic_exc.TaxiExpRequestError,
):
    return responses.AdminTestPublish400(
        data=default_responses.taxi_exp_request_error(exception),
    )


def _make_publish_data(
        promotion_id: str,
        exp_name: str,
        minutes_delta: int,
        promotion_type: str,
) -> typing.Union[
    api_models.AdminPublishRequest, api_models.AdminPromoOnMapPublishRequest,
]:
    start_date = dates.utcnow()
    end_date = start_date + datetime.timedelta(minutes=minutes_delta)

    request_class: typing.Union[
        typing.Type[api_models.AdminPromoOnMapPublishRequest],
        typing.Type[api_models.AdminPublishRequest],
    ]
    if promotion_type == promo.Type.PROMO_ON_MAP.value:
        request_class = api_models.AdminPromoOnMapPublishRequest
    else:
        request_class = api_models.AdminPublishRequest

    return request_class(
        promotion_id=promotion_id,
        experiment=exp_name,
        start_date=dates.timestring(start_date),
        end_date=dates.timestring(end_date),
        ticket='',
    )


async def handle(
        request: requests.AdminTestPublish, context: web_context.Context,
) -> responses.ADMIN_TEST_PUBLISH_RESPONSES:
    context_storage = storage.from_context(context)

    try:
        promotion_type = await context_storage.promotions.type_by_id(
            request.body.promotion_id,
        )
        publish_data = _make_publish_data(
            request.body.promotion_id,
            context.config.PROMOTIONS_TEST_PUBLISH_EXP_NAME,
            context.config.PROMOTIONS_TEST_PUBLISH_TIME_RANGE_MINUTES,
            promotion_type,
        )
        handler_context = ctx.AdminTestPublishContext(
            promotion_id=request.body.promotion_id,
            promotion_type=promotion_type,
            phones=request.body.phones,
            yql_link=request.body.yql_link,
            taxi_exp=context.client_taxi_exp,
            config=context.config,
            storage=context_storage,
            publish_data=publish_data,
            log_extra=request.log_extra,
            stq=context.stq,
        )
        feeds_admin_args = {}
        if isinstance(publish_data, api_models.AdminPublishRequest):
            feeds_admin_args = {
                'request': requests.AdminPublish(
                    log_extra=request.log_extra,
                    middlewares=request.middlewares,
                    body=publish_data,
                ),
                'context': context,
            }
        data = await actions.make_test_publish(
            handler_context, feeds_admin_args,
        )
    except logic_exc.TestPublishDisabled:
        return RESPONSE_TEST_PUBLISH_DISABLED
    except logic_exc.TaxiExpRequestError as exception:
        return _create_response_taxi_exp_request_error(exception)
    except logic_exc.TaxiExpRemoteError:
        return RESPONSE_TAXI_EXP_REMOTE_ERROR
    except repo_exc.NotFound:
        return RESPONSE_NOT_FOUND
    except repo_exc.AlreadyPublished:
        return RESPONSE_ALREADY_PUBLISHED
    return responses.AdminTestPublish200(data=data)
