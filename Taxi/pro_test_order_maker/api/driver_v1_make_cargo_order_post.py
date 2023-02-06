from typing import List

import generated.models.cargo_claims as cargo_claims_module

from pro_test_order_maker.generated.service.swagger import requests
from pro_test_order_maker.generated.service.swagger import responses
import pro_test_order_maker.generated.service.swagger.models.api as api_module
from pro_test_order_maker.generated.web import web_context


def to_route_point(
        point: api_module.V1Point,
        visit_order: int,
        point_type: str,
        fullname: str,
        phone: str,
        payment_on_delivery: bool = False,
) -> cargo_claims_module.CargoPointMP:
    return cargo_claims_module.CargoPointMP(
        point_id=point.point_id,
        visit_order=visit_order,
        type=point_type,
        address=cargo_claims_module.CargoPointAddress(
            fullname=point.street, coordinates=[point.lon, point.lat],
        ),
        contact=cargo_claims_module.ContactOnPoint(name=fullname, phone=phone),
        payment_on_delivery=None
        if not payment_on_delivery or type != 'destination'
        else cargo_claims_module.RequestPaymentOnDelivery(
            payment_method='card',
            customer=cargo_claims_module.RequestCustomerFiscalization(
                phone=phone,
            ),
        ),
        skip_confirmation=True,
    )


def to_item(
        item: api_module.V1Item, item_id: int, pickup_point_id: int,
) -> cargo_claims_module.CargoItemMP:
    return cargo_claims_module.CargoItemMP(
        cost_currency='RUB',
        cost_value=str(item.price),
        quantity=item.count,
        title=item.name,
        size=cargo_claims_module.CargoItemSizes(
            height=item.height, length=item.length, width=item.width,
        ),
        weight=item.weight,
        pickup_point=pickup_point_id,
        droppof_point=item.destination,
        fiscalization=cargo_claims_module.ItemFiscalization(
            article=f'Item{item_id}',
            vat_code_str='vat0',
            supplier_inn='762457411530',
            item_type='service',
        ),
    )


def build_client_requirements(
        request: requests.DriverV1MakeCargoOrderPost,
) -> cargo_claims_module.ClientRequirements:
    taxi_class = request.body.tariff
    taxi_classes = None
    cargo_type = None
    cargo_options = []

    if taxi_class == 'eda':
        taxi_class = 'eda'
    elif taxi_class == 'lavka':
        taxi_classes = ['lavka']
        taxi_class = 'express'
    elif taxi_class in ('lcv_s', 'lcv_m', 'lcv_l'):
        cargo_type = taxi_class
        taxi_class = 'cargo'

    if request.body.options is not None and 'only_car' in request.body.options:
        cargo_options.append('auto_courier')
    if request.body.options is not None and 'termobox' in request.body.options:
        cargo_options.append('thermobag')

    return cargo_claims_module.ClientRequirements(
        taxi_class=taxi_class,
        taxi_classes=taxi_classes,
        cargo_type=cargo_type,
        pro_courier=(
            request.body.options is not None and 'pro' in request.body.options
        ),
        cargo_options=cargo_options,
    )


def build_features(
        request: requests.DriverV1MakeCargoOrderPost,
) -> List[cargo_claims_module.ClaimFeature]:
    response = []

    if request.body.partial_delivery:
        response.append(
            cargo_claims_module.ClaimFeature(id='partial_delivery'),
        )

    return response


def build_request_body(
        request: requests.DriverV1MakeCargoOrderPost,
) -> cargo_claims_module.ClaimPropertiesMP:
    user_fullname = request.body.name or 'John Doe'
    user_phone = request.body.phone or '+70000000000'

    route_points = [
        to_route_point(
            point=x,
            visit_order=i,
            point_type='source' if i == 1 else 'destination',
            fullname=user_fullname,
            phone=user_phone if i != 2 else '+79099999999',
            payment_on_delivery=request.body.payment_on_delivery is not None
            and request.body.payment_on_delivery,
        )
        for i, x in enumerate(request.body.addresses, 1)
    ]
    if request.body.return_ is not None:
        route_points.append(
            to_route_point(
                point=request.body.return_,
                visit_order=len(request.body.addresses) + 1,
                point_type='return',
                fullname=user_fullname,
                phone=user_phone,
            ),
        )

    items = [
        to_item(
            item=x,
            item_id=i,
            pickup_point_id=request.body.addresses[0].point_id,
        )
        for i, x in enumerate(request.body.goods)
    ]

    claim_kind = None
    custom_context = None
    if request.body.tariff == 'eda':
        claim_kind = 'platform_usage'
        custom_context = {
            'brand_id': 151272,
            'brand_name': 'cargo-newflow claim',
            'delivery_flags': {
                'assign_rover': False,
                'is_forbidden_to_be_in_batch': False,
                'is_forbidden_to_be_in_taxi_batch': False,
                'is_forbidden_to_be_second_in_batch': False,
            },
            'place_id': 1873,
            'region_id': 1,
        }

    return cargo_claims_module.ClaimPropertiesMP(
        route_points=route_points,
        items=items,
        client_requirements=build_client_requirements(request),
        features=build_features(request),
        skip_door_to_door=not (
            request.body.options is not None
            and 'door_to_door' in request.body.options
        ),
        claim_kind=claim_kind,
        custom_context=custom_context,
    )


async def handle(
        request: requests.DriverV1MakeCargoOrderPost,
        context: web_context.Context,
) -> responses.DRIVER_V1_MAKE_CARGO_ORDER_POST_RESPONSES:
    result = await context.clients.cargo_claims.integration_v2_claims_create(
        accept_language='ru',
        request_id=request.x_idempotency_token,
        x_b2_b_client_id='b8cfabb9d01d48079e35655c253035a9',
        x_b2_b_client_storage='taxi',
        x_cargo_api_prefix='/api/b2b/cargo-claims/',
        x_yandex_login='lesf0',
        x_yandex_uid='123',
        x_remote_ip='127.0.0.1',
        body=build_request_body(request),
    )

    return responses.DriverV1MakeCargoOrderPost200(
        api_module.V1MakeCargoOrderResponse(result.body.id),
    )
