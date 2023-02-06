from .const_market import CREATE_ON_DEMAND, UPDATE_ONDEMAND_ORDER, CREATE_EXPRESS, DEFERRED_COURIER, UPDATE_ORDER, CALL_COURIER

def get_request_body_simple(base, **kwargs):
    for k, v in kwargs.items():
        base = base.replace('{' + k + '}', v)
    return base


def ds_create_ondemand_body(request_id, delivery_date):
    return get_request_body_simple(
        CREATE_ON_DEMAND,
        request_id=request_id,
        delivery_date=delivery_date
    )


def ds_update_ondemand_body(platform_request_id):
    return get_request_body_simple(
        UPDATE_ONDEMAND_ORDER,
        platform_request_id=platform_request_id
    )


def ds_create_express_body(request_id, delivery_date):
    return get_request_body_simple(
        CREATE_EXPRESS,
        request_id=request_id,
        delivery_date=delivery_date
    )


def ds_create_deferred_body(request_id, delivery_date):
    return get_request_body_simple(
        DEFERRED_COURIER,
        request_id=request_id,
        delivery_date=delivery_date
    )


def ds_update_body(platform_request_id):
    return get_request_body_simple(
        UPDATE_ORDER,
        platform_request_id=platform_request_id
    )


def ds_call_courier_body(platform_request_id):
    return get_request_body_simple(
        CALL_COURIER,
        platform_request_id=platform_request_id
    )
