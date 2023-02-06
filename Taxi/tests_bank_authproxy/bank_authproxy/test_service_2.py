import pytest

# pylint: disable=C5521
from .test_service import BB_PHONES
from .test_service import CONFIG
from .test_service import PHONE_NUMBER
from .test_service import PHONE_NUMBER_ID
from .test_service import STAFF_LOGIN
from .test_service import USER_TICKET


APPLICATION_RULES = {
    'rules': [
        {
            '@app_name': 'bank_app',
            'actions': ['#bank_version', '#bank_platform_simple'],
            'match': '^(?:com|ru)\\.yandex\\.bank/',
        },
        {
            '@app_name': 'bank_app_inhouse',
            'actions': ['#bank_version', '#bank_platform_simple'],
            'match': '^(?:com|ru)\\.yandex\\.bank\\.inhouse/',
        },
        {
            '@app_name': 'yandex_go_inhouse',
            'actions': [
                '#ios_ver',
                '#ytaxi_ver',
                '#build',
                '#bank_sdk_version',
                '#bank_platform_simple',
            ],
            'match': (
                '^(?:yandex-taxi|ru\\.yandex\\.ytaxi|ru'
                '\\.yandex\\.taxi)\\.inhouse/.+darwin'
            ),
        },
        {
            '@app_name': 'yandex_go',
            'actions': [
                '#ios_ver',
                '#ytaxi_ver',
                '#build',
                '#bank_sdk_version',
                '#bank_platform_simple',
            ],
            'match': (
                '^(?:yandex-taxi/|'
                'ru\\.yandex\\.ytaxi/|ru\\.yandex\\.taxi/).+darwin'
            ),
        },
        {
            '@app_name': 'yandex_go',
            'actions': [
                '#android_ver',
                '#ytaxi_ver',
                '#build',
                '#bank_sdk_version',
                '#bank_platform_simple',
            ],
            'match': (
                '^(?:yandex-taxi/|'
                'ru\\.yandex\\.ytaxi/|ru\\.yandex\\.taxi/).+android'
            ),
        },
        {
            '@app_name': 'sdk_example',
            'actions': ['#bank_platform_simple'],
            'match': '^YandexBankSdk TestApp.+\\(android\\)$',
        },
        {
            '@app_name': 'sdk_example',
            'actions': [
                '#app_version',
                '#bank_sdk_version',
                '#bank_platform_simple',
            ],
            'match': (
                '^(?:com|ru)\\.yandex\\.fintech\\' '.YXFintechWalletExampleApp'
            ),
        },
        {
            '@app_name': 'sdk_example',
            'actions': [
                '#app_version',
                '#bank_sdk_version',
                '#bank_platform_simple',
            ],
            'match': '^(?:com|ru)\\.yandex\\' '.fintech\\.wallettestapp',
        },
        {'@app_name': 'unknown'},
    ],
    'subrules': [
        {
            '@bank_sdk': 'true',
            '@sdk_ver1': '{1}',
            '@sdk_ver2': '{2}',
            '@sdk_ver3': '{3}',
            '@sdk_ver4': '{4}',
            '@sdk_ver5': '{5}',
            'match': (
                ' bank-sdk/(\\d+)\\.(\\d+)'
                '(?:\\.(\\d+))?(?:\\.(\\d+))?(?:\\.(\\d+))?'
            ),
            'name': '#bank_sdk_version',
        },
        {
            '@app_ver1': '{1}',
            '@app_ver2': '{2}',
            '@app_ver3': '{3}',
            '@app_ver4': '{4}',
            '@app_ver5': '{5}',
            '@bank_sdk': 'false',
            'match': (
                'bank(?:\\.inhouse)?/(\\d+)\\.(\\d+)'
                '(?:\\.(\\d+))?(?:\\.(\\d+))?(?:\\.(\\d+))?'
            ),
            'name': '#bank_version',
        },
        {
            '@app_ver1': '{1}',
            '@app_ver2': '{2}',
            '@app_ver3': '{3}',
            '@app_ver4': '{4}',
            '@app_ver5': '{5}',
            'match': (
                '^[a-zA-Z.]+/(\\d+)\\.(\\d+)'
                '(?:\\.(\\d+))?(?:\\.(\\d+))?(?:\\.(\\d+))?'
            ),
            'name': '#app_version',
        },
        {
            '@platform': '{1}',
            'match': '\\((ios|android)\\)$',
            'name': '#bank_platform_simple',
        },
        {
            '@device_make': 'apple',
            'any': [
                {
                    '@device_model': '{1}{2}.{3}',
                    '@platform_ver1': '{4}',
                    '@platform_ver2': '{5}',
                    '@platform_ver3': '{6}',
                    'match': (
                        '; ([^\\d]+)(\\d+)\\,'
                        '(\\d+); ios (\\d+)(?:\\.(\\d+))?(?:\\.(\\d+))?'
                    ),
                },
                {
                    '@platform_ver1': '{1}',
                    '@platform_ver2': '{2}',
                    '@platform_ver3': '{3}',
                    'match': 'ios (\\d+)(?:\\.(\\d+))?(?:\\.(\\d+))?',
                },
                {
                    '@platform_ver1': '{1}',
                    '@platform_ver2': '{2}',
                    '@platform_ver3': '{3}',
                    'match': (
                        'iphone os (\\d+)(?:[_\\.](\\d+))?(?:[_\\.](\\d+))?'
                    ),
                },
            ],
            'name': '#ios_ver',
        },
        {
            '@device_make': '{4}',
            '@device_model': '{5}',
            '@platform_ver1': '{1}',
            '@platform_ver2': '{2}',
            '@platform_ver3': '{3}',
            'match': (
                'android/(\\d+)(?:\\.(\\d+))?(?:\\.(\\d+))?'
                '(?:\\s+\\(([^\\);\\,=]*);\\s*([^\\)\\,=]*)\\))?'
            ),
            'name': '#android_ver',
        },
        {
            '@app_ver1': '{1}',
            '@app_ver2': '{2}',
            '@app_ver3': '{3}',
            'match': '(?:taxi)(?:\\.\\w+)?/(\\d+)\\.(\\d+)\\.(\\d+)',
            'name': '#ytaxi_ver',
        },
        {
            'any': [
                {'@app_build': 'alpha', 'match': '\\.alpha/'},
                {'@app_build': 'beta', 'match': '\\.beta/'},
                {'@app_build': 'release'},
            ],
            'name': '#build',
        },
    ],
}


