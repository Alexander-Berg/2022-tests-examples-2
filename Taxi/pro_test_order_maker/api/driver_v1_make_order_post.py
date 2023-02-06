import logging
from typing import Any
from typing import Dict
from typing import List

from generated.clients import candidates
import taxi.clients.geocoder as geocoder_client

from pro_test_order_maker.generated.service.swagger import requests
from pro_test_order_maker.generated.service.swagger import responses
import pro_test_order_maker.generated.service.swagger.models.api as api_module
from pro_test_order_maker.generated.web import web_context

logger = logging.getLogger(__name__)

USER_AGENT = 'pro_test_order_maker'


class OrderMakerException(Exception):
    pass


async def get_addr(
        geocoder: geocoder_client.GeocoderClient, lat: float, lon: float,
) -> dict:
    geocoder_data = await geocoder.get_address_by_coordinates([lon, lat])

    locality = None
    for component in geocoder_data['Components']:
        if component['kind'] == 'locality':
            locality = component['name']
            break

    response = {
        'city': locality,
        'fullname': geocoder_data['formatted'],
        'geopoint': [lon, lat],
        'short_text': geocoder_data['formatted'],
        'type': 'address',
    }

    return response


async def _make_profile(
        int_client: Any,
        geocoder: geocoder_client.GeocoderClient,
        user_phone: str,
) -> dict:
    profile_response = await int_client.profile(  # type: ignore
        {'user': {'phone': user_phone}},
        headers={'Accept-Language': 'en', 'User-Agent': USER_AGENT},
    )
    logger.info(f'/profile => {profile_response.data}')

    if profile_response.status != 200:
        raise OrderMakerException(profile_response.data)

    return profile_response.data


async def _make_offer(
        int_client: Any,
        user_id: str,
        route: List[api_module.GeoPoint],
        category: str,
        requirements: Dict,
        phone_pd_id: str,
) -> dict:
    orderestimate_response = await int_client.order_estimate(  # type: ignore
        {
            'route': [[point.lon, point.lat] for point in route],
            'selected_class': category,
            'user': {'personal_phone_id': phone_pd_id, 'user_id': user_id},
            'requirements': requirements,
        },
        headers={'Accept-Language': 'en', 'User-Agent': USER_AGENT},
    )
    logger.info(f'/orderestimate_response => {orderestimate_response.data}')

    if orderestimate_response.status != 200:
        raise OrderMakerException(orderestimate_response.data)

    return orderestimate_response.data


async def _check_driver_can_get_order(
        candidates_client: candidates.CandidatesClient,
        category: str,
        park_id: str,
        driver_id: str,
        route: List[api_module.GeoPoint],
        forced_performer_settings: Any,
        blocking_reasons_explanations: Any,
):
    candidates_resp = await candidates_client.order_satisfy_post(
        {
            'allowed_classes': [category],
            'driver_ids': [{'dbid': park_id, 'uuid': driver_id}],
            'point': [route[0].lon, route[0].lat],
            'destination': [route[-1].lon, route[-1].lat],
        },
    )
    candidates_info = candidates_resp.body.get('candidates', [])
    logger.info(f'/order_satisfy_post => {candidates_info}')

    if len(candidates_info) != 1:
        raise OrderMakerException(f'Не смогли найти водителя в order-satisfy')

    if candidates_info[0].get('reasons', []):
        reasons = candidates_info[0].get('reasons', [])
        logger.info(f'reasons => {reasons}')
        logger.info(
            f'forced_performer_settings => {forced_performer_settings}',
        )
        whitelisted_filers = set(
            forced_performer_settings.get('pro-test-order-maker', {}).get(
                'whitelisted_filters', [],
            ),
        )

        logger.info(f'whitelisted_filers => {whitelisted_filers}')

        blocking_reasons = []
        for reason in reasons:
            if reason not in whitelisted_filers:
                blocking_reasons.append(reason)
        if blocking_reasons:
            human_readable_reasons = [
                '{}({})'.format(
                    reason,
                    blocking_reasons_explanations.get(
                        reason, 'У нас нет объяснения этому фильтру(',
                    ),
                )
                for reason in blocking_reasons
            ]
            logger.info(f'blocking_reasons => {blocking_reasons}')
            raise OrderMakerException(
                'Не получилось назначить заказ'
                'из-за блокирующих фильтров: {}'.format(
                    human_readable_reasons,
                ),
            )


