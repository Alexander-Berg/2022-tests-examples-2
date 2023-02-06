import copy
import datetime
import re

from google.protobuf import json_format
from psycopg2 import extensions
from psycopg2 import extras
# pylint: disable=E0401, E0611
from routehistory.handlers import routehistory_get_pb2
from routehistory.handlers import routehistory_search_get_pb2
from routehistory.handlers import routehistory_shuttle_order_pb2
from routehistory.internal.db import drive_db_pb2
from routehistory.internal.db import grocery_db_pb2
from routehistory.internal.db import phone_history_db_pb2
from routehistory.internal.db import search_db_pb2
from routehistory.internal.db import shuttle_db_pb2

POINT_NAMES = {'position', 'adjusted_source', 'point', 'completion_point'}

PROTO_TYPES = {
    'PhoneHistoryOrderData': phone_history_db_pb2.PhoneHistoryOrderData,
    'SearchData': search_db_pb2.SearchData,
}


# Convert data retrieved from DB to a convenient form
def convert_pg_result(x):
    # pylint: disable=unidiomatic-typecheck
    # pylint: disable=invalid-name

    # If it is a plain tuple
    if type(x) is tuple:
        # For one-element tuple just unwrap it:
        if len(x) == 1:
            return convert_pg_result(x[0])
        # Otherwise process each element and return a tuple
        result = []
        for v in x:
            result.append(convert_pg_result(v))
        return tuple(result)
    # If it is a named tuple:
    if isinstance(x, tuple):
        # Recursively convert to a dict
        result = {}
        for k, v in zip(x._fields, x):
            # Hack for points such as '(37.5,55.1)'
            if k in POINT_NAMES and isinstance(v, str):
                match = re.match(r'^\((\d+(?:\.\d*)?)\,(\d+(?:\.\d*)?)\)$', v)
                if match:
                    result[k] = [float(match[1]), float(match[2])]
                    continue
            if v is not None:
                result[k] = convert_pg_result(v)
        return result
    # If it is an array
    if isinstance(x, list):
        # Recursively convert its items
        result = []
        for v in x:
            result.append(convert_pg_result(v))
        return result
    # If it is a timestamp
    if isinstance(x, datetime.datetime):
        # Remove time zone
        return (x - x.utcoffset()).replace(tzinfo=None)
    # Otherwise return as is
    return x


def register_user_types(cursor):
    extras.register_composite('routehistory.rerouting', cursor)
    extras.register_composite('routehistory.drive_history', cursor)
    extras.register_composite('routehistory.common_strings', cursor)
    extras.register_composite('routehistory.search_history', cursor)


def register_user_types_ph(cursor):
    extras.register_composite('routehistory_ph.users', cursor)
    extras.register_composite('routehistory_ph.phone_history2', cursor)


def fill_db_table(cursor, table, values):
    caster = extras.register_composite(table, cursor)
    tuples = []
    for value in values:
        value_tuple = []
        for name in caster.attnames:
            pg_value = value.get(name, None)
            if isinstance(pg_value, dict) and '$proto' in pg_value:
                message_type = PROTO_TYPES[pg_value['$proto']]
                message = message_type()
                pg_value_shallow_copy = copy.copy(pg_value)
                del pg_value_shallow_copy['$proto']
                json_format.ParseDict(pg_value_shallow_copy, message)
                pg_value = message.SerializeToString(deterministic=True)
            value_tuple.append(pg_value)
        tuples.append(tuple(value_tuple))
    cursor.execute(
        'INSERT INTO %(table)s SELECT (__inner.__val).* FROM ('
        'SELECT UNNEST(%(tuples)s::%(table)s[]) "__val") "__inner"',
        {'tuples': tuples, 'table': extensions.AsIs(table)},
    )


def fill_db(cursor, tables):
    for table, values in tables.items():
        fill_db_table(cursor, table, values)


def read_phone_history_db(cursor, cursor_ph):
    register_user_types(cursor)
    register_user_types_ph(cursor_ph)

    # pylint: disable=attribute-defined-outside-init
    class Records:
        pass

    records = Records()

    cursor_ph.execute(
        'SELECT c FROM routehistory_ph.phone_history2 c ORDER BY order_id',
    )
    records.phone_history = convert_pg_result(cursor_ph.fetchall())
    decode_ph_orders(records.phone_history)

    cursor.execute(
        'SELECT c FROM routehistory.common_strings c ' 'ORDER BY id',
    )
    records.strings = convert_pg_result(cursor.fetchall())

    cursor_ph.execute(
        'SELECT c FROM routehistory_ph.users c '
        'ORDER BY yandex_uid, phone_id',
    )
    records.users = convert_pg_result(cursor_ph.fetchall())

    return records


def decode_drive_order(order):
    data = drive_db_pb2.DriveOrderData()
    data.ParseFromString(order['data'])
    order['data'] = json_format.MessageToDict(data)


def decode_drive_orders(orders):
    for order in orders:
        decode_drive_order(order)


def decode_pb_grocery_order_data(order_data):
    data = grocery_db_pb2.GroceryOrderData()
    data.ParseFromString(order_data)
    return json_format.MessageToDict(data)


def decode_pb_shuttle_order_data(order_data):
    data = shuttle_db_pb2.ShuttleOrderData()
    data.ParseFromString(order_data)
    return json_format.MessageToDict(data)


def _parse_orders(single_order_parser, orders):
    orders_by_id = dict()
    for order in orders:
        parsed_order = single_order_parser(order)
        order_id = parsed_order['orderId']
        assert order_id not in orders_by_id  # bad test: duplicate order_id
        orders_by_id[order_id] = parsed_order
    return orders_by_id


