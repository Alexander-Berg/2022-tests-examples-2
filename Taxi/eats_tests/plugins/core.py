import datetime
import time
import typing

import pytest
import requests

from eats_tests.utils import order_statuses


class EatsCoreService:
    def __init__(self):
        self.host = None

    def set_host(self, host: str):
        self.host = host

    def get_health(self) -> requests.Response:
        return requests.get(url=f'{self.host}/api/v1/health')

    def get_pickers_list(self) -> requests.Response:
        return requests.post(
            url=f'{self.host}/server/api/v1/supply/pickers-list',
        )

    def cart_append(
            self,
            eater_id: int,
            item_id: int,
            latitude: float,
            longitude: float,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/api/v1/cart'
            f'?latitude={latitude}&longitude={longitude}',
            json={'item_id': item_id},
            cookies={'PHPSESSID': f'test_{eater_id}'},
            headers={
                'X-YaTaxi-User': f'eats_user_id={eater_id}',
                'X-Eats-User': f'user_id={eater_id}',
                'X-Ya-Service-Ticket': '3:serv:1-2011662',
                'X-Device-Id': f'test_device_{eater_id}',
            },
        )

    def go_checkout(
            self,
            address_identity: int,
            provider: str,
            eater_id: int,
            passport_uid: int,
            latitude: float,
            longitude: float,
    ) -> requests.Response:
        return requests.post(
            url=f'{self.host}/api/v2/cart/go-checkout',
            params={'latitude': latitude, 'longitude': longitude},
            json={
                'address': {
                    'identity': str(address_identity),
                    'provider': provider,
                },
            },
            cookies={'PHPSESSID': f'test_{eater_id}'},
            headers={
                'X-YaTaxi-User': f'eats_user_id={eater_id}',
                'X-Eats-User': f'user_id={eater_id}',
                'X-Ya-Service-Ticket': '3:serv:1-2011662',
                'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
                'X-YaTaxi-Pass-Flags': 'phonish',
                'X-Yandex-UID': str(passport_uid),
                'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
                'X-Request-Language': 'ru',
                'X-Request-Application': f'app_name=yango_android',
                'X-Ya-User-Ticket': 'user_ticket',
                'X-Device-Id': f'test_device_{eater_id}',
            },
        )

    def create_order(
            self,
            eater_id: int,
            passport_uid: int,
            user_email: str,
            user_phone_number: str,
            user_first_name: str,
            latitude: float,
            longitude: float,
            payment_method_id: int,
            persons_quantity: int,
            card_id: str,
            cost_for_customer: float,
            address_comment: typing.Optional[str] = None,
            change_on: int = 500,
    ) -> requests.Response:
        now = datetime.datetime.now()
        delivery_start = now.astimezone().replace(microsecond=0).isoformat()
        stop = now + datetime.timedelta(minutes=30)
        delivery_stop = stop.astimezone().replace(microsecond=0).isoformat()

        return requests.post(
            url=f'{self.host}/api/v1/orders'
            f'?latitude={latitude}&longitude={longitude}',
            json={
                'comment': 'Random order Go Checkout',
                'email': user_email,
                'phone': user_phone_number,
                'first_name': user_first_name,
                'payment_method_id': payment_method_id,
                'persons_quantity': persons_quantity,
                'change_on': change_on,
                'code': None,
                'address': {
                    'city': 'Москва',
                    'house': '1',
                    'comment': address_comment,
                },
                'location': {'longitude': longitude, 'latitude': latitude},
                'payment_information': {
                    'type': 'card',
                    'id': card_id,
                    'costForCustomer': '%.2f' % cost_for_customer,
                },
                'extended_options': [
                    {
                        'type': 'slot_interval',
                        'delivery_slot_started_at': delivery_start,
                        'delivery_slot_finished_at': delivery_stop,
                    },
                ],
            },
            cookies={'PHPSESSID': f'test_{eater_id}'},
            headers={
                'X-YaTaxi-User': f'eats_user_id={eater_id}',
                'X-Eats-User': f'user_id={eater_id}',
                'X-Ya-Service-Ticket': '3:serv:1-2011662',
                'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
                'X-YaTaxi-Pass-Flags': 'phonish',
                'X-Yandex-UID': str(passport_uid),
                'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
                'X-Request-Language': 'ru',
                'X-Request-Application': f'app_name=yango_android',
                'X-Ya-User-Ticket': 'user_ticket',
                'X-Device-Id': f'test_device_{eater_id}',
            },
        )

    def get_order(
            self, order_nr: str, eater_id: int, passport_uid: int,
    ) -> requests.Response:
        return requests.get(
            url=f'{self.host}/api/v1/orders/{order_nr}',
            cookies={'PHPSESSID': f'test_{eater_id}'},
            headers={
                'X-YaTaxi-User': f'eats_user_id={eater_id}',
                'X-Ya-Service-Ticket': '3:serv:1-2011662',
                'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
                'X-YaTaxi-Pass-Flags': 'phonish',
                'X-Yandex-UID': str(passport_uid),
                'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
                'X-Request-Language': 'ru',
                'X-Request-Application': f'app_name=yango_android',
                'X-Ya-User-Ticket': 'user_ticket',
                'X-Device-Id': f'test_device_{eater_id}',
            },
        )

    def cancel_order(self, order_nr: str, eater_id: int, passport_uid: int):
        return requests.post(
            url=f'{self.host}/api/v2/orders/{order_nr}/cancel',
            json={'reasonCode': 'client.self.accidentally_placed_order'},
            cookies={'PHPSESSID': f'test_{eater_id}'},
            headers={
                'X-YaTaxi-User': f'eats_user_id={eater_id}',
                'X-Ya-Service-Ticket': '3:serv:1-2011662',
                'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
                'X-YaTaxi-Pass-Flags': 'phonish',
                'X-Yandex-UID': str(passport_uid),
                'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
                'X-Request-Language': 'ru',
                'X-Request-Application': f'app_name=yango_android',
                'X-Ya-User-Ticket': 'user_ticket',
                'X-Device-Id': f'test_device_{eater_id}',
            },
        )

    def order_send_immediately(self, order_nr: str):
        return requests.post(
            url=f'{self.host}/internal-api/v1/order-send/send-to-place',
            json={'order_id': order_nr, 'sync': True, 'idempotency_key': '1'},
            headers={'X-Ya-Service-Ticket': '3:serv:1-2011662'},
        )

    def wait_for_courier_assigned(
            self,
            order_nr: str,
            eater_id: int,
            passport_uid: int,
            max_timeout: int = 10,
    ):
        for _ in range(max_timeout):
            response = self.get_order(order_nr, eater_id, passport_uid)
            assert response.status_code == 200, response.text
            if response.json()['courier']:
                return
            time.sleep(1)
        pytest.fail(f'Courier assignment timeout for order_nr={order_nr}')

    def wait_for_order_status_changed(
            self,
            order_nr: str,
            eater_id: int,
            passport_uid: int,
            expected_status: order_statuses.EatsOrderStatus,
            max_timeout=10,
    ):
        for _ in range(max_timeout):
            response = self.get_order(order_nr, eater_id, passport_uid)
            assert response.status_code == 200, (
                f'Unexpected response code for order_nr={order_nr}, '
                f'response_text={response.text}'
            )
            status_id = order_statuses.EatsOrderStatus(
                int(response.json()['status']['id']),
            )
            if status_id == expected_status:
                return
            time.sleep(1)
        pytest.fail(
            'Cannot move order_nr={0} to expected status: {1}'.format(
                order_nr, expected_status,
            ),
        )


@pytest.fixture
def core():
    return EatsCoreService()
