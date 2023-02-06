# encoding=utf-8
import json

import pytest


PD_PHONES_DATA = [
    {'value': '+7000', 'id': 'id_+7000'},
    {'value': '+701', 'id': 'id_+701'},
    {'value': '+79217652332', 'id': 'id_+79217652332'},
    {'value': '89031234568', 'id': 'id_89031234568'},
    {'value': '+123', 'id': 'id_+123'},
    {'value': '+70004510451', 'id': 'id_+70004510451'},
    {'value': '+79104607457', 'id': 'id_+79104607457'},
    {'value': '+79575775757', 'id': 'id_+79575775757'},
    {'value': '+791612332144', 'id': 'id_+791612332144'},
    {'value': '+79163936525', 'id': 'id_+79163936525'},
    {'value': '+79217652331', 'id': 'id_+79217652331'},
    {'value': '89031234567', 'id': 'id_89031234567'},
    {'value': '+7004', 'id': 'id_+7004'},
    {'value': '+7003', 'id': 'id_+7003'},
    {'value': '+7002', 'id': 'id_+7002'},
    {'value': '+7001', 'id': 'id_+7001'},
    {'value': '+711', 'id': 'id_+711'},
    {'value': '+3811', 'id': 'id_+3811'},
    {'value': '+700', 'id': 'id_+700'},
    {'value': '+3800', 'id': 'id_+3800'},
    {'value': '+48123', 'id': 'id_+48123'},
    {'value': '+79990002244', 'id': 'id_+79990002244'},
    {'value': '+79211237321', 'id': 'id_+79211237321'},
    {'value': '89031237321', 'id': 'id_89031237321'},
]


@pytest.fixture
def mock_personal_data(mockserver):
    class PersonalDataContext:
        def __init__(self):
            self.pd_data = PD_PHONES_DATA

        def set_pd_data(self, data):
            self.pd_data = data

    context = PersonalDataContext()

    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_find(request):
        phone = json.loads(request.get_data())['value']
        pd_item = next(filter(lambda i: i['value'] == phone, context.pd_data))
        if pd_item:
            return pd_item
        else:
            return mockserver.make_response({}, 404)

    @mockserver.json_handler('/personal/v1/phones/bulk_find')
    def _phones_bulk_find(request):
        phones = set(
            [i['value'] for i in json.loads(request.get_data())['items']],
        )
        pd_items = [d for d in context.pd_data if d['value'] in phones]
        return {'items': pd_items}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        phone = json.loads(request.get_data())['id']
        pd_item = filter(lambda i: i['id'] == phone, context.pd_data)
        return next(pd_item)

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _phones_bulk_retrieve(request):
        phones = set(
            [i['id'] for i in json.loads(request.get_data())['items']],
        )
        pd_items = [d for d in context.pd_data if d['id'] in phones]
        return {'items': pd_items}

    context.phones_find = _phones_find
    context.phones_bulk_find = _phones_bulk_find
    context.phones_retrieve = _phones_retrieve
    context.phones_bulk_retrieve = _phones_bulk_retrieve

    return context


def make_bulk_store(request_body, make_id=lambda x: x):
    items = json.loads(request_body)['items']
    response_items = [
        {'id': 'id_' + make_id(i['value']), 'value': i['value']} for i in items
    ]
    return {'items': response_items}


def make_bulk_retrieve(request_body):
    items = json.loads(request_body)['items']
    # id is supposed to be of form id_<value>
    response_items = [
        {'id': i['id'], 'value': i['id'][3:]}
        for i in items
        if i['id'].startswith('id_')
    ]
    return {'items': response_items}


# driver licenses


@pytest.fixture
def personal_driver_licenses_bulk_store(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_store')
    def mock_callback(request):
        return make_bulk_store(request.get_data())

    return mock_callback


@pytest.fixture
def personal_driver_licenses_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def mock_callback(request):
        return make_bulk_retrieve(request.get_data())

    return mock_callback


# emails


@pytest.fixture
def personal_emails_bulk_store(mockserver):
    @mockserver.json_handler('/personal/v1/emails/bulk_store')
    def mock_callback(request):
        return make_bulk_store(request.get_data())

    return mock_callback


@pytest.fixture
def personal_emails_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def mock_callback(request):
        return make_bulk_retrieve(request.get_data())

    return mock_callback


# identifications


@pytest.fixture
def personal_identifications_bulk_store(mockserver):
    @mockserver.json_handler('/personal/v1/identifications/bulk_store')
    def mock_callback(request):
        return make_bulk_store(
            request.get_data(), make_id=lambda x: json.loads(x)['number'],
        )

    return mock_callback


@pytest.fixture
def personal_identifications_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/identifications/bulk_retrieve')
    def mock_callback(request):
        return make_bulk_retrieve(request.get_data())

    return mock_callback


# phones


@pytest.fixture
def personal_phones_bulk_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def mock_callback(request):
        return make_bulk_store(request.get_data())

    return mock_callback


@pytest.fixture
def personal_phones_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def mock_callback(request):
        return make_bulk_retrieve(request.get_data())

    return mock_callback


@pytest.fixture
def personal_phones_bulk_find(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_find')
    def mock_callback(request):
        return make_bulk_store(request.get_data())

    return mock_callback


# tins


@pytest.fixture
def personal_tins_bulk_store(mockserver):
    @mockserver.json_handler('/personal/v1/tins/bulk_store')
    def mock_callback(request):
        return make_bulk_store(request.get_data())

    return mock_callback


@pytest.fixture
def personal_tins_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/tins/bulk_retrieve')
    def mock_callback(request):
        return make_bulk_retrieve(request.get_data())

    return mock_callback


@pytest.fixture(autouse=True)
def personal_deptrans_ids_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/deptrans_ids/bulk_retrieve')
    def mock_callback(request):
        return make_bulk_retrieve(request.get_data())

    return mock_callback
