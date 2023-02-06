# pylint: disable=C5521, R1705, R1710
import pytest

from tests_contractor_profiles_manager.utils import make_normalization

DATA_TYPES = {'phones', 'emails', 'driver_licenses'}


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):
    class Context:
        def __init__(self):
            self.driver_license = None
            self.license_pd_id = None
            self.phone = None
            self.phone_pd_id = None
            self.email = None
            self.email_pd_id = None
            self.error_code = None

        def set_data(
                self,
                driver_license=None,
                license_pd_id=None,
                phone=None,
                phone_pd_id=None,
                email=None,
                email_pd_id=None,
                error_code=None,
        ):
            if driver_license is not None:
                self.driver_license = driver_license
            if license_pd_id is not None:
                self.license_pd_id = license_pd_id
            if phone is not None:
                self.phone = phone
            if phone_pd_id is not None:
                self.phone_pd_id = phone_pd_id
            if email is not None:
                self.email = email
            if email_pd_id is not None:
                self.email_pd_id = email_pd_id
            if error_code is not None:
                self.error_code = error_code

        @property
        def has_store_calls(self):
            return mock_store.has_calls

        @property
        def has_retrieve_calls(self):
            return mock_retrieve.has_calls

        def make_request_store(self, data_type):
            if data_type == 'phones':
                return {'value': self.phone, 'validate': True}
            elif data_type == 'driver_licenses':
                return {
                    'value': make_normalization(self.driver_license),
                    'validate': True,
                }
            elif data_type == 'emails':
                return {'value': self.email, 'validate': True}

        def make_response(self, data_type):
            if data_type == 'phones':
                return {'value': self.phone, 'id': self.phone_pd_id}
            elif data_type == 'driver_licenses':
                return {
                    'value': make_normalization(self.driver_license),
                    'id': self.license_pd_id,
                }
            elif data_type == 'emails':
                return {'value': self.email, 'id': self.email_pd_id}

        def make_request_retrieve(self, data_type):
            if data_type == 'phones':
                return {'id': self.phone_pd_id, 'primary_replica': False}
            elif data_type == 'driver_licenses':
                return {'id': self.license_pd_id, 'primary_replica': False}
            elif data_type == 'emails':
                return {'id': self.email_pd_id, 'primary_replica': False}

    context = Context()
    store_url = r'/personal/v1/(?P<data_type>\w+)/store'
    retrieve_url = r'/personal/v1/(?P<data_type>\w+)/retrieve'

    @mockserver.json_handler(store_url, regex=True)
    def mock_store(request, data_type):
        assert data_type in DATA_TYPES
        request_json = context.make_request_store(data_type)
        if data_type == 'driver_licenses':
            request_json.update({'validate': request.json.get('validate')})
        assert request.json == request_json
        return context.make_response(data_type)

    @mockserver.json_handler(retrieve_url, regex=True)
    def mock_retrieve(request, data_type):
        assert data_type in DATA_TYPES
        assert request.json == context.make_request_retrieve(data_type)
        if context.error_code is not None:
            return mockserver.make_response(
                json={'code': 'error', 'message': 'error'},
                status=context.error_code,
            )
        return context.make_response(data_type)

    return context
