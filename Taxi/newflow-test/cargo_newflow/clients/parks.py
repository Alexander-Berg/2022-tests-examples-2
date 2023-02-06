import uuid

from .base import BaseClient
import cargo_newflow.consts as consts


class ParksClient(BaseClient):
    _base_url = 'http://parks.taxi.tst.yandex.net/'
    _tvm_id = '2002064'

    def create_profile(self, park_id, json):
        return self._perform_post(
            'internal/driver-profiles/create',
            params={'park_id': park_id},
            json=json,
            headers={'X-Idempotency-Token': str(uuid.uuid4())},
        )

    def search_profile(self, phone):
        return self._perform_post(
            'driver-profiles/search',
            json={
                'query': {'driver': {'phone': [phone]}},
                'fields': {'driver': ['id']},
            },
        )

    def cars_list(self, park_id):
        return self._perform_post(
            '/cars/list', json={'query': {'park': {'id': park_id}}},
        )

    def bind_car(self, driver_id, park_id, car_id):
        return self._perform_put(
            '/driver-profiles/car-bindings',
            params={
                'park_id': park_id,
                'driver_profile_id': driver_id,
                'car_id': car_id,
            },
            headers={'X-YaTaxi-Driver-Id': driver_id},
        )

    def create_car(self, park_id, json):
        return self._perform_post(
            'cars',
            params={'park_id': park_id},
            json=json,
            headers={
                'X-Ya-User-Ticket': (
                    f'_!fake!_ya-{consts.PARK_DIRECTOR_MAPPING[park_id]}'
                ),
                'X-Ya-User-Ticket-Provider': 'yandex',
                'X-Idempotency-Token': str(uuid.uuid4()),
            },
        )
