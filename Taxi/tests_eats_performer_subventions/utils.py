import datetime


def to_string(whatever):
    if whatever is None:
        return None
    if isinstance(whatever, datetime.datetime):
        return whatever.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return str(whatever)


def make_event(
        order_nr,
        order_event,
        event_time,
        created_at=None,
        order_type='native',
        delivery_type='native',
        shipping_type='delivery',
        eater_id='eater_id-1',
        eater_personal_phone_id='eater_personal_phone_id-1',
        promised_at='2022-03-03T19:30:00+03:00',
        application='web',
        place_id='1',
        payment_method='payment-method',
        **kwargs,
):
    if isinstance(event_time, datetime.datetime):
        event_time = to_string(event_time)
    if created_at is None:
        created_at = event_time
    event = {
        'order_nr': order_nr,
        'order_event': order_event,
        'order_type': order_type,
        'created_at': created_at,
        'delivery_type': delivery_type,
        'shipping_type': shipping_type,
        'eater_id': eater_id,
        'eater_personal_phone_id': eater_personal_phone_id,
        'promised_at': promised_at,
        'application': application,
        'place_id': place_id,
        'payment_method': payment_method,
        f'{order_event}_at': event_time,
    }
    for key, value in kwargs.items():
        if value is None:
            if key in event:
                del event[key]
        else:
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            event[key] = value
    return event


def parse_datetime(date_string: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(
            date_string, '%Y-%m-%dT%H:%M:%S.%f%z',
        )
    except ValueError:
        return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')