def parse_grocery_stq_orders(orders):
    def parse_single_order(order):
        created = datetime.datetime.strptime(
            order['created'], '%Y-%m-%dT%H:%M:%S+%f',
        )
        return {
            k: v
            for k, v in {
                'orderId': order['order_id'],
                'yandex_uid': int(order['yandex_uid']),
                'created': created,
                'uri': order['place_uri'],
                'position': {
                    'lon': order['position'][0],
                    'lat': order['position'][1],
                },
                'entrance': order['entrance'],
                'floorNumber': order['floor'],
                'quartersNumber': order['flat'],
                'doorphoneNumber': order['doorcode'],
                'commentCourier': order['comment'],
                'buildingName': order.get('building_name'),
                'doorbellName': order.get('doorbell_name'),
                'doorcodeExtra': order.get('doorcode_extra'),
                'leftAtDoor': order.get('left_at_door'),
                'meetOutside': order.get('meet_outside'),
                'noDoorCall': order.get('no_door_call'),
            }.items()
            if v is not None
        }

    return _parse_orders(parse_single_order, orders)


def parse_grocery_db_orders(orders):
    def parse_single_order(order):
        parsed_order = decode_pb_grocery_order_data(order[2])
        parsed_order['yandex_uid'] = order[0]
        parsed_order['created'] = order[1]
        return parsed_order

    return _parse_orders(parse_single_order, orders)


def parse_grocery_response_orders(response):
    def parse_single_order(order):
        created = datetime.datetime.strptime(
            order['created'], '%Y-%m-%dT%H:%M:%S+%f',
        )
        return {
            k: v
            for k, v in {
                'orderId': order['order_id'],
                'yandex_uid': int(order['yandex_uid']),
                'created': created,
                'uri': order['uri'],
                'position': {
                    'lon': order['position'][0],
                    'lat': order['position'][1],
                },
                'entrance': order['entrance'],
                'floorNumber': order['floor_number'],
                'quartersNumber': order['quarters_number'],
                'doorphoneNumber': order['doorphone_number'],
                'commentCourier': order['comment_courier'],
                'buildingName': order.get('building_name'),
                'doorbellName': order.get('doorbell_name'),
                'doorcodeExtra': order.get('doorcode_extra'),
                'leftAtDoor': order.get('left_at_door'),
                'meetOutside': order.get('meet_outside'),
                'noDoorCall': order.get('no_door_call'),
            }.items()
            if v is not None
        }

    return _parse_orders(parse_single_order, response.json()['results'])


def parse_shuttle_response_orders(response):
    resp_json = rh_shuttle_get_response_proto_to_json(response)
    print(resp_json)

    def parse_single_order(order):
        created = datetime.datetime.strptime(
            order['created'], '%Y-%m-%dT%H:%M:%SZ',
        )
        return {
            'orderId': order['orderId'],
            'created': created,
            'yandex_uid': order['yandexUid'],
            'source': order['source'],
            'destination': order['destination'],
        }

    return _parse_orders(parse_single_order, resp_json.get('result', []))


def parse_shuttle_stq_orders(orders):
    def parse_single_order(order):
        created = datetime.datetime.strptime(
            order['created'], '%Y-%m-%dT%H:%M:%S+%f',
        )
        return {
            'orderId': order['order_id'],
            'created': created,
            'yandex_uid': order['yandex_uid'],
            'source': {
                'text': order['source']['text'],
                'uri': order['source']['uri'],
                'position': {
                    'lon': order['source']['position'][0],
                    'lat': order['source']['position'][1],
                },
            },
            'destination': {
                'text': order['destination']['text'],
                'uri': order['destination']['uri'],
                'position': {
                    'lon': order['destination']['position'][0],
                    'lat': order['destination']['position'][1],
                },
            },
        }

    return _parse_orders(parse_single_order, orders)


def parse_shuttle_db_orders(orders):
    def parse_single_order(order):
        parsed_order = decode_pb_shuttle_order_data(order[2])
        parsed_order['yandex_uid'] = str(order[0])
        parsed_order['created'] = order[1]
        return parsed_order

    return _parse_orders(parse_single_order, orders)


def decode_ph_order(order):
    data = phone_history_db_pb2.PhoneHistoryOrderData()
    data.ParseFromString(order['data'])
    order['data'] = json_format.MessageToDict(data)


def decode_ph_orders(orders):
    for order in orders:
        decode_ph_order(order)


def decode_search(search):
    data = search_db_pb2.SearchData()
    data.ParseFromString(search['data'])
    search['data'] = json_format.MessageToDict(data)


def decode_searches(searches):
    for search in searches:
        decode_search(search)


def rh_get_response_json_to_proto(js_dict):
    msg = routehistory_get_pb2.RouteHistoryGetResponse()
    json_format.ParseDict(js_dict, msg)
    return msg.SerializeToString(deterministic=True)


def rh_get_response_proto_to_json(binary):
    msg = routehistory_get_pb2.RouteHistoryGetResponse()
    msg.ParseFromString(binary)
    return json_format.MessageToDict(msg)


# pylint: disable=invalid-name
def rh_search_get_response_proto_to_json(binary):
    msg = routehistory_search_get_pb2.RouteHistorySearchGetResponse()
    msg.ParseFromString(binary)
    return json_format.MessageToDict(msg)


def rh_shuttle_get_response_proto_to_json(binary):
    msg = routehistory_shuttle_order_pb2.RouteHistoryShuttleOrdersResponse()
    msg.ParseFromString(binary)
    return json_format.MessageToDict(msg)
