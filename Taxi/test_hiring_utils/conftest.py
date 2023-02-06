# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import functools
import logging
import random

import pytest

import hiring_utils.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_utils.generated.service.pytest_plugins']


logger = logging.getLogger(__name__)


@pytest.fixture
def simple_secdist(simple_secdist):
    # в нужные секции дописываем свои значения
    simple_secdist['settings_override'].update(
        {
            'INFRANAIM_APIKEYS': {'driveryandex': 'token_driveryandex'},
            'OKTELL_DB_AUTH': {
                'host': 'test',
                'port': '0000',
                'username': 'test',
                'password': 'test',
                'database': 'test',
            },
        },
    )
    return simple_secdist


def gen_phone():
    return '+79' + str(random.randint(10 ** 8, 10 ** 9 - 1))


@functools.lru_cache(None)
def personal_response(type_, id_):
    value = gen_phone()
    response = {type_: value, 'id': id_}
    return response


@pytest.fixture  # noqa: F405
def personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def retrieve_phones_bulk(request):
        items = []
        for item in request.json['items']:
            items.append(personal_response('value', item['id']))
        return {'items': items}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def retrieve_phone(request):
        assert request.json == {'id': 'phone_pd_id'}
        return {'id': 'phone_pd_id', 'value': '+79001231234'}

    @mockserver.json_handler('/personal/v1/phones/store')
    def store_phone(request):
        return {
            'id': 'fd835ed6a95f44b598cfca688c710c84',
            'value': '+79998887766',
        }


@pytest.fixture  # noqa: F405
def driver_profiles(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def retrieve(request):
        data = {
            'profiles': [
                {
                    'park_driver_profile_id': '123123',
                    'data': {
                        'phone_pd_ids': [
                            {'pd_id': '725ff1cacb4145658d99ebb54aff939d'},
                        ],
                    },
                },
            ],
        }
        return data


@pytest.fixture  # noqa: F405
def cargo_claims(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def v2_get_full_claim(request):
        data = {
            'id': '121231',
            'version': 1,
            'status': 'new',
            'corp_client_id': '01234567890123456789012345678912',
            'emergency_contact': {
                'name': 'emergency_name',
                'phone': '+79098887777',
                'personal_phone_id': 'asdfsdf',
            },
            'skip_door_to_door': False,
            'skip_client_notify': False,
            'skip_emergency_notify': False,
            'optional_return': False,
            'pricing': {},
            'comment': 'Очень полезный комментарий',
            'available_cancel_state': 'free',
            'items': [
                {
                    'title': 'item title 1',
                    'extra_id': '1',
                    'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                    'cost_value': '10.40',
                    'cost_currency': 'RUR',
                    'weight': 10.2,
                    'pickup_point': 1,
                    'droppof_point': 2,
                    'quantity': 2,
                    'id': 12121,
                },
                {
                    'title': 'item title 2',
                    'extra_id': '2',
                    'size': {'length': 10.0, 'width': 5.8, 'height': 0.5},
                    'cost_value': '53.00',
                    'cost_currency': 'RUR',
                    'weight': 3.7,
                    'pickup_point': 1,
                    'droppof_point': 3,
                    'quantity': 1,
                    'id': 123123,
                },
            ],
            'route_points': [
                {
                    'point_id': 1,
                    'visit_order': 1,
                    'address': {
                        'fullname': '1',
                        'coordinates': [1, 2],
                        'country': '1',
                        'city': '1',
                        'street': '1',
                        'building': '1',
                        'door_code': 'door_1',
                        'comment': 'comment_1',
                    },
                    'contact': {
                        'phone': '+79999999991',
                        'name': 'string',
                        'email': '1@yandex.ru',
                        'personal_phone_id': '12112',
                    },
                    'type': 'source',
                    'id': 123123,
                    'visit_status': 'visited',
                },
                {
                    'point_id': 2,
                    'visit_order': 2,
                    'address': {
                        'fullname': '2',
                        'coordinates': [2, 3],
                        'country': '2',
                        'city': '2',
                        'street': '2',
                        'building': '2',
                        'door_code': 'door_2',
                        'comment': 'comment_2',
                    },
                    'contact': {
                        'phone': '+79999999992',
                        'name': 'string',
                        'personal_phone_id': '12312312',
                    },
                    'type': 'destination',
                    'id': 23123,
                    'visit_status': 'visited',
                },
                {
                    'point_id': 3,
                    'visit_order': 3,
                    'address': {
                        'fullname': '3',
                        'coordinates': [3, 4],
                        'country': '3',
                        'city': '3',
                        'street': '3',
                        'building': '3',
                        'door_code': 'door_3',
                        'comment': 'comment_3',
                    },
                    'contact': {
                        'phone': '+79999999993',
                        'name': 'string',
                        'email': '3@yandex.ru',
                        'personal_phone_id': '1231321',
                    },
                    'type': 'destination',
                    'id': 1212333,
                    'visit_status': 'visited',
                },
                {
                    'point_id': 4,
                    'visit_order': 4,
                    'address': {
                        'fullname': '4',
                        'coordinates': [4, 5],
                        'country': '4',
                        'city': '4',
                        'street': '4',
                        'building': '4',
                        'door_code': 'door_4',
                        'comment': 'comment_4',
                    },
                    'contact': {
                        'phone': '+79999999994',
                        'name': 'string',
                        'email': '4@yandex.ru',
                        'personal_phone_id': 'fqwerwqe',
                    },
                    'type': 'return',
                    'id': 1233312,
                    'visit_status': 'visited',
                },
            ],
            'current_point_id': 1,
            'created_ts': '3000-01-01T00:00:00+0300',
            'updated_ts': '3000-01-01T00:00:00+0300',
        }
        return data


@pytest.fixture  # noqa: F405
def user_api(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/user-api/v2/user_phones/get')
    def user_phones_get(request):
        data = {'id': '1234123421', 'personal_phone_id': 'adfqrqwerqwer'}
        return data


def main_configuration(func):
    @pytest.mark.config(  # noqa: F405
        TVM_RULES=[
            {'dst': 'cargo-claims', 'src': 'hiring-utils'},
            {'dst': 'driver-profiles', 'src': 'hiring-utils'},
            {'dst': 'personal', 'src': 'hiring-utils'},
            {'dst': 'territories', 'src': 'hiring-utils'},
            {'dst': 'user-api', 'src': 'hiring-utils'},
        ],
    )
    @pytest.mark.usefixtures(
        'personal', 'driver_profiles', 'cargo_claims', 'user_api',
    )  # noqa: F405
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


@pytest.fixture
def mock_territories_api(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }
