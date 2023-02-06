import dataclasses
import typing

from _pytest.mark import ParameterSet
import pytest

from order_notify.logic.events import Events
from order_notify.notifications import EVENTS_TO_NOTIFIERS_FOR_OTHER_MAPPER
from order_notify.notifications import EVENTS_TO_NOTIFIERS_MAPPER
from order_notify.payloads import common as payload_logic
from test_order_notify.conftest import BASE_PAYLOAD
from test_order_notify.conftest import TRANSLATIONS_NOTIFY


@dataclasses.dataclass()
class TestCase:
    payload: typing.Dict[str, typing.Any]
    prefix_name: str = ''

    # removes PytestCollectionWarning from test run output
    __test__ = False


def move_to_cash_modifier() -> typing.List[TestCase]:
    return [
        TestCase(BASE_PAYLOAD),
        TestCase(
            {**BASE_PAYLOAD, 'coupon_price': 80.0}, prefix_name='with_coupon',
        ),
    ]


def complete_modifier() -> typing.List[TestCase]:
    return [
        TestCase(BASE_PAYLOAD, prefix_name='with_cost'),
        TestCase({**BASE_PAYLOAD, 'cost': None}, prefix_name='without_cost'),
        TestCase(
            {**BASE_PAYLOAD, 'complement_price': 50.0},
            prefix_name='with_complement',
        ),
        TestCase(
            {**BASE_PAYLOAD, 'cashback_price': 20.0, 'cashback_discount': 1.0},
            prefix_name='with_cashback',
        ),
        TestCase(
            {**BASE_PAYLOAD, 'coupon_price': 80.0}, prefix_name='with_coupon',
        ),
        TestCase(
            {**BASE_PAYLOAD, 'cost': 0, 'coupon_price': 200.0},
            prefix_name='full_coupon',
        ),
    ]


def cancel_modifier() -> typing.List[TestCase]:
    return [
        TestCase(BASE_PAYLOAD, prefix_name='with_cost'),
        TestCase({**BASE_PAYLOAD, 'cost': None}, prefix_name='without_cost'),
        TestCase(
            {
                **BASE_PAYLOAD,
                'is_early_hold': True,
                'is_cancelled_by_early_hold': True,
            },
            prefix_name='by_early_hold',
        ),
        TestCase(
            {**BASE_PAYLOAD, 'is_early_hold': True},
            prefix_name='early_hold_with_cost',
        ),
        TestCase(
            {**BASE_PAYLOAD, 'is_early_hold': True, 'cost': None},
            prefix_name='early_hold_without_cost',
        ),
    ]


def search_failed_modifier() -> typing.List[TestCase]:
    return [
        TestCase(BASE_PAYLOAD),
        TestCase(
            {**BASE_PAYLOAD, 'is_expired_before_check_in': True},
            prefix_name='expired_before_check_in',
        ),
        TestCase(
            {**BASE_PAYLOAD, 'is_expired_before_check_in': False},
            prefix_name='expired_after_check_in',
        ),
    ]


PAYLOAD_MODIFIERS = {
    Events.COMPLETE: complete_modifier,
    Events.MOVED_TO_CASH: move_to_cash_modifier,
    Events.CANCEL_BY_USER: cancel_modifier,
    Events.SEARCH_FAILED: search_failed_modifier,
}


def get_parametrizes(
        mapper: dict,
) -> typing.Tuple[str, typing.List[ParameterSet]]:
    arg_str = 'notifier_cls, payload_doc, expected_push_payload'

    params = []
    for event, notifier_cls in mapper.items():
        custom_parametrize = PAYLOAD_MODIFIERS.get(event)

        if custom_parametrize:
            cases = custom_parametrize()
        else:
            cases = [TestCase(BASE_PAYLOAD)]

        for case in cases:
            case_name = event.name.lower()
            if case.prefix_name:
                case_name = f'{case_name}__{case.prefix_name}'

            params.append(
                pytest.param(
                    notifier_cls, case.payload, case_name, id=case_name,
                ),
            )

    return arg_str, params


