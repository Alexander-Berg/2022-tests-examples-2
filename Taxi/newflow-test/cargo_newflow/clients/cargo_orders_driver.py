import uuid
import time
import typing

from . import base
from cargo_newflow import consts


class CargoOrdersDriverClient(base.BaseClient):
    _base_url = 'http://cargo-orders.taxi.tst.yandex.net/'
    _tvm_id = '2020955'

    def __init__(
            self,
            user,
            performer,
            cargo_order_id,
            *,
            waybill_ref,
            dispatch_client,
            corp_client_id=consts.DEFAULT_CORP_CLIENT_ID,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self._user = user
        self._cargo_order_id = cargo_order_id
        self._waybill_ref = waybill_ref
        self._dispatch_client = dispatch_client
        self._driver_profile_id = performer['driver_id']
        self._park_id = performer['park_id']
        self._corp_client_id = corp_client_id

    def performers_bulk_info(self, order_ids: typing.List[str]):
        return self._perform_post(
            '/v1/performers/bulk-info', json={'order_ids': order_ids},
        )

    def _get_next_status_and_point(self):
        state_response = self.state()
        return (
            state_response['status'],  # taximeter status
            state_response['current_point']['id'],  # claim_point_id
        )

    def state(self):
        return self._perform_post(
            '/driver/v1/cargo-claims/v1/cargo/state',
            json={'cargo_ref_id': 'order/' + self._cargo_order_id},
        )

    def arrive_at_point(self):
        taximeter_status, claim_point_id = self._get_next_status_and_point()
        return self._perform_post(
            '/driver/v1/cargo-claims/v1/cargo/arrive_at_point',
            json={
                'last_known_status': taximeter_status,
                'cargo_ref_id': 'order/' + self._cargo_order_id,
                'idempotency_token': uuid.uuid4().hex,
                'point_id': claim_point_id,
            },
        )

    def exchange_init(self):
        taximeter_status, claim_point_id = self._get_next_status_and_point()
        return self._perform_post(
            '/driver/v1/cargo-claims/v1/cargo/exchange/init',
            json={
                'last_known_status': taximeter_status,
                'cargo_ref_id': 'order/' + self._cargo_order_id,
                'idempotency_token': uuid.uuid4().hex,
                'point_id': claim_point_id,
            },
        )

    def exchange_confirm(self):
        taximeter_status, claim_point_id = self._get_next_status_and_point()
        return self._perform_post(
            'driver/v1/cargo-claims/v1/cargo/exchange/confirm',
            json={
                'last_known_status': taximeter_status,
                'confirmation_code': '123456',
                'cargo_ref_id': 'order/' + self._cargo_order_id,
                'point_id': claim_point_id,
            },
        )

    def return_point(self, comment=None):
        taximeter_status, claim_point_id = self._get_next_status_and_point()
        return self._perform_post(
            'driver/v1/cargo-claims/v1/cargo/return',
            json={
                'last_known_status': taximeter_status,
                'cargo_ref_id': 'order/' + self._cargo_order_id,
                'point_id': claim_point_id,
                'comment': comment or 'point returned by test client',
            },
        )

    def _get_headers(self, headers):
        return {
            **super()._get_headers(headers),
            'X-B2B-Client-Id': self._corp_client_id,
            'Accept-Language': 'ru',
            'X-Yandex-Login': self._user,
            'X-Yandex-UID': '123',
            'X-YaTaxi-Driver-Profile-Id': self._driver_profile_id,
            'X-YaTaxi-Park-Id': self._park_id,
            'X-Request-Application': 'taximeter',
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
        }

    def iteration(self, do_return=False, case='default'):
        time.sleep(1)
        try:
            status = self.arrive_at_point()
        except base.HttpConflictError:
            pass

        status = self.exchange_init()
        if do_return:
            status = self.return_point()
        else:
            status = self.exchange_confirm()
        if status['new_status'] == 'complete':
            return True
        return False

