# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_wallet_plugins.generated_tests import *

import pytest
import copy

WALLETS_INFO_PATH = '/v1/wallet/v1/get_wallets_info'
CARDS_INFO_PATH = '/v1/wallet/v1/get_cards_info'
WALLET_PROMO_PATH = '/v1/wallet/v1/get_wallet_promo'

DEFAULT_HEADERS = {
    'X-Yandex-BUID': 'bad_buid',
    'X-YaBank-SessionUUID': '1',
    'X-Yandex-UID': '1',
    'X-Request-Language': 'ru',
    'X-YaBank-PhoneID': '1',
    'X-Ya-User-Ticket': '1',
}

DEFAULT_BANK_WALLET_INFO_CONFIG = {
    'wallet_info': {
        'image': '',
        'subtitle': 'Повышенный кешбек в сервисах Яндекса',
        'title': 'Карта Яндекса',
    },
    'unauthorized_info': {
        'image': '',
        'subtitle': 'Повышенный кешбек в сервисах Яндекса',
        'title': 'Пройди авторизацию',
    },
}


def _remove_wallet_ids(resp):
    for wallet in resp:
        wallet.pop('wallet_id')


def make_checks(
        api_core_banking_mock,
        expected_response,
        response,
        status_code: int = 200,
):
    assert response.status_code == status_code
    assert api_core_banking_mock.wallets_balance2_handler.has_calls
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'handle_path, root_field',
    [(WALLETS_INFO_PATH, 'wallets_info'), (CARDS_INFO_PATH, 'cards_info')],
)
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
@pytest.mark.experiments3()
async def test_bad_buid(
        taxi_bank_wallet, bank_core_statement_mock, handle_path, root_field,
):
    response = await taxi_bank_wallet.post(
        handle_path, headers=DEFAULT_HEADERS,
    )

    expected_response = {root_field: []}

    make_checks(bank_core_statement_mock, expected_response, response, 200)


@pytest.mark.parametrize(
    'handle_path, root_field',
    [(WALLETS_INFO_PATH, 'wallets_info'), (CARDS_INFO_PATH, 'cards_info')],
)
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
@pytest.mark.experiments3()
async def test_many_wallets(
        taxi_bank_wallet, bank_core_statement_mock, handle_path, root_field,
):
    headers = copy.copy(DEFAULT_HEADERS)
    headers['X-Yandex-BUID'] = 'many_wallets'

    response = await taxi_bank_wallet.post(handle_path, headers=headers)

    expected_response = {
        root_field: [
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
                'subtitle': 'Баланс: 10 000 \u20BD',
                'title': 'Кошелек',
                'payment_method_id': 'method1',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
                'subtitle': 'Баланс: 10\xa0000\xa0₽',
                'title': 'Кошелек',
                'payment_method_id': 'method2',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'payment_method_id': 'method1',
                'subtitle': 'Баланс: 0\xa0₽',
                'title': 'Кошелек',
                'wallet_id': 'f0180000-a339-497e-9572-130f440cc338',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'payment_method_id': 'method2',
                'subtitle': 'Баланс: 0\xa0₽',
                'title': 'Кошелек',
                'wallet_id': 'f0180000-a339-497e-9572-130f440cc338',
            },
        ],
    }
    if handle_path == CARDS_INFO_PATH:
        _remove_wallet_ids(expected_response[root_field])

    make_checks(bank_core_statement_mock, expected_response, response, 200)


@pytest.mark.parametrize(
    'handle_path, root_field',
    [(WALLETS_INFO_PATH, 'wallets_info'), (CARDS_INFO_PATH, 'cards_info')],
)
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
async def test_many_wallets_no_experiments(
        taxi_bank_wallet, bank_core_statement_mock, handle_path, root_field,
):
    headers = copy.copy(DEFAULT_HEADERS)
    headers['X-Yandex-BUID'] = 'many_wallets'

    response = await taxi_bank_wallet.post(handle_path, headers=headers)

    expected_response = {
        root_field: [
            {
                'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'subtitle': 'Повышенный кешбек в сервисах Яндекса',
                'title': 'Карта Яндекса',
                'payment_method_id': 'method1',
            },
            {
                'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'subtitle': 'Повышенный кешбек в сервисах Яндекса',
                'title': 'Карта Яндекса',
                'payment_method_id': 'method2',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'payment_method_id': 'method1',
                'subtitle': 'Повышенный кешбек в сервисах Яндекса',
                'title': 'Карта Яндекса',
                'wallet_id': 'f0180000-a339-497e-9572-130f440cc338',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'payment_method_id': 'method2',
                'subtitle': 'Повышенный кешбек в сервисах Яндекса',
                'title': 'Карта Яндекса',
                'wallet_id': 'f0180000-a339-497e-9572-130f440cc338',
            },
        ],
    }
    if handle_path == CARDS_INFO_PATH:
        _remove_wallet_ids(expected_response[root_field])

    make_checks(bank_core_statement_mock, expected_response, response, 200)


