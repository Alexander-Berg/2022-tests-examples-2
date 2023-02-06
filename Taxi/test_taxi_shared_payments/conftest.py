# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
from datetime import datetime

import aiohttp.web
import pytest

import taxi_shared_payments.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_shared_payments.generated.service.pytest_plugins']

DEFAULT_HEADERS = {
    'Accept-Language': 'ru',
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': '_id1',
    'X-YaTaxi-PhoneId': '00aaaaaaaaaaaaaaaaaaaa01',
    'X-Yandex-Login': 'test',
    'X-Remote-IP': 'amazing_ip',
}


@pytest.fixture
def mock_personal_api(mockserver):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id'][3:]}

    @mockserver.json_handler('/personal/v1/emails/store')
    def _store(request):
        return {
            'id': f'id-{request.json["value"]}',
            'value': request.json['value'],
        }


@pytest.fixture
def mock_user_api(mockserver, load_json):
    @mockserver.json_handler('/user_api-api/user_phones/get')
    def _get_user_phone(request):
        return load_json('user_phones.json')[request.json['id']]

    @mockserver.json_handler('/user_api-api/user_phones/by_number/retrieve')
    def _get_user_phone_id(request):
        return load_json('user_phones_by_phone.json').get(
            request.json['phone'], aiohttp.web.json_response(status=404),
        )

    @mockserver.json_handler('/user_api-api/user_phones/get_bulk')
    def _get_user_phones_bulk(request):
        user_phones = load_json('user_phones.json')
        return {
            'items': [
                user_phones[ph_id]
                for ph_id in request.json['ids']
                if ph_id in user_phones
            ],
        }

    @mockserver.json_handler('/user_api-api/users/get')
    def _get_user(request):
        return load_json('users.json')[request.json['id']]


@pytest.fixture
def mock_cardstorage_api(mock_cardstorage, load_json):
    @mock_cardstorage('/v1/card')
    def _mock_payment_method(request, **kwargs):
        assert request.method == 'POST'
        assert 'yandex_uid' in request.json
        assert 'card_id' in request.json
        all_cards = load_json('cardstorage_all.json')
        for card in all_cards['available_cards']:
            if (
                    card['card_id'] == request.json['card_id']
                    and card['owner'] == request.json['yandex_uid']
            ):
                return card
        return aiohttp.web.json_response(
            status=404, data={'code': '404', 'message': 'Card not found'},
        )


@pytest.fixture
def mock_antifraud_api(mock_antifraud):
    @mock_antifraud('/v1/currency/convert')
    def _mock_convert(request, **kwargs):
        return {'value': 1.50}


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
                {
                    '_id': 'est',
                    'national_access_code': '372',
                    'phone_code': '372',
                    'phone_max_length': 11,
                    'phone_min_length': 10,
                },
            ],
        }


@pytest.fixture
def mock_all_api(
        mock_antifraud_api,
        mock_cardstorage_api,
        mock_personal_api,
        mock_territories_api,
        mock_user_api,
):
    pass


@pytest.fixture
def create_member_exception(patch):
    @patch('taxi_shared_payments.repositories.members.create')
    async def _raise_exception(*args, **kwargs):
        raise ValueError('just mocking a db failure')


@pytest.fixture(scope='function')
def family_card(request):
    from taxi_shared_payments.common import models
    return models.Card(
        owner_uid='payment.owner',
        number='payment.number',
        billing_id='payment.billing_card_id',
        payment_id='payment.card_id',
        persistent_id='payment.persistent_id',
        valid=True,
        unbound=False,
        expiration_date=datetime.now(),
        currency='payment.currency',
        payment_system='payment.system',
        family_info=models.FamilyInfo(
            is_owner=True,
            currency='RUB',
            expenses=5000,
            limit=10000,
            frame='frame',
        ),
    )
