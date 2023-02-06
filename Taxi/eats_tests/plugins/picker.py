import datetime
import random
import time
import typing

import pytest
import requests

WAIT_FOR_PICKING_COMPLETED = 300


class Headers:
    _internal_headers: typing.Dict[str, str] = {
        'Content-Type': 'application/json',
        'X-Ya-Service-Ticket': '3:serv:test',
        'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
        'X-YaTaxi-Park-Id': 'park_id1',
        'X-Request-Application': 'XYPro',
        'X-Request-Application-Version': '9.99 (9999)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'ios',
    }

    @classmethod
    def get_internal_headers(cls):
        return cls._internal_headers

    @classmethod
    def get_external_headers(cls, picker_id):
        headers = cls._internal_headers
        headers['X-YaEda-CourierId'] = picker_id
        return headers


class OrderItems:
    @classmethod
    def get_items(cls) -> typing.List[typing.Dict]:
        return [
            {
                'id': 'ПН00000010',
                'vendor_code': 'РН102534',
                'name': 'Палочки хлебные Гриссини',
                'category': {
                    'id': '57c3d247-e7ac-11ea-98c6-001e676a98dc',
                    'name': 'Эксклюзивно в Мираторге',
                },
                'barcode': {
                    'values': ['8000633034559'],
                    'weight_encoding': None,
                },
                'location': '',
                'package_info': 'Не указано',
                'quantity': 1,
                'price': 100,
                'measure': {'unit': 'GRM', 'value': 1},
                'measure_v2': {
                    'value': 100,
                    'max_overweight': 0,
                    'unit': 'GRM',
                    'quantum': 1,
                    'absolute_quantity': 1,
                    'quantum_quantity': 1,
                    'quantum_price': 1,
                    'price': 100,
                },
                'is_catch_weight': False,
                'images': [],
            },
        ]


class BasePickerService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host


class PickerOrdersService(BasePickerService):
    @classmethod
    def random_order_nrs(cls) -> str:
        number = str(random.randint(111111, 999999))
        return f'{datetime.date.today().strftime("%y%m%d")}-{number}'

    def create_order(
            self,
            place_id: int,
            flow_type: str,
            order_nr: str = None,
            claim_id=None,
    ) -> typing.Tuple[typing.Optional[str], requests.Response]:
        if not order_nr:
            order_nr = PickerOrdersService.random_order_nrs()

        response = requests.post(
            url=f'{self.host}/api/v1/order',
            headers=Headers.get_internal_headers(),
            json={
                'eats_id': order_nr,
                'place_id': place_id,
                'claim_id': claim_id,
                'estimated_picking_time': 1000,
                'items': OrderItems.get_items(),
                'payment': {
                    'value': 579,
                    'limit': 579 * 1.1,
                    'currency': {'code': 'RUB'},
                },
                'flow_type': flow_type,
                'comment': '',
                'require_approval': False,
                'customer': {'name': 'Yandex.Eda', 'phone': '88006001210'},
            },
        )
        return order_nr, response

    def put_courier(
            self, order_nr: str, picker_id: str, card_value: str = '123456789',
    ) -> requests.Response:
        return requests.put(
            url=f'{self.host}/api/v1/order/courier?eats_id={order_nr}',
            headers=Headers.get_internal_headers(),
            json={
                'id': str(picker_id),
                'requisites': [{'type': 'TinkoffBank', 'value': card_value}],
            },
        )

    def get_order(self, order_nr: str) -> requests.Response:
        return requests.get(
            url=f'{self.host}/api/v1/order',
            params={'eats_id': order_nr},
            headers=Headers.get_internal_headers(),
        )

    def cancel_order(self, order_nr: str) -> requests.Response:
        return requests.delete(
            url=f'{self.host}/api/v1/order?eats_id={order_nr}',
            headers=Headers.get_internal_headers(),
            json={'comment': 'test'},
        )

    def get_picker_orders(self, picker_id: str) -> requests.Response:
        return requests.get(
            url=f'{self.host}/api/v1/picker/orders?picker_id={picker_id}',
            headers=Headers.get_internal_headers(),
        )

    def start_order(self, order_nr: str, picker_id: str) -> requests.Response:
        return requests.post(
            url=f'{self.host}/4.0/eats-picker/api/v1/order/start',
            headers=Headers.get_external_headers(picker_id),
            json={'eats_id': order_nr},
        )

    def external_get_orders(self, picker_id: str) -> requests.Response:
        return requests.get(
            url=f'{self.host}/4.0/eats-picker/api/v1/picker/orders',
            headers=Headers.get_external_headers(picker_id),
        )

    def wait_order_sync(self, order_nr: str):
        for _ in range(30):
            response = self.get_order(order_nr)
            if response.status_code == 200:
                return
            time.sleep(1)
        pytest.fail(f'Order {order_nr} is not appeared in eats-picker-orders')

    def wait_for_picker_complete_order(self, order_nr: str):
        picker_order = None
        for _ in range(WAIT_FOR_PICKING_COMPLETED):
            response = self.get_order(order_nr)
            if response.status_code != 200:
                pytest.fail(
                    f'Failed to get order \'{order_nr}\' from {self.host}:\n'
                    f'{response.text}',
                )

            body = response.json()
            picker_order = body['payload']
            if picker_order['status'] == 'complete':
                return
            time.sleep(1)
        pytest.fail(
            f'Order \'{order_nr}\' has`t been completed:\n{picker_order}',
        )


class PickerDispatchService(BasePickerService):
    def dispatch(self, order_nr: str) -> requests.Response:
        return requests.post(
            url=rf'{self.host}/api/v1/dispatch',
            headers=Headers.get_internal_headers(),
            json={'eats_id': order_nr},
        )


class PickerSupplyService(BasePickerService):
    def select_picker(self, place_id: int, duration: int = 1):
        return requests.post(
            url=f'{self.host}/api/v1/select-picker',
            headers=Headers.get_internal_headers(),
            json={'place_id': place_id, 'picking_duration': duration},
        )

    def change_priority(
            self, picker_id: str, add: float = 0.0, multiply: float = 0.0,
    ):
        return requests.post(
            url=f'{self.host}/api/v1/picker/change-priority',
            headers=Headers.get_internal_headers(),
            json={'picker_id': picker_id, 'add': add, 'multiply': multiply},
        )


@pytest.fixture
def picker():
    return PickerOrdersService()


@pytest.fixture
def dispatch():
    return PickerDispatchService()


@pytest.fixture
def supply():
    return PickerSupplyService()