@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2, 'cashback': 0}},
)
@pytest.mark.now('2021-05-07T10:48')
@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY,
    tariff={
        'currency_sign.rub': {'ru': '₽'},
        'currency.rub': {'ru': 'руб.'},
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$ $CURRENCY$'},
    },
    color={'FAFBFB': {'ru': 'белый'}},
)
@pytest.mark.parametrize(*get_parametrizes(EVENTS_TO_NOTIFIERS_MAPPER))
async def test_all_notifiers(
        stq3_context,
        mock_tariff_zones,
        mock_feedback,
        mockserver,
        load_json,
        notifier_cls,
        payload_doc,
        expected_push_payload,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _mock_push(request):
        expected = load_json('ucommunications_requests.json')[
            expected_push_payload
        ]

        expected['extra'] = {
            'id': '00000000000040008000000000000000',
            'order_id': 'order_id_1',
        }

        assert request.json['data']['payload'] == expected
        return {}

    locale = 'ru'

    raw_payload = payload_logic.RawPayload(**payload_doc)
    payload = payload_logic.CommonPayload(stq3_context, locale, raw_payload)

    notifier = notifier_cls(stq3_context, 'order_id_1', locale, payload)

    # pylint: disable=protected-access
    sensor_success = f'notify.success.send_push.{notifier._intent}'
    sensor_disabled = f'notify.disabled.send_push.{notifier._intent}'

    get_counter = stq3_context.stats.get_counter

    assert get_counter({'sensor': sensor_success})._value == 0

    await notifier.send_push('user_id_1')

    is_notifier_enabled = await notifier._enabled()
    if is_notifier_enabled:
        assert get_counter({'sensor': sensor_success})._value == 1
    else:
        assert get_counter({'sensor': sensor_disabled})._value == 1


@pytest.mark.now('2021-05-07T10:48')
@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY, color={'FAFBFB': {'en': 'white'}},
)
@pytest.mark.parametrize(
    *get_parametrizes(EVENTS_TO_NOTIFIERS_FOR_OTHER_MAPPER),
)
@pytest.mark.config(
    ROUTE_SHARING_URL_TEMPLATES={
        'yataxi': 'https://taxi.yandex.ru/route-enter/{key}',
    },
    ORDER_ROUTE_SHARING_TASK_CREATION_ENABLED=True,
    ORDER_ROUTE_SHARING_TARIFFS=['econom'],
)
async def test_all_notifiers_for_other(
        stq3_context,
        mock_tariff_zones,
        mock_yacc,
        order_archive_mock,
        mock_yt_locale_fetch,
        mockserver,
        load_json,
        notifier_cls,
        payload_doc,
        expected_push_payload,
        client_experiments3,
):
    @mockserver.json_handler('/user-api/user_phones/get')
    def _mock_user_phones_get(request):
        assert request.json == {'id': 'phone_id_1', 'primary_replica': False}
        return load_json('user_api_response.json')

    @mockserver.json_handler('/communication-scenario/v1/start')
    async def _mock_communication_scenario(request):
        expected = load_json('communication-scenario_requests_for_other.json')[
            expected_push_payload
        ]
        assert request.json == expected
        return {'launch_id': '123'}

    order_archive_mock.set_order_proc(
        {'_id': 'some_id', 'order': {'user_locale': 'en'}},
    )

    locale = 'ru'

    raw_payload = payload_logic.RawPayload(**payload_doc)
    payload = payload_logic.CommonPayload(stq3_context, locale, raw_payload)

    notifier = notifier_cls(stq3_context, 'order_id_1', locale, payload)

    # pylint: disable=protected-access
    is_notifier_enabled = await notifier._enabled()
    if not is_notifier_enabled:
        # todo: enable CancelForOtherNotifier
        return

    await notifier.send_sms('phone_id_1', push_instead_sms=True)

    sensor_success = f'notify.success.send_sms.{notifier._intent}'
    assert (
        stq3_context.stats.get_counter({'sensor': sensor_success})._value == 1
    )

    assert _mock_communication_scenario.times_called == 1
