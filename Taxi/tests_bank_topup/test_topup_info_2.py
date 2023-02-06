import pytest

from tests_bank_topup import common


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_anon_max_limit_less_balance(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')

    headers = common.get_default_headers()
    headers.pop('X-YaBank-ColorTheme')

    params = common.make_body(handle_path, 'max_limit_less_balance')

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    cur_theme = {
        'dark': common.get_exceed_limit_widget_theme(),
        'light': common.get_exceed_limit_widget_theme(),
    }

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 0 \u20BD'
                ),
                'money': {'amount': '0', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100 \u20BD'
                ),
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [
                {
                    'action': (
                        'banksdk://events.action/'
                        'open_simplified_identification_info'
                    ),
                    'condition': {
                        'lower_limit': {'amount': '-1', 'currency': 'RUB'},
                    },
                    'title': 'На балансе максимум',
                    'description': (
                        'Перейдите на новый уровень,'
                        ' чтобы держать на счёте больше 20 \u20BD'
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


@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
async def test_anon_residue_limit(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')

    headers = common.get_default_headers()
    headers.pop('X-YaBank-ColorTheme')

    params = common.make_body(handle_path, 'remaining_less_threshold')

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    cur_theme = {
        'dark': common.get_exceed_limit_widget_theme(),
        'light': common.get_exceed_limit_widget_theme(),
    }

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 20 \u20BD'
                ),
                'money': {'amount': '20', 'currency': 'RUB'},
            },
            'min_limit': {
                'description': (
                    'Ты не можешь пополнить меньше, чем на 100 \u20BD'
                ),
                'money': {'amount': '100', 'currency': 'RUB'},
            },
            'widgets': [
                {
                    'action': (
                        'banksdk://events.action'
                        '/open_simplified_identification_info'
                    ),
                    'condition': {
                        'lower_limit': {'amount': '20', 'currency': 'RUB'},
                    },
                    'title': 'Можно внести только 20 \u20BD',
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


@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize('app_type', ['REGISTRATION', 'DIGITAL_CARD_ISSUE'])
@pytest.mark.parametrize(
    'application_id',
    [
        common.APPLICATION_ID_PROCESSING,
        common.APPLICATION_ID_FAILED,
        common.APPLICATION_ID_SUCCESS,
        common.APPLICATION_ID_CREATED,
    ],
)
async def test_anonym_application_with_inappropriate_type(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        app_type,
        application_id,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')

    headers = common.get_default_headers()
    headers.update({'X-YaBank-ColorTheme': 'SYSTEM'})

    params = common.make_body(
        handle_path, 'money_less_max_limit', application_id,
    )

    bank_applications_mock.set_application_type(app_type)

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

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
                    'action': (
                        'banksdk://events.action'
                        '/open_simplified_identification_info'
                    ),
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


@pytest.mark.parametrize(
    'app_type',
    ['REGISTRATION', 'SIMPLIFIED_IDENTIFICATION', 'DIGITAL_CARD_ISSUE'],
)
@pytest.mark.parametrize(
    'application_id',
    [
        common.APPLICATION_ID_PROCESSING,
        common.APPLICATION_ID_FAILED,
        common.APPLICATION_ID_SUCCESS,
        common.APPLICATION_ID_CREATED,
        common.APPLICATION_ID_NOEXIST,
    ],
)
@pytest.mark.parametrize(
    'auth_level', ['ANONYMOUS', 'IDENTIFIED', 'KYC', 'KYC_EDS'],
)
@pytest.mark.experiments3(filename='topup_widgets_off_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_widgets_off(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        auth_level,
        application_id,
        app_type,
        handle_path,
):
    headers = common.get_default_headers()

    params = common.make_body(
        handle_path, 'money_less_max_limit', application_id,
    )

    bank_applications_mock.set_application_type(app_type)

    bank_core_client_mock.set_auth_level(auth_level)
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
    'app_type',
    ['REGISTRATION', 'SIMPLIFIED_IDENTIFICATION', 'DIGITAL_CARD_ISSUE'],
)
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_no_buid(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        app_type,
        handle_path,
):
    headers = common.get_default_headers()
    headers.pop('X-Yandex-BUID')

    bank_applications_mock.set_application_type(app_type)

    params = common.make_body(
        handle_path, 'many_limits', common.APPLICATION_ID_SUCCESS,
    )
    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    assert response.status_code == 401


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_default_theme(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')

    headers = common.get_default_headers()
    headers.pop('X-YaBank-ColorTheme')

    params = common.make_body(handle_path, 'money_less_max_limit')

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

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
                    'action': (
                        'banksdk://events.action'
                        '/open_simplified_identification_info'
                    ),
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


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_uprid_max_limit_less_balance(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('IDENTIFIED')

    headers = common.get_default_headers()
    headers.pop('X-YaBank-ColorTheme')

    params = common.make_body(handle_path, 'max_limit_less_balance')
    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    cur_theme = {
        'dark': common.get_exceed_limit_widget_theme(need_image=False),
        'light': common.get_exceed_limit_widget_theme(need_image=False),
    }

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 0 \u20BD'
                ),
                'money': {'amount': '0', 'currency': 'RUB'},
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
                        'lower_limit': {'amount': '-1', 'currency': 'RUB'},
                    },
                    'title': 'На балансе максимум',
                    'description': (
                        'Перейдите на новый уровень, '
                        'чтобы держать на счёте больше 20 \u20BD'
                    ),
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


@pytest.mark.experiments3(filename='topup_widgets_on_experiments.json')
@pytest.mark.parametrize(
    'handle_path', [common.V1_HANDLE_PATH, common.V2_HANDLE_PATH],
)
async def test_uprid_residue_limit_uprid(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_applications_mock,
        bank_core_client_mock,
        handle_path,
):
    bank_core_client_mock.set_auth_level('IDENTIFIED')

    headers = common.get_default_headers()
    headers.pop('X-YaBank-ColorTheme')

    params = common.make_body(handle_path, 'remaining_less_threshold')

    response = await taxi_bank_topup.post(
        handle_path, headers=headers, json=params,
    )

    cur_theme = {
        'dark': common.get_exceed_limit_widget_theme(need_image=False),
        'light': common.get_exceed_limit_widget_theme(need_image=False),
    }

    expected_response = common.extend_expected_result(
        {
            'max_limit': {
                'description': (
                    'Ты не можешь пополнить больше, чем на 20 \u20BD'
                ),
                'money': {'amount': '20', 'currency': 'RUB'},
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
                        'lower_limit': {'amount': '20', 'currency': 'RUB'},
                    },
                    'title': 'Можно внести только 20 \u20BD',
                    'description': (
                        'Чтобы положить на карту больше, пройдите KYC'
                    ),
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