async def _make_order_draft(
        int_client: Any,
        park_id: str,
        driver_id: str,
        user_id: str,
        prepared_route: List[Dict[Any, Any]],
        offer_id: str,
        category: str,
        requirements: Dict,
        phone_pd_id: str,
        extra_params: Dict,
) -> dict:

    orderdraft_response = await int_client.order_draft(  # type: ignore
        {
            'callcenter': {'personal_phone_id': phone_pd_id},
            'lookup_extra': {
                'intent': 'pro-test-order-maker',
                'performer_id': f'{park_id}_{driver_id}',
            },
            'dispatch_type': 'forced_performer',
            'class': [category],
            'comment': 'Order by ProTestOrderMaker',
            'requirements': requirements,
            'offer': offer_id,
            'id': user_id,
            'route': prepared_route,
            'parks': [],
            **extra_params,
        },
        headers={'Accept-Language': 'en', 'User-Agent': USER_AGENT},
    )

    logger.info(f'/orderdraft => {orderdraft_response.data}')

    if orderdraft_response.status != 200:
        raise OrderMakerException(
            f'Ошибка order_draft: {orderdraft_response.data}',
        )

    return orderdraft_response.data


async def _commit_order(int_client: Any, user_id: str, order_id: str):

    ordercommit_response = await int_client.order_commit(  # type: ignore
        {'userid': user_id, 'orderid': order_id},
        headers={'Accept-Language': 'en', 'User-Agent': USER_AGENT},
    )

    logger.info(f'/ordercommit => {ordercommit_response.data}')

    if ordercommit_response.status != 200:
        raise OrderMakerException(
            f'Ошибка order_commit: {ordercommit_response.data}',
        )


async def handle(
        request: requests.DriverV1MakeOrderPost, context: web_context.Context,
) -> responses.DRIVER_V1_MAKE_ORDER_POST_RESPONSES:
    context.orders_stats.total.inc()
    try:
        await _check_driver_can_get_order(
            context.clients.candidates,
            request.body.category,
            request.body.park_id,
            request.body.driver_id,
            request.body.route,
            context.config.LOOKUP_FORCED_PERFORMER_SETTINGS,
            context.config.PRO_TEST_ORDER_MAKER_BLOCKING_REASONS_EXPLANATIONS,
        )

        profile = await _make_profile(
            context.client_integration_api,
            context.client_geocoder,
            request.body.user_phone,
        )

        offer = await _make_offer(
            context.client_integration_api,
            profile['user_id'],
            request.body.route,
            request.body.category,
            request.body.requirements or {},
            profile['personal_phone_id'],
        )

        order = await _make_order_draft(
            context.client_integration_api,
            request.body.park_id,
            request.body.driver_id,
            profile['user_id'],
            [
                await get_addr(context.client_geocoder, point.lat, point.lon)
                for point in request.body.route
            ],
            offer['offer'],
            request.body.category,
            request.body.requirements or {},
            profile['personal_phone_id'],
            request.body.order_extra or {},
        )

        await _commit_order(
            context.client_integration_api,
            profile['user_id'],
            order['orderid'],
        )

    except OrderMakerException as err:
        context.orders_stats.failed.inc()
        logger.error(f'Не удалось создать заказ из-за: {str(err)}')
        return responses.DriverV1MakeOrderPost410(
            data=api_module.V1OrderStatusResponse(
                status='fail', message=str(err),
            ),
        )

    return responses.DriverV1MakeOrderPost200(
        data=api_module.V1MakeOrderResponse(order_id=order['orderid']),
    )
