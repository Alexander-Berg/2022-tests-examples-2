# pylint: disable=import-error, no-name-in-module
import json

import fbs.pin_storage.Pins as FbsPins


def build_pin(
        experiments,
        offer_id,
        order_id,
        personal_phone_id,
        longitude,
        latitude,
        longitude_b,
        latitude_b,
        user_id,
        layer,
        classes,
        created,
        use_point_a=False,
        driver_id=None,
        selected_class=None,
):
    result = {
        'created': created,
        'pin': {
            'experiments': experiments,
            'offer_id': offer_id,
            'order_id': order_id,
            'personal_phone_id': personal_phone_id,
            'point_b': [longitude_b, latitude_b],
            'trip': {'distance': 12.3, 'time': 45.6},
            'user_id': user_id,
            'user_layer': layer,
            'classes': classes,
        },
    }

    if use_point_a:
        result['pin']['point_a'] = [longitude, latitude]
    else:
        result['pin']['point'] = {'lat': latitude, 'lon': longitude}

    if selected_class is not None or classes:
        result['pin']['selected_class'] = selected_class or classes[0]['name']

    if driver_id is not None:
        result['pin']['driver_id'] = driver_id

    return json.dumps(result)


def parse_pins(data):
    response = FbsPins.Pins.GetRootAsPins(data, 0)
    pins = []
    for i in range(0, response.PinsLength()):
        pins.append(response.Pins(i))
    return pins
