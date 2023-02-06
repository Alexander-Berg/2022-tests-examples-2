import datetime
from typing import Optional

from taxi_safety_center.generated.service.swagger.models import api

DEFAULT_CONFIDENCE = 30


def significant_contact(number: int):
    return {
        'phone_number': '+7987654321{}'.format(number),
        'name': 'Важный контакт {}'.format(number),
    }


def generated_accident(
        number: int, generate_id: bool = False,
) -> api.NewAccidentObject:
    accident_dict = generated_accident_dict(number, generate_id)
    return api.NewAccidentObject.deserialize(accident_dict)


def generated_accident_dict(
        number: int,
        generate_id: bool = False,
        generate_update_time: bool = False,
        datetime_format: str = 'str',
):
    result = {
        'idempotency_key': 'idempotency_key' + str(number),
        'order_alias_id': 'order_alias_id' + str(number),
        'confidence': DEFAULT_CONFIDENCE + number,
    }
    if generate_id:
        result['accident_id'] = 'accident-id-' + str(number)

    if datetime_format == 'str':
        timestamp = '2019-04-10T18:00:0' + str(number % 10) + '.0Z'
    elif datetime_format == 'datetime':
        timestamp = str(datetime.datetime(2019, 4, 10, 18, 0, number % 10, 0))
    else:
        raise AttributeError

    result['occurred_at'] = timestamp
    if generate_update_time:
        result['created_at'] = timestamp
        result['updated_at'] = timestamp
    return result


INSERT_ACCIDENT_QUERY = """
    INSERT INTO safety_center.accidents (
        accident_id,
        idempotency_key,
        order_id,
        order_alias_id,
        user_id,
        confidence,
        occurred_at,
        created_at,
        updated_at
    )
    VALUES (
        '{accident_id}'::text,
        '{idempotency_key}'::text,
        '{order_id}'::text,
        '{order_alias_id}'::text,
        '{user_id}'::text,
        {confidence}::integer,
        '{occurred_at}'::timestamptz,
        '{created_at}'::timestamptz,
        '{updated_at}'::timestamptz
    )
    ;"""


def insert_accident_query(number: int, confidence: Optional[int] = None):
    args = generated_accident_dict(
        number,
        generate_id=True,
        generate_update_time=True,
        datetime_format='datetime',
    )
    args['order_id'] = 'order_id' + str(number)
    args['user_id'] = 'user_id' + str(number)
    args['yandex_uid'] = 'yandex_uid' + str(number)
    if confidence is not None:
        args['confidence'] = confidence
    return INSERT_ACCIDENT_QUERY.format(**args)
