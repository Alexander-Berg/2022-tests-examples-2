import datetime
import json
import pathlib
import time
import random
random.seed(42)

from .consts import LAVKA_CORP_CLIENT_ID, EATS_CORP_CLIENT_ID
from . import utils


ADMIN_LINK = (
    'https://tariff-editor.taxi.tst.yandex-team.ru/logs/by_link/{link}'
)
ORDER_LINK = 'https://tariff-editor.taxi.tst.yandex-team.ru/orders/{order_id}'
CLAIM_LINK = 'https://tariff-editor.taxi.tst.yandex-team.ru/corp-claims/show/{claim_id}/info'
LOGS_BY_ORDER = (
    'https://tariff-editor.taxi.tst.yandex-team.ru/logs?order_id={order_id}'
)

SEGMENT_TO_TAXIMETER_STATUS = {
    'performer_found': 'new',
    'pickup_arrived': 'new',
    'pickuped': 'delivering',
    'delivery_arrived': 'delivering',
    'ready_for_pickup_confirmation': 'pickup_confirmation',
    'ready_for_delivery_confirmation': 'droppof_confirmation',
    'pay_waiting': 'droppof_confirmation',
    'ready_for_return_confirmation': 'return_confirmation',
    'return_arrived': 'returning',
    'returning': 'returning',
    'cancelled': 'complete',
    'cancelled_with_payment': 'complete',
    'cancelled_by_taxi': 'complete',
    'delivered': 'complete',
    'returned': 'complete',
    'cancelled_with_items_on_hands': 'complete',
}
PROJECT_DIRECTORY = pathlib.Path(__file__).resolve().parent


class NoPointsLeft(Exception):
    pass


class SegmentNotCreated(Exception):
    pass


def get_next_waybill_point(waybill):
    for point in waybill['execution']['points']:
        visit_status = point['visit_status']
        if visit_status in ('visited', 'skipped'):
            continue
        return point
    raise NoPointsLeft('No points left in waybill sorry')


def get_admin_link(link):
    if not link:
        return 'n/a'
    return ADMIN_LINK.format(link=link)


def get_order_link(order_id):
    if not order_id:
        return 'n/a'
    return ORDER_LINK.format(order_id=order_id)


def get_claim_link(claim_id):
    if not claim_id:
        return 'n/a'
    return CLAIM_LINK.format(claim_id=claim_id)


def get_order_logs_link(order_id):
    if not order_id:
        return 'n/a'
    return LOGS_BY_ORDER.format(order_id=order_id)


def add_post_payment(create_request, phone, email):
    for point in create_request['route_points']:
        if point['type'] == 'destination':
            point['payment_on_delivery'] = {
                # 'external_payment_id': '006e6405-d205-40d3-9284-f5b1eb19f098',
                'payment_method': 'card',
                'customer': {'phone': phone, 'email': email},
            }
    for i, item in enumerate(create_request['items']):
        item['fiscalization'] = {
            'article': f'item {i}',
            'vat_code_str': 'vat0',
            'supplier_inn': '762457411530',
            'item_type': 'product',
            'mark': {'kind': 'compiled', 'code': '444D00000000003741'},
        }
    create_request['items'].append(
        {
            'cost_currency': 'RUB',
            'cost_value': '100',
            'droppof_point': 2,
            'pickup_point': 1,
            'quantity': 1,
            'size': {'height': 0.0, 'length': 0.0, 'width': 0.0},
            'weight': 0,
            'title': 'dostavka',
            'fiscalization': {
                'article': 'dostavka',
                'vat_code_str': 'vat20',
                'supplier_inn': '762457411530',
                'item_type': 'service',
            },
        },
    )


