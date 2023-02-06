import datetime
import re

import pytest

from tests_contractor_profiles_manager import utils


def _parse_providers(providers):
    result = []
    if providers['partner']:
        result.append('park')
    if providers['platform']:
        result.append('yandex')
    return result


def _make_date(date):
    return f'{date}T00:00:00+00:00'


def _format_date(date):
    in_format = '%Y-%m-%dT%H:%M:%S.%f'
    out_format = '%Y-%m-%dT%H:%M:%S+00:00'

    out = datetime.datetime.strptime(date, in_format)
    return out.strftime(out_format)


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):
    class Context:
        def __init__(self):
            self.contractor_profile_id = None
            self.retrieve_response = None
            self.projection = None
            self.check_duplicates_response = None
            self.park_id = None
            self.license_pd_id = None
            self.payment_service_id = None
            self.phone_pd_id = None
            self.email_pd_id = None
            self.enable_updated_trigger = True
            self.driver_profile = None
            self.key_id = None
            self.yandex_uid = None
            self.user_ip = None
            self.ticket_provider = None
            self.is_readonly = None
            self.save_response_code = 200

        def set_data(
                self,
                park_id=None,
                contractor_profile_id=None,
                retrieve_response=None,
                projection=None,
                check_duplicates_response=None,
                license_pd_id=None,
                payment_service_id=None,
                phone_pd_id=None,
                email_pd_id=None,
                driver_profile=None,
                enable_updated_trigger=None,
                key_id=None,
                yandex_uid=None,
                user_ip=None,
                ticket_provider=None,
                is_readonly=None,
                save_response_code=None,
        ):
            if park_id is not None:
                self.park_id = park_id
            if contractor_profile_id is not None:
                self.contractor_profile_id = contractor_profile_id
            if retrieve_response is not None:
                self.retrieve_response = retrieve_response
            if projection is not None:
                self.projection = projection
            if license_pd_id is not None:
                self.license_pd_id = license_pd_id
            if payment_service_id is not None:
                self.payment_service_id = payment_service_id
            if phone_pd_id is not None:
                self.phone_pd_id = phone_pd_id
            if email_pd_id is not None:
                self.email_pd_id = email_pd_id
            if check_duplicates_response is not None:
                self.check_duplicates_response = check_duplicates_response
            if driver_profile is not None:
                self.driver_profile = driver_profile
            if enable_updated_trigger is not None:
                self.enable_updated_trigger = enable_updated_trigger
            if key_id is not None:
                self.key_id = key_id
            if yandex_uid is not None:
                self.yandex_uid = yandex_uid
            if user_ip is not None:
                self.user_ip = user_ip
            if ticket_provider is not None:
                self.ticket_provider = ticket_provider
            if is_readonly is not None:
                self.is_readonly = is_readonly
            if save_response_code is not None:
                self.save_response_code = save_response_code

        @property
        def has_proxy_retrive_mock_calls(self):
            return mock_proxy_retrive.has_calls

        @property
        def has_check_duplicates_mock_calls(self):
            return mock_check_duplicates.has_calls

        @property
        def has_update_profile_mock_calls(self):
            return mock_update_profile.has_calls

        def make_proxy_retrive_request(self):
            return {
                'id_in_set': [f'{self.park_id}_{self.contractor_profile_id}'],
                'projection': self.projection,
            }

        def make_check_duplicates_request(self):
            return {
                'license_pd_id': self.license_pd_id,
                'payment_service_id': self.payment_service_id,
                'phone_pd_id': self.phone_pd_id,
            }

        def make_update_profile_request(self):
            result = {
                'additional_params': {
                    'enable_balance_limit_updated_trigger': (
                        self.enable_updated_trigger
                    ),
                },
            }
            expected_state = {}
            assert len(self.retrieve_response['profiles']) == 1

            old_driver_profile = self.retrieve_response['profiles'][0].get(
                'data', {},
            )
            if 'full_name' in old_driver_profile:
                full_name = old_driver_profile['full_name']
                if 'first_name' in full_name:
                    expected_state['first_name'] = full_name['first_name']
                if 'middle_name' in full_name:
                    expected_state['middle_name'] = full_name['middle_name']
                if 'last_name' in full_name:
                    expected_state['last_name'] = full_name['last_name']
            if 'license' in old_driver_profile:
                driver_license = old_driver_profile['license']
                if 'pd_id' in driver_license:
                    expected_state['driver_license_pd_id'] = driver_license[
                        'pd_id'
                    ]
                if 'country' in driver_license:
                    expected_state['license_country'] = driver_license[
                        'country'
                    ]
            if 'license_driver_birth_date' in old_driver_profile:
                expected_state['license_driver_birth_date'] = _format_date(
                    old_driver_profile['license_driver_birth_date'],
                )
            if 'license_expire_date' in old_driver_profile:
                expected_state['license_expire_date'] = _format_date(
                    old_driver_profile['license_expire_date'],
                )
            if 'license_issue_date' in old_driver_profile:
                expected_state['license_issue_date'] = _format_date(
                    old_driver_profile['license_issue_date'],
                )
            if (
                    'license_experience' in old_driver_profile
                    and 'total' in old_driver_profile['license_experience']
            ):
                expected_state['license_experience'] = {
                    'total': _format_date(
                        old_driver_profile['license_experience']['total'],
                    ),
                }
            result['expected_state'] = expected_state

            identity = None
            if self.key_id is not None:
                identity = {
                    'key_id': self.key_id,
                    'user_ip': self.user_ip,
                    'type': 'fleet_api',
                }
            else:
                identity = {
                    'passport_id': self.yandex_uid,
                    'ticket_provider': self.ticket_provider,
                    'type': 'user',
                }
            result['author'] = {
                'consumer': 'contractor-profiles-manager',
                'identity': identity,
            }

            update_body = {}

            full_name = self.driver_profile['person']['full_name']
            update_body['first_name'] = full_name['first_name']
            update_body['last_name'] = full_name['last_name']
            if 'middle_name' in full_name:
                update_body['middle_name'] = full_name['middle_name']

            if self.email_pd_id is not None:
                update_body['email_pd_id'] = self.email_pd_id

            update_body['phone_pd_ids'] = [self.phone_pd_id]
            if 'address' in self.driver_profile['person']['contact_info']:
                update_body['address'] = self.driver_profile['person'][
                    'contact_info'
                ]['address']

            update_body['license_driver_birth_date'] = _make_date(
                self.driver_profile['person']['driver_license']['birth_date'],
            )
            update_body['license_expire_date'] = _make_date(
                self.driver_profile['person']['driver_license']['expiry_date'],
            )
            update_body['license_issue_date'] = _make_date(
                self.driver_profile['person']['driver_license']['issue_date'],
            )
            update_body['license_country'] = (
                self.driver_profile['person']['driver_license']['country']
                .lower()
                .strip()
            )

            license_number = re.sub(
                r'\s+',
                '',
                self.driver_profile['person']['driver_license']['number'],
            ).upper()
            update_body['license'] = license_number
            update_body['license_number'] = license_number
            update_body['license_normalized'] = utils.make_normalization(
                self.driver_profile['person']['driver_license']['number'],
            )
            update_body['driver_license_pd_id'] = self.license_pd_id

            if 'driver_license_experience' in self.driver_profile['person']:
                update_body['license_experience'] = {
                    'total': _make_date(
                        self.driver_profile['person'][
                            'driver_license_experience'
                        ]['total_since_date'],
                    ),
                }

            update_body['balance_limit'] = round(
                float(self.driver_profile['account']['balance_limit']), 4,
            )
            update_body['balance_deny_onlycard'] = self.driver_profile[
                'account'
            ]['block_orders_on_balance_below_limit']
            update_body['password'] = self.driver_profile['account'][
                'payment_service_id'
            ]
            update_body['rule_id'] = self.driver_profile['account'][
                'work_rule_id'
            ]

            if 'comment' in self.driver_profile['profile']:
                update_body['comment'] = self.driver_profile['profile'][
                    'comment'
                ]
            if 'fire_date' in self.driver_profile['profile']:
                update_body['fire_date'] = _make_date(
                    self.driver_profile['profile']['fire_date'],
                )
            if 'feedback' in self.driver_profile['profile']:
                update_body['check_message'] = self.driver_profile['profile'][
                    'feedback'
                ]

            update_body['hire_date'] = _make_date(
                self.driver_profile['profile']['hire_date'],
            )
            update_body['work_status'] = self.driver_profile['profile'][
                'work_status'
            ]

            update_body['providers'] = _parse_providers(
                self.driver_profile['order_provider'],
            )
            if (
                    'car_id' in self.driver_profile
                    and self.driver_profile['car_id'] is not None
            ):
                update_body['car_id'] = self.driver_profile['car_id']

            result['update_query'] = update_body
            return result

        def make_proxy_retrive_response(self):
            if self.retrieve_response is None:
                return {
                    'profiles': [
                        {
                            'park_driver_profile_id': (
                                f'{self.park_id}_{self.contractor_profile_id}'
                            ),
                        },
                    ],
                }

            return self.retrieve_response

        def make_check_duplicates_response(self):
            if self.check_duplicates_response is None:
                return {'contractor_profiles': []}

            return self.check_duplicates_response

        def make_update_is_readonly_request(self, is_readonly):
            job_name = (
                'pro-profiles-removal-create'
                if is_readonly
                else 'pro-profiles-removal-cancel'
            )
            return {
                'author': {
                    'consumer': 'contractor-profiles-manager',
                    'identity': {'type': 'job', 'job_name': job_name},
                },
                'data': {'is_readonly': is_readonly},
            }

    context = Context()

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/proxy-retrieve',
    )
    def mock_proxy_retrive(request):
        assert request.json == context.make_proxy_retrive_request()
        return context.make_proxy_retrive_response()

    @mockserver.json_handler(
        '/driver-profiles/v1/contractor-profiles/'
        'retrieve-for-check-duplicates',
    )
    def mock_check_duplicates(request):
        check_duplicates_request = context.make_check_duplicates_request()
        if 'license_pd_id' not in request.json:
            check_duplicates_request.pop('license_pd_id')
        assert request.json == check_duplicates_request
        assert request.args['park_id'] == context.park_id
        assert (
            request.args['contractor_profile_id']
            == context.contractor_profile_id
        )
        return context.make_check_duplicates_response()

    @mockserver.json_handler('/driver-profiles/v1/contractor/driver-profile')
    def mock_update_profile(request):
        assert request.json == context.make_update_profile_request()
        assert request.args['park_id'] == context.park_id
        assert (
            request.args['contractor_profile_id']
            == context.contractor_profile_id
        )
        if context.save_response_code != 200:
            return mockserver.make_response(
                json={
                    'code': str(context.save_response_code),
                    'message': 'error',
                },
                status=context.save_response_code,
            )
        return {}

    @mockserver.json_handler('/driver-profiles/v1/driver/is-readonly')
    def _mock_update_is_readonly(request):
        is_readonly = request.json['data']['is_readonly']
        assert request.json == context.make_update_is_readonly_request(
            is_readonly,
        )
        if context.save_response_code != 200:
            return mockserver.make_response(
                json={
                    'code': str(context.save_response_code),
                    'message': 'error',
                },
                status=context.save_response_code,
            )
        return {}

    return context
