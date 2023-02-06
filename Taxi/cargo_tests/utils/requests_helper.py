import datetime
import json
import pathlib
import typing


def get_project_root() -> pathlib.Path:
    return pathlib.Path(__file__).parent.parent.parent


def read_json(path: pathlib.Path) -> typing.Dict:
    with open(path) as json_file:
        return json.load(json_file)


def add_post_payment(
        create_request: typing.Dict, phone: str, email: str,
) -> None:
    for point in create_request['route_points']:
        if point['type'] == 'destination':
            point['payment_on_delivery'] = {
                'payment_method': 'card',
                'customer': {'phone': phone, 'email': email},
            }
    for i, item in enumerate(create_request['items']):
        item['fiscalization'] = {
            'article': f'item {i}',
            'vat_code_str': 'vat0',
            'supplier_inn': '762457411530',
            'item_type': 'service',
        }


def build_request(
        *,
        username,
        phone,
        comment,
        request=None,
        corp_client_id=None,
        taxi_class=None,
        dont_skip_confirmation=False,
        post_payment=None,
        due=None,
) -> typing.Dict:
    root_dir = get_project_root()

    email = f'{username}@yandex-team.ru'
    if not request:
        request_body = read_json(root_dir / 'test_data/default.json')
    else:
        request_body = read_json(request)

    # override parameters from json
    for point in request_body['route_points']:
        point['contact'] = {'phone': phone, 'name': 'string'}
        if point['type'] != 'destination':
            point['contact']['email'] = email
        point['skip_confirmation'] = not dont_skip_confirmation

    request_body['emergency_contact'] = {'phone': phone, 'name': 'string'}
    request_body['comment'] = comment
    if 'client_requirements' not in request_body:
        request_body['client_requirements'] = {}
    if taxi_class:
        request_body['client_requirements']['taxi_class'] = taxi_class

    if due:
        request_body['due'] = (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=due)
        ).isoformat()
    if post_payment:
        add_post_payment(request_body, phone, email)
    return request_body
