# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name, import-only-modules
from datetime import datetime

import pytest

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'


def is_valid_header(request_header, context_header):
    for key, value in context_header.items():
        assert request_header.get(key) == value, f'invalid header {key}'
    return True


@pytest.fixture(name='mock_parks_driver_creation')
def _mock_parks_driver_creation(mockserver):
    class Context:
        def __init__(self):
            self.car_id = None
            self.account = {}
            self.order_provider = {}
            self.contact_info = {}
            self.driver_license = {}
            self.driver_license_experience = {}
            self.full_name = {}
            self.profile = {}
            self.fleet_api_client_id = None
            self.fleet_api_key_id = None
            self.real_ip = None
            self.idempotency_token = None

        def set_data(
                self,
                car_id=None,
                account=None,
                order_provider=None,
                contact_info=None,
                driver_license=None,
                driver_license_experience=None,
                full_name=None,
                profile=None,
                fleet_api_client_id=None,
                fleet_api_key_id=None,
                real_ip=None,
                idempotency_token=None,
        ):
            if car_id is not None:
                self.car_id = car_id
            if account is not None:
                self.account = account
            if order_provider is not None:
                self.order_provider = order_provider
            if contact_info is not None:
                self.contact_info = contact_info
            if driver_license is not None:
                self.driver_license = driver_license
            if driver_license_experience is not None:
                self.driver_license_experience = driver_license_experience
            if full_name is not None:
                self.full_name = full_name
            if profile is not None:
                self.profile = profile
            if fleet_api_client_id is not None:
                self.fleet_api_client_id = fleet_api_client_id
            if fleet_api_key_id is not None:
                self.fleet_api_key_id = fleet_api_key_id
            if real_ip is not None:
                self.real_ip = real_ip
            if idempotency_token is not None:
                self.idempotency_token = idempotency_token

        def make_parks_request(self):
            request = {'driver_profile': {}}

            if self.account:
                request['accounts'] = [
                    {
                        'balance_limit': self.account['balance_limit'],
                        'type': 'current',
                    },
                ]

            request['driver_profile']['providers'] = []
            request['driver_profile']['profession_id'] = (
                self.account.get('profession_id') or 'taxi-driver'
            )
            if self.order_provider['partner']:
                request['driver_profile']['providers'].append('park')
            if self.order_provider['platform']:
                request['driver_profile']['providers'].append('yandex')

            if self.driver_license:
                request['driver_profile']['driver_license'] = {
                    'birth_date': self.driver_license['birth_date'],
                    'country': self.driver_license['country'],
                    'expiration_date': self.driver_license['expiry_date'],
                    'issue_date': self.driver_license['issue_date'],
                    'number': self.driver_license['number'],
                }

            if self.driver_license_experience:
                request['driver_profile']['license_experience'] = {
                    'total_since': self.driver_license_experience[
                        'total_since_date'
                    ],
                }

            request['driver_profile']['hire_date'] = self.profile['hire_date']

            if 'comment' in self.profile:
                request['driver_profile']['comment'] = self.profile['comment']

            if self.car_id is not None:
                request['driver_profile']['car_id'] = self.car_id

            if 'work_rule_id' in self.account:
                request['driver_profile']['work_rule_id'] = self.account[
                    'work_rule_id'
                ]

            if 'payment_service_id' in self.account:
                request['driver_profile']['payment_service_id'] = self.account[
                    'payment_service_id'
                ]

            if 'block_orders_on_balance_below_limit' in self.account:
                request['driver_profile'][
                    'balance_deny_onlycard'
                ] = self.account['block_orders_on_balance_below_limit']

            request['driver_profile']['first_name'] = self.full_name[
                'first_name'
            ]
            request['driver_profile']['last_name'] = self.full_name[
                'last_name'
            ]

            if 'middle_name' in self.full_name:
                request['driver_profile']['middle_name'] = self.full_name[
                    'middle_name'
                ]

            if 'email' in self.contact_info:
                request['driver_profile']['email'] = self.contact_info['email']
            if 'address' in self.contact_info:
                request['driver_profile']['address'] = self.contact_info[
                    'address'
                ]
            request['driver_profile']['phones'] = [self.contact_info['phone']]

            return request

        def make_parks_responce(self):
            providers = []
            if self.order_provider['partner']:
                providers.append('park')
            if self.order_provider['platform']:
                providers.append('yandex')
            hire_date = datetime.strptime(
                self.profile['hire_date'], DATE_FORMAT,
            )
            return {
                'accounts': None,
                'driver_profile': {
                    'id': 'contractor_id',
                    'park_id': '123',
                    'first_name': self.full_name['first_name'],
                    'last_name': self.full_name['last_name'],
                    'hire_date': hire_date.strftime(DATETIME_FORMAT),
                    'providers': providers,
                    'work_status': 'working',
                },
            }

        @property
        def has_mock_parks_calls(self):
            return mock_parks.has_calls

        @property
        def gen_idempotency_token(self):
            return (
                f'fleet-api/{self.fleet_api_key_id}/{self.idempotency_token}'
            )

        def make_header(self):
            return {
                'X-Fleet-API-Client-ID': self.fleet_api_client_id,
                'X-Fleet-API-Key-ID': self.fleet_api_key_id,
                'X-Real-IP': self.real_ip,
                'X-Idempotency-Token': self.gen_idempotency_token,
            }

    context = Context()

    @mockserver.json_handler('/parks/driver-profiles/create')
    def mock_parks(request):
        assert is_valid_header(request.headers, context.make_header())
        assert request.json == context.make_parks_request()
        return context.make_parks_responce()

    return context