def build_comment(
        speed=100,
        wait=0,
        cargo_noexchange=None,
        reject=None,
        contractor_id=None,
        comment=None,
        force_crutches=False,
        live_batch_with=None,
        batch_with=None,
        wait_for_batch=False,
        reject_live_batch=None,
):
    crutches_json = {}
    crutches = ['crutches-begin', f'speed-{speed}', f'wait-{wait}']
    if cargo_noexchange:
        crutches.append('cargo_noexchange-1')
    if reject is not None:
        crutches.append(f'reject-{reject}')
    if reject_live_batch:
        crutches.append('reject_live_batch-1')
    if contractor_id:
        crutches_json['target_contractor_id'] = contractor_id
    if force_crutches:
        crutches_json['force_crutch_builder'] = True
    if live_batch_with:
        crutches_json['live_batch_with'] = live_batch_with
    if batch_with:
        crutches_json['batch_with'] = batch_with
    if wait_for_batch:
        crutches_json['wait_for_batch'] = wait_for_batch

    if crutches_json:
        crutches.append(
            ''.join(['$$$', json.dumps(crutches_json), '$$$']),
        )

    crutches.append('crutches-end')
    if comment:
        crutches.append(comment)
    return ','.join(crutches)


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
        pickup_code=None,
        randomize_pickup_coordinates=False,
        randomize_dropoff_coordinates=False,
        not_emulator_performer=False,
):
    root_dir = utils.get_project_root()

    email = f'{username}@yandex-team.ru'
    if not request:
        if corp_client_id == LAVKA_CORP_CLIENT_ID:
            request_body = utils.read_json(root_dir / 'requests/lavka.json')
        elif corp_client_id == EATS_CORP_CLIENT_ID:
            request_body = utils.read_json(root_dir / 'eats.json')
        else:
            request_body = utils.read_json(root_dir / 'requests/default.json')
    else:
        request_body = utils.read_json(request)

    # override parameters from json
    for point in request_body['route_points']:
        point['contact'] = {'phone': phone, 'name': 'string'}
        if point['type'] != 'destination':
            point['contact']['email'] = email

        point['skip_confirmation'] = not dont_skip_confirmation
        if pickup_code and point['type'] == 'source':
            point['pickup_code'] = '123456'
            point['skip_confirmation'] = False

        if len(point['address']['coordinates']) == 2:
            if (
                    randomize_dropoff_coordinates
                    and point['type'] == 'destination'
            ):
                point['address']['coordinates'][0] += random.uniform(
                    -0.005, 0.005,
                )
                point['address']['coordinates'][1] += random.uniform(
                    -0.005, 0.005,
                )
            if randomize_pickup_coordinates and (
                    point['type'] == 'source' or point['type'] == 'return'
            ):
                point['address']['coordinates'][0] += random.uniform(
                    -0.005, 0.005,
                )
                point['address']['coordinates'][1] += random.uniform(
                    -0.005, 0.005,
                )
    request_body['emergency_contact'] = {'phone': phone, 'name': 'string'}
    request_body['comment'] = comment

    if taxi_class:
        if 'client_requirements' not in request_body:
            request_body['client_requirements'] = {}
        request_body['client_requirements']['taxi_class'] = taxi_class

    if due:
        request_body['due'] = (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(seconds=due)
        ).isoformat()

    if not_emulator_performer:
        if 'features' not in request_body:
            request_body['features'] = []
        already_contains_feature = any(
            map(
                lambda f: f['id'] == 'not_emulator_performer_feature',
                request_body['features'],
            ),
        )

        if not already_contains_feature:
            request_body['features'].append(
                {'id': 'not_emulator_performer_feature'},
            )

    if post_payment:
        add_post_payment(request_body, phone, email)

    return request_body


class Journals:
    def __init__(self, claims_client):
        self.claims_client = claims_client
        self._cursor_path = pathlib.Path('/var/tmp/.segments-cursor.dat')
        self.segments_journal_cursor = self._read_cursor()

        self._prepare_journals()

    def _read_cursor(self):
        if not self._cursor_path.exists():
            return None
        return self._cursor_path.read_text()

    def _write_cursor(self, cursor):
        self._cursor_path.write_text(cursor)

    def _prepare_journals(self):
        while True:
            self.segments_journal_cursor, entries = (
                self.claims_client.read_segments_journal(
                    self.segments_journal_cursor,
                )
            )
            self._write_cursor(self.segments_journal_cursor)

            if entries:
                print('Waiting for segments journal cursor...')
                continue
                # time.sleep(1)
            else:
                break

    def get_segment_id(self, claim_id):
        _, entries = self.claims_client.read_segments_journal(
            self.segments_journal_cursor,
        )
        for entry in entries:
            if entry.get('current', {}).get('claim_id') == claim_id:
                return entry['segment_id']

        return None

    def wait_for_segment_id(self, claim_id, wait=5):
        timer = datetime.datetime.now() + datetime.timedelta(seconds=wait)
        segment = None
        while True:
            segment_id = self.get_segment_id(claim_id)
            if segment_id or datetime.datetime.now() > timer:
                return segment_id
            else:
                time.sleep(1)
                continue
