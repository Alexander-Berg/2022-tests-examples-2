# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_card_filter import helpers

REQUEST = {
    'yandex_uid': '111111',
    'user_id': 'user_id',
    'service_type': 'card',
}
HEADERS = {
    'X-Yandex-UID': '111111',
    'X-Remote-IP': '213.180.193.1',
    'X-Request-Application': 'app_name=iphone,app_ver1=10,app_ver2=2',
}


@pytest.fixture(name='mock_card_antifraud')
def mock_card_antifraud_fixture(mockserver):
    def _mock_card_antifraud(
            all_payments_available=False, available_cards=None,
    ):
        @mockserver.json_handler('/card-antifraud/v1/payment/availability')
        def handler(request):
            return {
                'all_payments_available': all_payments_available,
                'available_cards': available_cards or [],
            }

        return handler

    return _mock_card_antifraud


@pytest.mark.parametrize(
    ['uri', 'request_service', 'service'],
    [
        ('/v1/filteredcards', 'eats', 'eats'),
        ('/v1/filteredcards/legacy', None, 'taxi'),
    ],
)
@pytest.mark.parametrize(
    ['all_payments_available', 'card', 'card_available', 'reason'],
    [
        pytest.param(
            True,
            helpers.make_card(unverified=False),
            True,
            'card-antifraud all payments available',
            id='card-antifraud all_payments_available=True, verified card',
        ),
        pytest.param(
            True,
            helpers.make_card(unverified=True),
            False,
            'unverified from cardstorage',
            id='card-antifraud all_payments_available=True, unverified card',
        ),
        pytest.param(
            False,
            helpers.make_card(unverified=False),
            False,
            'no trust verification details',
            id='card-antifraud all_payments_available=False, verified card',
        ),
        pytest.param(
            False,
            helpers.make_card(unverified=True),
            False,
            'unverified from cardstorage',
            id='card-antifraud all_payments_available=False, unverified card',
        ),
    ],
)
async def test_card_availability_metrics_all_payments_available(
        taxi_card_filter_monitor,
        invoke_handler,
        mock_cardstorage,
        mock_card_antifraud,
        uri,
        request_service,
        service,
        card,
        all_payments_available,
        card_available,
        reason,
):

    mock_cardstorage([card])
    mock_card_antifraud(all_payments_available=all_payments_available)

    request = REQUEST.copy()
    if request_service is not None:
        request['service'] = request_service

    async with metrics_helpers.MetricsCollector(
            taxi_card_filter_monitor, sensor='card-validation',
    ) as collector:
        await invoke_handler(uri, request, HEADERS)

    assert collector.get_single_collected_metric() == metrics_helpers.Metric(
        labels={
            'application_name': 'iphone',
            'service_name': service,
            'service_type': 'card',
            'available': '1' if card_available else '0',
            'reason': reason,
            'verification_level': 'none',
            'sensor': 'card-validation',
        },
        value=1,
    )


@pytest.mark.parametrize(
    ['uri', 'request_service', 'service'],
    [
        ('/v1/filteredcards', 'eats', 'eats'),
        ('/v1/filteredcards/legacy', None, 'taxi'),
    ],
)
@pytest.mark.parametrize(
    ['available_cards', 'card', 'card_available', 'reason'],
    [
        pytest.param(
            [{'card_id': 'card_id'}],
            helpers.make_card(unverified=False),
            True,
            'card-antifraud available cards',
            id='card in available cards, verified card',
        ),
        # not sure if this one is possible
        pytest.param(
            [{'card_id': 'card_id'}],
            helpers.make_card(unverified=True),
            False,
            'unverified from cardstorage',
            id='card in available cards, unverified card',
        ),
    ],
)
async def test_card_availability_metrics_available_cards(
        taxi_card_filter_monitor,
        invoke_handler,
        mock_cardstorage,
        mock_card_antifraud,
        uri,
        request_service,
        service,
        available_cards,
        card,
        card_available,
        reason,
):
    mock_cardstorage([card])
    mock_card_antifraud(available_cards=available_cards)

    request = REQUEST.copy()
    if request_service is not None:
        request['service'] = request_service

    async with metrics_helpers.MetricsCollector(
            taxi_card_filter_monitor, sensor='card-validation',
    ) as collector:
        await invoke_handler(uri, request, HEADERS)

    assert collector.get_single_collected_metric() == metrics_helpers.Metric(
        labels={
            'application_name': 'iphone',
            'service_name': service,
            'service_type': 'card',
            'available': '1' if card_available else '0',
            'reason': reason,
            'verification_level': 'none',
            'sensor': 'card-validation',
        },
        value=1,
    )


@pytest.mark.config(CARD_ANTIFRAUD_VERIFICATION_LEVELS_BLACKLIST=['cvv'])
@pytest.mark.parametrize(
    ['uri', 'request_service', 'service'],
    [
        ('/v1/filteredcards', 'eats', 'eats'),
        ('/v1/filteredcards/legacy', None, 'taxi'),
    ],
)
@pytest.mark.parametrize(
    ['card_available', 'verification_level', 'reason'],
    [
        pytest.param(
            False,
            'cvv',
            'trust verification level blacklisted',
            id='trust verification level blacklisted',
        ),
        # not sure if this one is possible
        pytest.param(
            True,
            '3ds',
            'trust verification level accepted',
            id='trust verification level accepted',
        ),
    ],
)
async def test_card_availability_metrics_verification_level(
        taxi_card_filter_monitor,
        invoke_handler,
        mock_cardstorage,
        mock_card_antifraud,
        uri,
        request_service,
        service,
        card_available,
        verification_level,
        reason,
):
    mock_cardstorage(
        [
            helpers.make_card(
                verification_details={'level': verification_level},
            ),
        ],
    )
    mock_card_antifraud()

    request = REQUEST.copy()
    if request_service is not None:
        request['service'] = request_service

    async with metrics_helpers.MetricsCollector(
            taxi_card_filter_monitor, sensor='card-validation',
    ) as collector:
        await invoke_handler(uri, request, HEADERS)

    assert collector.get_single_collected_metric() == metrics_helpers.Metric(
        labels={
            'application_name': 'iphone',
            'service_name': service,
            'service_type': 'card',
            'available': '1' if card_available else '0',
            'reason': reason,
            'verification_level': verification_level,
            'sensor': 'card-validation',
        },
        value=1,
    )
