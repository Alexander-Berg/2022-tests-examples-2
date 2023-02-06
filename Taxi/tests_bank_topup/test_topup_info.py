# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_topup_plugins.generated_tests import *
from tests_bank_topup import common

import pytest


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
@pytest.mark.parametrize(
    'locale, min_limit, max_limit, fee_message',
    [
        (
            'ru',
            'Ты не можешь пополнить меньше, чем на 100 \u20BD',
            'Ты не можешь пополнить больше, чем на 10,1 \u20BD',
            'Без комиссии',
        ),
        (
            'en',
            'You can not top up less then \u20BD 100',
            'You can not top up more then \u20BD 10.1',
            'No fee',
        ),
        (
            'unknown',
            'Ты не можешь пополнить меньше, чем на 100 \u20BD',
            'Ты не можешь пополнить больше, чем на 10,1 \u20BD',
            'Без комиссии',
        ),
        (
            'unknown_key',
            'Ты не можешь пополнить меньше, чем на 100 \u20BD',
            'Ты не можешь пополнить больше, чем на 10.1 \u20BD',
            'Без комиссии',
        ),
    ],
)
@pytest.mark.experiments3(filename='topup_info_experiments.json')
async def test_many_limits(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        locale,
        min_limit,
        max_limit,
        fee_message,
        handle_path,
):
    headers = common.get_default_headers()
    headers.update({'X-Request-Language': locale})
    params = common.make_body(
        handle_path, 'many_limits', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = (
        common.extend_expected_result(
            {
                'max_limit': {
                    'description': max_limit,
                    'money': {'amount': '10.1', 'currency': 'RUB'},
                },
                'min_limit': {
                    'description': min_limit,
                    'money': {'amount': '100', 'currency': 'RUB'},
                },
                'widgets': [],
                'fee_message': fee_message,
            },
            handle_path,
        )
        if locale != 'unknown_key'
        else {'code': '500', 'message': 'Internal Server Error'}
    )

    code = 200 if locale != 'unknown_key' else 500
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        code,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.experiments3(filename='topup_info_no_tanker_key_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_no_tanker_key(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'many_limits', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 10,1 \u20BD'
                ),
                'money': {'amount': '10.1', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': '',
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [],
            'fee_message': 'Без комиссии',
        },
        handle_path,
    )

    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_info_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_no_wallets(
        taxi_bank_topup, bank_core_statement_mock, handle_path,
):
    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'bad_id', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    if handle_path == common.V1_HANDLE_PATH:
        assert bank_core_statement_mock.wallets_balance_handler.has_calls
    elif handle_path == common.V2_HANDLE_PATH:
        assert bank_core_statement_mock.agreements_balance_handler.has_calls
    assert response.status_code == 404


