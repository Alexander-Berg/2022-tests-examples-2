import enum

from aiohttp import web
import pytest

from payments_eda import consts as service_consts
from payments_eda.utils import experiments

PAYMENT_INFO = {
    'currency': 'RUB',
    'description': 'оплата бейджиком',
    'id': 'badge:yandex_badge:RUB',
    'name': 'Yandex Badge',
    'type': 'corp',
}

DESTINATION_POINT = [37.561912536621094, 55.42511704917208]
DESTINATION_POINT2 = [30.561912536621094, 50.42511704917208]
YANDEX_UID = 'uid'
PHONE_ID = 'phone_id'
PERSONAL_PHONE_ID = 'personal_phone_id'
REQUEST_APPLICATION_HEADER = (
    'app_name=android,app_brand=yataxi,app_ver1=1,app_ver2=2,app_ver3=3'
)


class BadgeDisabledReason(enum.Enum):
    EMPTY = ''
    TECHNICAL_ISSUE = 'технические проблемы, попробуйте чуть позже'
    NOT_FOUND_LOGIN_REASON = 'не найдена связь со стафф-аккаунтом'
    PAYER_INFO_ERROR = 'ошибка при получении данных о плательщике'
    PAYER_INFO_NONE = 'компенсация питания не предусмотрена'
    LOCATION_NOT_OFFICE = 'местоположение не в пределах офиса'


BADGE_OFFICE_AVAILABILITY_EXPERIMENT = pytest.mark.client_experiments3(
    consumer='payments_eda/badge_availability',
    experiment_name='badge_office_availability',
    args=[
        {'name': 'location', 'type': 'point', 'value': DESTINATION_POINT},
        {'name': 'phone_id', 'type': 'string', 'value': PHONE_ID},
        {'name': 'yandex_uid', 'type': 'string', 'value': YANDEX_UID},
        {
            'name': 'personal_phone_id',
            'type': 'string',
            'value': PERSONAL_PHONE_ID,
        },
    ],
    value={},
)


def _get_external_login_exp(enabled):
    return pytest.mark.client_experiments3(
        consumer=service_consts.EXP3_CONSUMER_WEB,
        experiment_name=experiments.PAYMENTS_EDA_EXTERNAL_LOGIN_EXP,
        args=[
            {'name': 'yandex_uid', 'type': 'string', 'value': 'uid'},
            {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'version',
                'type': 'application_version',
                'value': '1.2.3',
            },
            {'name': 'application.brand', 'type': 'string', 'value': 'yataxi'},
        ],
        value={'enabled': enabled},
    )


@pytest.fixture(name='mock_badgepay_payerinfo')
def _mock_badgepay_payerinfo(mockserver):
    def wrap(
            login='login',
            location='All',
            response=None,
            check_staff_login=False,
            check_external_login=False,
            status=400,
    ):
        @mockserver.json_handler('/badgepay/pg/eda/payerInfo')
        def handler(request):
            if check_staff_login:
                assert 'login' in request.query
            if check_external_login:
                assert 'externalLogin' in request.query

            if response is None:
                return mockserver.make_response(
                    status=200, json={'login': login, 'location': location},
                )

            return web.json_response(response, status=status)

        return handler

    return wrap


@pytest.fixture(name='blackbox_mock')
def _blackbox_mock(mockserver):
    def wrap(response=None, fail=False):
        @mockserver.json_handler('/blackbox/blackbox')
        async def blackbox_handler(request):
            if fail:
                return mockserver.make_response(status=500)
            return response

        return blackbox_handler

    return wrap


async def test_blackbox_error(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        build_pa_headers,
        mockserver,
        blackbox_mock,
):
    blackbox_mock(fail=True)

    response = await web_app_client.post(
        '/v1/badge-availability',
        json={},
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid='uid',
            request_application=REQUEST_APPLICATION_HEADER,
        ),
    )
    assert response.status == 200
    assert await response.json() == {
        'availability': {
            'available': False,
            'disabled_reason': BadgeDisabledReason.TECHNICAL_ISSUE.value,
        },
        **PAYMENT_INFO,
    }

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'badge_availability'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'application_name': 'android',
                'availability': '0',
                'disabled_reason': 'TECHNICAL_ISSUE',
                'location': 'no_location',
                'sensor': 'badge_availability',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


@pytest.fixture
def _all_methods_in_exp3(mockserver, load_json):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def handler(request):
        return load_json('exp3_all_methods_enabled.json')

    return handler


@pytest.mark.parametrize(
    ['location', 'person_is_kpb', 'ext_login_exp_enabled'],
    [
        pytest.param(
            DESTINATION_POINT,
            False,
            False,
            marks=[_get_external_login_exp(False)],
        ),
        pytest.param(
            DESTINATION_POINT,
            False,
            True,
            marks=[_get_external_login_exp(True)],
        ),
        pytest.param(
            DESTINATION_POINT,
            True,
            True,
            marks=[_get_external_login_exp(True)],
        ),
        pytest.param(
            None, False, False, marks=[_get_external_login_exp(False)],
        ),
    ],
)
@BADGE_OFFICE_AVAILABILITY_EXPERIMENT
async def test_monthly_compensation(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        build_pa_headers,
        mockserver,
        mock_badgepay_payerinfo,
        blackbox_mock,
        location,
        person_is_kpb,
        ext_login_exp_enabled,
):
    blackbox_mock(
        response={
            'users': [
                {
                    'login': 'uta123321',
                    'aliases': {} if person_is_kpb else {'13': 'uta123'},
                    'dbfields': (
                        {
                            'subscription.suid.668': (
                                '1' if person_is_kpb else ''
                            ),
                        }
                        if ext_login_exp_enabled
                        else {'subscription.suid.669': ''}
                    ),
                },
            ],
        },
    )

    mock_badgepay_payerinfo(
        location='All',
        check_staff_login=not person_is_kpb,
        check_external_login=person_is_kpb,
    )

    response = await web_app_client.post(
        '/v1/badge-availability',
        json={'location': location},
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid='uid',
            personal_phone_id=PERSONAL_PHONE_ID,
            request_application=REQUEST_APPLICATION_HEADER,
        ),
    )

    assert response.status == 200
    assert await response.json() == {
        'availability': {'available': True, 'disabled_reason': ''},
        **PAYMENT_INFO,
    }

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'badge_availability'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'application_name': 'android',
                'availability': '1',
                'disabled_reason': 'EMPTY',
                'location': 'All',
                'sensor': 'badge_availability',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


