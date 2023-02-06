def has_shipping_type(response, shipping_type):
    available_shipping_types = response['payload']['foundPlace'][
        'locationParams'
    ]['availableShippingTypes']
    for entry in available_shipping_types:
        if entry['type'] == shipping_type:
            return True
    return False


def is_taxi_delivery(response) -> bool:
    is_taxi = response['payload']['foundPlace']['place']['features'][
        'delivery'
    ]['isYandexTaxi']
    return has_shipping_type(response, 'delivery') and is_taxi


def is_pedestrian_delivery(response) -> bool:
    is_taxi = response['payload']['foundPlace']['place']['features'][
        'delivery'
    ]['isYandexTaxi']
    return has_shipping_type(response, 'delivery') and not is_taxi


def is_pickup_available(response) -> bool:
    return has_shipping_type(response, 'pickup')


def is_available(response) -> bool:
    return (
        has_shipping_type(response, 'delivery')
        and response['payload']['foundPlace']['locationParams']['available']
    )