@pytest.mark.experiments3(filename='topup_info_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_no_uid(taxi_bank_topup, bank_core_statement_mock, handle_path):
    headers = common.get_default_headers()
    headers.pop('X-Yandex-UID')

    params = common.make_body(
        handle_path,
        'f0180a66-a339-497e-9572-130f440cc338',
        common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    assert response.status_code == 401
    assert not bank_core_statement_mock.wallets_balance_handler.has_calls
    assert not bank_core_statement_mock.agreements_balance_handler.has_calls


@pytest.mark.config(BANK_TOPUP_WALLET_MIN_LIMITS={})
@pytest.mark.experiments3(filename='topup_info_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_no_limits(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        handle_path,
):
    headers = common.get_default_headers()
    params = common.make_body(
        handle_path, 'no_limits', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {'fee_message': 'Без комиссии'}, handle_path,
    )

    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_info_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_different_wallet_ids(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        handle_path,
):
    headers = common.get_default_headers()

    params = common.make_body(handle_path, 'different_id')

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = {'code': '500', 'message': 'Internal Server Error'}

    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        500,
        handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_no_topup_info_experiments(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'many_limits', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 10,1 \u20BD'
                ),
                'money': {'amount': '10.1', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100 \u20BD'
                ),
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [],
            'fee_message': 'Без комиссии',
        },
        handle_path,
    )
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'code_like_number,status',
    [(400, 500), (401, 500), (404, 404), (429, 429), (500, 500)],
)
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_code_of_exceptions(
        taxi_bank_topup,
        bank_core_statement_mock,
        code_like_number,
        status,
        handle_path,
):
    headers = common.get_default_headers()

    params = common.make_body(handle_path, 'check_status')

    bank_core_statement_mock.set_http_status_code(code_like_number)

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    assert response.status_code == status


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_anonym_no_application(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')

    headers = common.get_default_headers()

    params = common.make_body(handle_path, 'money_less_max_limit')

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 5 \u20BD'
                ),
                'money': {'amount': '5', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100 \u20BD'
                ),
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [
                {
                    'action': 'banksdk://events.action/open_simplified_identification_info',
                    'condition': {
                        'lower_limit': {'amount': '5', 'currency': 'RUB'},
                    },
                    'title': 'Можно внести только 5 \u20BD',
                    'description': (
                        'Чтобы положить на карту больше, подтвердите личность'
                    ),
                    'button': {'text': 'Как подтвердить?'},
                    'widget_type': 'LIMIT',
                    'themes': {
                        'light': {
                            'background': {'color': 'FFFFF0E0'},
                            'title_text_color': 'FFA15912',
                            'description_text_color': 'FFA15912',
                            'delimiter_color': 'FF98591B',
                            'button_theme': {
                                'background': {'color': 'FFFFF0E0'},
                                'text_color': 'FFA15912',
                            },
                            'image': {
                                'size_type': 'TITLE',
                                'url': 'https://avatars.mdst.yandex.net/get-fintech/0000000/limit_png',
                            },
                        },
                    },
                },
            ],
            'fee_message': 'Без комиссии',
        },
        handle_path,
    )
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_anonym_application_failed(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')
    bank_applications_mock.set_application_type('SIMPLIFIED_IDENTIFICATION')

    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'money_less_max_limit', common.APPLICATION_ID_FAILED,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 5 \u20BD'
                ),
                'money': {'amount': '5', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100 \u20BD'
                ),
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [
                {
                    'action': 'banksdk://events.action/open_simplified_identification_form',
                    'condition': {
                        'lower_limit': {'amount': '5', 'currency': 'RUB'},
                    },
                    'title': 'Паспорт не проверен',
                    'description': 'Поищите ошибку в данных. А пока можете внести до 20 \u20BD',
                    'widget_type': 'LIMIT',
                    'themes': {
                        'light': {
                            'background': {'color': 'FFFFEBEB'},
                            'title_text_color': 'FFE23636',
                            'description_text_color': 'FFE23636',
                            'image': {
                                'size_type': 'BACKGROUND',
                                'url': 'https://avatars.mdst.yandex.net/get-fintech/1401668/eagle_mistake_png',
                            },
                        },
                    },
                },
            ],
            'fee_message': 'Без комиссии',
        },
        handle_path,
    )
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_anonym_application_progressing(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')
    bank_applications_mock.set_application_type('SIMPLIFIED_IDENTIFICATION')

    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'money_less_max_limit', common.APPLICATION_ID_PROCESSING,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 5 \u20BD'
                ),
                'money': {'amount': '5', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100 \u20BD'
                ),
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [
                {
                    'condition': {
                        'lower_limit': {'amount': '5', 'currency': 'RUB'},
                    },
                    'title': 'Проверяем паспорт',
                    'description': 'Скажем, когда закончим. а пока вы можете внести до 20 \u20BD',
                    'widget_type': 'LIMIT',
                    'themes': {
                        'light': {
                            'background': {'color': 'FFF4F6F7'},
                            'title_text_color': 'FF000000',
                            'description_text_color': 'FF000000',
                            'image': {
                                'size_type': 'BACKGROUND',
                                'url': 'https://avatars.mdst.yandex.net/get-fintech/1401668/eagle_processing_png',
                            },
                        },
                    },
                },
            ],
            'fee_message': 'Без комиссии',
        },
        handle_path,
    )
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_uprid_application_success(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_applications_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('IDENTIFIED')
    bank_applications_mock.set_application_type('SIMPLIFIED_IDENTIFICATION')

    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'money_less_max_limit', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {
            'min_limit': {
                'money': {'amount': '100', 'currency': 'RUB'},
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100\xa0₽'
                ),
            },
            'max_limit': {
                'money': {'amount': '5', 'currency': 'RUB'},
                'description': 'Ты не можешь пополнить больше, чем на 5\xa0₽',
            },
            'fee_message': 'Без комиссии',
            'widgets': [
                {
                    'condition': {
                        'lower_limit': {'amount': '5', 'currency': 'RUB'},
                    },
                    'title': 'Можно внести только 5\xa0₽',
                    'description': (
                        'Чтобы положить на карту больше, пройдите KYC'
                    ),
                    'themes': {
                        'light': common.get_exceed_limit_widget_theme(
                            need_image=False,
                        ),
                    },
                    'widget_type': 'LIMIT',
                },
                {
                    'condition': {
                        'lower_limit': {'amount': '-1', 'currency': 'RUB'},
                        'upper_limit': {'amount': '5', 'currency': 'RUB'},
                    },
                    'title': 'Паспорт проверен',
                    'description': 'Теперь вы можете держать на счете до 20\xa0₽ и переводить деньги',
                    'themes': {
                        'light': {
                            'background': {'color': 'FFE2F7E9'},
                            'title_text_color': 'FF268C4C',
                            'description_text_color': 'FF268C4C',
                            'image': {
                                'size_type': 'BACKGROUND',
                                'url': 'https://avatars.mdst.yandex.net/get-fintech/65575/eagle_checked_png',
                            },
                        },
                    },
                    'widget_type': 'INFO',
                },
            ],
        },
        handle_path,
    )
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_uprid_no_application(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('IDENTIFIED')

    headers = common.get_default_headers()

    params = common.make_body(handle_path, 'money_less_max_limit')

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = common.extend_expected_result(
        {
            'min_limit': {
                'money': {'amount': '100', 'currency': 'RUB'},
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100\xa0₽'
                ),
            },
            'max_limit': {
                'money': {'amount': '5', 'currency': 'RUB'},
                'description': 'Ты не можешь пополнить больше, чем на 5\xa0₽',
            },
            'fee_message': 'Без комиссии',
            'widgets': [
                {
                    'condition': {
                        'lower_limit': {'amount': '5', 'currency': 'RUB'},
                    },
                    'title': 'Можно внести только 5\xa0₽',
                    'description': (
                        'Чтобы положить на карту больше, пройдите KYC'
                    ),
                    'themes': {
                        'light': common.get_exceed_limit_widget_theme(
                            need_image=False,
                        ),
                    },
                    'widget_type': 'LIMIT',
                },
            ],
        },
        handle_path,
    )

    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize('auth_level', ['ANONYMOUS', 'IDENTIFIED'])