@pytest.mark.parametrize('handle_path', [WALLETS_INFO_PATH, WALLET_PROMO_PATH])
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
async def test_no_authorized_no_experiments(taxi_bank_wallet, handle_path):
    headers = {'X-YaBank-SessionUUID': '1', 'X-Request-Language': 'ru'}

    response = await taxi_bank_wallet.post(handle_path, headers=headers)

    expected_response = {
        'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_unauthorized/',
        'subtitle': 'Повышенный кешбек в сервисах Яндекса',
        'title': 'Пройди авторизацию',
    }
    if handle_path == WALLETS_INFO_PATH:
        expected_response = {'wallets_info': [expected_response.copy()]}

    assert response.json() == expected_response
    assert response.status_code == 200


@pytest.mark.parametrize('handle_path', [WALLETS_INFO_PATH, WALLET_PROMO_PATH])
@pytest.mark.parametrize(
    'header', ['X-Yandex-BUID', 'X-Yandex-UID', 'X-YaBank-PhoneID'],
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
async def test_no_authorized(taxi_bank_wallet, header, handle_path):
    headers = copy.copy(DEFAULT_HEADERS)
    headers['X-Yandex-BUID'] = 'many_wallets'
    headers.pop(header)

    response = await taxi_bank_wallet.post(handle_path, headers=headers)

    expected_response = {
        'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_unauthorized/',
        'subtitle': 'Пройдите авторизацию!',
        'title': 'Не зарегистрирован',
    }
    if handle_path == WALLETS_INFO_PATH:
        expected_response = {'wallets_info': [expected_response.copy()]}

    assert response.json() == expected_response
    assert response.status_code == 200


@pytest.mark.parametrize('handle_path', [WALLETS_INFO_PATH, WALLET_PROMO_PATH])
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
async def test_no_authorized_by_authproxy(taxi_bank_wallet, handle_path):
    headers = copy.copy(DEFAULT_HEADERS)
    headers['X-Yandex-BUID'] = 'many_wallets'
    headers['X-YaBank-AuthorizedByAuthproxy'] = 'no'

    response = await taxi_bank_wallet.post(handle_path, headers=headers)

    expected_response = {
        'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_unauthorized/',
        'subtitle': 'Пройдите авторизацию!',
        'title': 'Не зарегистрирован',
    }
    if handle_path == WALLETS_INFO_PATH:
        expected_response = {'wallets_info': [expected_response.copy()]}

    assert response.json() == expected_response
    assert response.status_code == 200


@pytest.mark.parametrize('handle_path', [WALLETS_INFO_PATH, WALLET_PROMO_PATH])
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
async def test_no_session_uuid(taxi_bank_wallet, handle_path):
    headers = copy.copy(DEFAULT_HEADERS)
    headers['X-Yandex-BUID'] = 'many_wallets'
    headers.pop('X-YaBank-SessionUUID')

    response = await taxi_bank_wallet.post(handle_path, headers=headers)

    expected_response = {'code': '401', 'message': 'No session uuid'}

    assert response.json() == expected_response
    assert response.status_code == 401


@pytest.mark.parametrize(
    'handle_path, root_field',
    [(WALLETS_INFO_PATH, 'wallets_info'), (CARDS_INFO_PATH, 'cards_info')],
)
@pytest.mark.parametrize('header', ['X-Yandex-UID', 'X-YaBank-PhoneID'])
@pytest.mark.experiments3(filename='experiments3_defaults.json')
@pytest.mark.config(BANK_WALLET_INFO=DEFAULT_BANK_WALLET_INFO_CONFIG)
async def test_authorized_by_authproxy(
        taxi_bank_wallet,
        bank_core_statement_mock,
        header,
        handle_path,
        root_field,
):
    headers = copy.copy(DEFAULT_HEADERS)
    headers['X-Yandex-BUID'] = 'many_wallets'
    headers['X-YaBank-AuthorizedByAuthproxy'] = 'yes'
    headers.pop(header)

    response = await taxi_bank_wallet.post(handle_path, headers=headers)

    expected_response = {
        root_field: [
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
                'subtitle': 'Баланс: 10 000 \u20BD',
                'title': 'Кошелек',
                'payment_method_id': 'method1',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'wallet_id': 'f0180a66-a339-497e-9572-130f440cc338',
                'subtitle': 'Баланс: 10\xa0000\xa0₽',
                'title': 'Кошелек',
                'payment_method_id': 'method2',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'payment_method_id': 'method1',
                'subtitle': 'Баланс: 0\xa0₽',
                'title': 'Кошелек',
                'wallet_id': 'f0180000-a339-497e-9572-130f440cc338',
            },
            {
                'image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/card_authorized/',
                'payment_method_id': 'method2',
                'subtitle': 'Баланс: 0\xa0₽',
                'title': 'Кошелек',
                'wallet_id': 'f0180000-a339-497e-9572-130f440cc338',
            },
        ],
    }
    if handle_path == CARDS_INFO_PATH:
        _remove_wallet_ids(expected_response[root_field])

    assert response.status_code == 200
    assert response.json() == expected_response