@pytest.mark.parametrize(
    'location, availability, disabled_reason',
    [
        (DESTINATION_POINT, True, BadgeDisabledReason.EMPTY),
        (DESTINATION_POINT2, False, BadgeDisabledReason.LOCATION_NOT_OFFICE),
        (None, True, BadgeDisabledReason.EMPTY),
    ],
)
@BADGE_OFFICE_AVAILABILITY_EXPERIMENT
async def test_daily_compensation(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        build_pa_headers,
        mockserver,
        mock_badgepay_payerinfo,
        client_experiments3,
        blackbox_mock,
        location,
        availability,
        disabled_reason,
):
    blackbox_mock(response={'users': [{'aliases': {'13': 'login'}}]})
    mock_badgepay_payerinfo(location='Office')

    response = await web_app_client.post(
        '/v1/badge-availability',
        json={'location': location},
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid='uid',
            personal_phone_id=PERSONAL_PHONE_ID,
            request_application=REQUEST_APPLICATION_HEADER,
        ),
    )

    assert response.status == 200
    assert await response.json() == {
        'availability': {
            'available': availability,
            'disabled_reason': disabled_reason.value,
        },
        **PAYMENT_INFO,
    }

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'badge_availability'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'application_name': 'android',
                'availability': str(int(availability)),
                'disabled_reason': disabled_reason.name,
                'location': 'Office',
                'sensor': 'badge_availability',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


@pytest.mark.parametrize('location', [DESTINATION_POINT, None])
@BADGE_OFFICE_AVAILABILITY_EXPERIMENT
async def test_none_compensation(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        build_pa_headers,
        mockserver,
        mock_badgepay_payerinfo,
        blackbox_mock,
        location,
):
    blackbox_mock(response={'users': [{'aliases': {'13': 'login'}}]})
    mock_badgepay_payerinfo(location='None')

    response = await web_app_client.post(
        '/v1/badge-availability',
        json={'location': location},
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid='uid',
            personal_phone_id=PERSONAL_PHONE_ID,
            request_application=REQUEST_APPLICATION_HEADER,
        ),
    )

    assert response.status == 200
    assert await response.json() == {
        'availability': {
            'available': False,
            'disabled_reason': BadgeDisabledReason.PAYER_INFO_NONE.value,
        },
        **PAYMENT_INFO,
    }

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'badge_availability'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'application_name': 'android',
                'availability': '0',
                'disabled_reason': 'PAYER_INFO_NONE',
                'location': 'None',
                'sensor': 'badge_availability',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


async def test_payerinfo_bad_response(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        build_pa_headers,
        mockserver,
        mock_badgepay_payerinfo,
        blackbox_mock,
):
    blackbox_mock(response={'users': [{'aliases': {'13': 'login'}}]})
    mock_badgepay_payerinfo(
        response={'status': 'ERROR', 'message': 'Client error'}, status=400,
    )

    response = await web_app_client.post(
        '/v1/badge-availability',
        json={},
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid='uid',
            request_application=REQUEST_APPLICATION_HEADER,
        ),
    )

    assert response.status == 200
    assert await response.json() == {
        'availability': {
            'available': False,
            'disabled_reason': BadgeDisabledReason.PAYER_INFO_ERROR.value,
        },
        **PAYMENT_INFO,
    }

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'badge_availability'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'application_name': 'android',
                'availability': '0',
                'disabled_reason': 'PAYER_INFO_ERROR',
                'location': 'no_location',
                'sensor': 'badge_availability',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


async def test_badge_not_found(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        build_pa_headers,
        mockserver,
        mock_badgepay_payerinfo,
        blackbox_mock,
):
    blackbox_mock(response={'users': [{'aliases': {}}]})
    mock_badgepay_payerinfo(location='All')

    response = await web_app_client.post(
        '/v1/badge-availability',
        json={},
        headers=build_pa_headers(
            '1.1.1.1',
            'ru-RU',
            yandex_uid='uid',
            request_application=REQUEST_APPLICATION_HEADER,
        ),
    )

    assert response.status == 200
    assert await response.json() == {
        'availability': {
            'available': False,
            'disabled_reason': (
                BadgeDisabledReason.NOT_FOUND_LOGIN_REASON.value
            ),
        },
        **PAYMENT_INFO,
    }

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'badge_availability'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'application_name': 'android',
                'availability': '0',
                'disabled_reason': 'NOT_FOUND_LOGIN_REASON',
                'location': 'no_location',
                'sensor': 'badge_availability',
            },
            'timestamp': None,
            'value': 1,
        },
    ]