@pytest.mark.parametrize(
    'code_like_number, status, code, message',
    [(404, 404, 'NotFound', 'Application not found')],
)
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_cannot_find_application(
        taxi_bank_topup,
        bank_core_statement_mock,
        mockserver,
        bank_applications_mock,
        code,
        message,
        code_like_number,
        status,
        auth_level,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level(auth_level)
    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'money_less_max_limit', common.APPLICATION_ID_NOEXIST,
    )

    bank_applications_mock.set_http_status_code(code_like_number)
    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = {'code': code, 'message': message}
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        status,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_no_client_info(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    headers = common.get_default_headers()
    headers.update({'X-Yandex-BUID': 'bad_buid'})

    params = common.make_body(
        handle_path, 'many_limits', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    expected_response = {'code': 'NotFound', 'message': 'Client not found'}

    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        404,
        handle_path=handle_path,
    )


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize('color_theme', ['DARK', 'LIGHT', 'SYSTEM'])
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_themes(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        color_theme,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')

    headers = common.get_default_headers()
    headers.update({'X-YaBank-ColorTheme': color_theme})

    params = common.make_body(
        handle_path, 'money_less_max_limit', common.APPLICATION_ID_SUCCESS,
    )

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )
    cur_theme = {'light': common.get_exceed_limit_widget_theme()}
    if color_theme == 'DARK':
        cur_theme = {'dark': common.get_exceed_limit_widget_theme()}
    elif color_theme == 'SYSTEM':
        cur_theme = {
            'dark': common.get_exceed_limit_widget_theme(),
            'light': common.get_exceed_limit_widget_theme(),
        }

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 5 \u20BD'
                ),
                'money': {'amount': '5', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100 \u20BD'
                ),
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [
                {
                    'action': 'banksdk://events.action/open_simplified_identification_info',
                    'condition': {
                        'lower_limit': {'amount': '5', 'currency': 'RUB'},
                    },
                    'title': 'Можно внести только 5 \u20BD',
                    'description': (
                        'Чтобы положить на карту больше, подтвердите личность'
                    ),
                    'button': {'text': 'Как подтвердить?'},
                    'widget_type': 'LIMIT',
                    'themes': cur_theme,
                },
            ],
            'fee_message': 'Без комиссии',
        },
        handle_path,
    )
    common.make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        handle_path=handle_path,
    )