@pytest.mark.config(
    BANK_AUTHPROXY_ROUTE_RULES=CONFIG,
    APPLICATION_DETECTION_RULES_NEW=APPLICATION_RULES,
)
@pytest.mark.parametrize(
    'user_agent, expected_app_vars',
    [
        (
            'ru.yandex.taxi.inhouse/650.25.0.189678 (iPhone; '
            'iPhone13,2; iOS 15.1.1; Darwin) bank-sdk/0.12.0 (ios)',
            'app_brand=yataxi,'
            'app_build=release,'
            'app_name=yandex_go_inhouse,'
            'app_ver1=650,'
            'app_ver2=25,'
            'app_ver3=0,'
            'bank_sdk=true,'
            'device_make=apple,'
            'device_model=iphone13.2,'
            'platform=ios,'
            'platform_ver1=15,'
            'platform_ver2=1,'
            'platform_ver3=1,'
            'sdk_ver1=0,'
            'sdk_ver2=12,'
            'sdk_ver3=0',
        ),
        (
            'ru.yandex.taxi/650.25.0.189678 (iPhone; iPhone13,2; '
            'iOS 15.1.1; Darwin) bank-sdk/0.12.0 (ios)',
            'app_brand=yataxi,'
            'app_build=release,'
            'app_name=yandex_go,'
            'app_ver1=650,'
            'app_ver2=25,'
            'app_ver3=0,'
            'bank_sdk=true,'
            'device_make=apple,'
            'device_model=iphone13.2,'
            'platform=ios,'
            'platform_ver1=15,'
            'platform_ver2=1,'
            'platform_ver3=1,'
            'sdk_ver1=0,'
            'sdk_ver2=12,'
            'sdk_ver3=0',
        ),
        (
            'com.yandex.bank/1.0.0.125 (ios)',
            'app_brand=yataxi,'
            'app_name=bank_app,'
            'app_ver1=1,'
            'app_ver2=0,'
            'app_ver3=0,'
            'app_ver4=125,'
            'bank_sdk=false,'
            'platform=ios',
        ),
        (
            'com.yandex.bank/1.0.0.125 (android)',
            'app_brand=yataxi,'
            'app_name=bank_app,'
            'app_ver1=1,'
            'app_ver2=0,'
            'app_ver3=0,'
            'app_ver4=125,'
            'bank_sdk=false,'
            'platform=android',
        ),
        (
            'com.yandex.bank.inhouse/1.0.0.125 (ios)',
            'app_brand=yataxi,'
            'app_name=bank_app_inhouse,'
            'app_ver1=1,'
            'app_ver2=0,'
            'app_ver3=0,'
            'app_ver4=125,'
            'bank_sdk=false,'
            'platform=ios',
        ),
        (
            'ru.yandex.fintech.YXFintechWalletExampleApp.debug/'
            '1.0.0.125 (ios) bank-sdk/0.12.0 (ios)',
            'app_brand=yataxi,'
            'app_name=sdk_example,'
            'app_ver1=1,'
            'app_ver2=0,'
            'app_ver3=0,'
            'app_ver4=125,'
            'bank_sdk=true,'
            'platform=ios,'
            'sdk_ver1=0,'
            'sdk_ver2=12,'
            'sdk_ver3=0',
        ),
        (
            'YandexBankSdk TestApp/0.15.0 bank-sdk/0.15.0 (android)',
            'app_brand=yataxi,app_name=sdk_example,platform=android',
        ),
        (
            'ru.yandex.fintech.wallettestapp/0.15.0 bank-sdk/0.15.0 (android)',
            'app_brand=yataxi,'
            'app_name=sdk_example,'
            'app_ver1=0,'
            'app_ver2=15,'
            'app_ver3=0,'
            'bank_sdk=true,'
            'platform=android,'
            'sdk_ver1=0,'
            'sdk_ver2=15,'
            'sdk_ver3=0',
        ),
    ],
)
async def test_correct_user_agent_parsing(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        user_agent,
        expected_app_vars,
):
    backend = mock_remote('/abc')
    token = 'token'
    headers = {
        'X-YaBank-SessionUUID': '123',
        'User-Agent': user_agent,
        'Accept-Language': 'en',
        'Authorization': 'Bearer ' + token,
    }
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-Yandex-BUID'] == '123'
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert headers['X-Request-Language'] == 'en'
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    # Compare ignoring key-value pair order
    assert set(headers['X-Request-Application'].split(',')) == set(
        expected_app_vars.split(','),
    )
    assert response.status_code == 200
