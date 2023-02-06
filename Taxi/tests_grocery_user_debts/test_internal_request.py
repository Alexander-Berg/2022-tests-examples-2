# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error

import datetime
import decimal

from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import models
from .plugins import grocery_user_debts_configs as configs

DEBT_AMOUNT = '12345'
PRIMARY_PAYMENT_TYPE = 'card'
PERMANENT_CARD_ID = 'some-card-1234'
CARD_ID = 'card-x00089157c000c80e0000ac74'


@pytest.fixture(name='grocery_user_debts_request')
def _grocery_user_debts_request(taxi_grocery_user_debts):
    async def _inner(
            *,
            status_code=200,
            reason=models.debt_reason(payment_type=PRIMARY_PAYMENT_TYPE),
            **kwargs,
    ):
        body = {
            'debt_id': consts.DEBT_ID,
            'user': consts.USER_INFO,
            'order': {
                'order_id': consts.ORDER_ID,
                'country_iso3': consts.COUNTRY_ISO3,
            },
            'reason': reason,
            'originator': 'grocery',
            'debt_amount': DEBT_AMOUNT,
            **kwargs,
        }
        response = await taxi_grocery_user_debts.post(
            '/internal/debts/v1/request', json=body,
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('debt_available_tech', [True, False])
@pytest.mark.parametrize('orders_count', [0, 1, 5, 10])
async def test_basic(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_order_log,
        debt_available_tech,
        orders_count,
):
    orders_count_to_enable = 5
    debt_available = (
        debt_available_tech and orders_count >= orders_count_to_enable
    )

    grocery_user_debts_configs.available_tech(
        debt_available=debt_available_tech,
    )
    grocery_user_debts_configs.available_non_tech(
        orders_count_to_enable=orders_count_to_enable,
    )

    grocery_order_log.mock_ids_by_range([str(i) for i in range(orders_count)])

    response = await grocery_user_debts_request()
    assert response == dict(debt_available=debt_available)


@pytest.mark.now(consts.NOW)
async def test_order_log(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_order_log,
):
    grocery_user_debts_configs.available_tech(debt_available=True)

    grocery_order_log.check_ids_by_range(
        yandex_uid=consts.YANDEX_UID,
        filter_by_status='closed',
        range=dict(offset=0, limit=configs.ORDERS_HISTORY_LIMIT),
        period=dict(
            start=(
                consts.NOW_DT
                - datetime.timedelta(hours=configs.ORDERS_HISTORY_PERIOD)
            ).isoformat(),
            end=consts.NOW_DT.isoformat(),
        ),
    )

    await grocery_user_debts_request()
    assert grocery_order_log.ids_by_range_times_called() == 1


async def test_debts_list(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_order_log,
        debt_collector,
):
    grocery_user_debts_configs.available_tech(debt_available=False)

    debt_collector.list.check(
        service=consts.SERVICE,
        debtors=[f'yandex/uid/{consts.YANDEX_UID}'],
        limit=1,
    )

    await grocery_user_debts_request()
    assert debt_collector.list.times_called == 1


@pytest.mark.parametrize('debt_available', [True, False])
async def test_pgsql(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        grocery_order_log,
        debt_available,
):
    debt_reason = models.debt_reason()

    grocery_user_debts_configs.available(debt_available=debt_available)

    response = await grocery_user_debts_request(reason=debt_reason)
    assert response == dict(debt_available=debt_available)

    debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert debt is None


@pytest.mark.parametrize('tech_available', [True, False])
@pytest.mark.parametrize('non_tech_available', [True, False])
@pytest.mark.parametrize('tech_reason', ['tech_reason', None])
@pytest.mark.parametrize('non_tech_reason', ['non_tech_reason', None])
async def test_metric(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_order_log,
        taxi_grocery_user_debts_monitor,
        tech_available,
        non_tech_available,
        tech_reason,
        non_tech_reason,
):
    sensor = 'grocery_user_debts_request_metrics'

    grocery_user_debts_configs.available_tech(
        debt_available=tech_available, reason=tech_reason,
    )
    grocery_user_debts_configs.available_non_tech(
        debt_available=non_tech_available, reason=non_tech_reason,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_user_debts_monitor, sensor=sensor,
    ) as collector:
        await grocery_user_debts_request()

    def expected_reason():
        if not tech_available:
            return tech_reason
        if not non_tech_available:
            return non_tech_reason

        return (
            f'{tech_reason}:{non_tech_reason}'
            if tech_reason and non_tech_reason
            else tech_reason or non_tech_reason
        )

    available = tech_available and non_tech_available

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'originator': models.InvoiceOriginator.grocery.name,
        'country': consts.COUNTRY,
        'payment_type': PRIMARY_PAYMENT_TYPE,
        'is_available': 'true' if available else 'false',
        'reason': expected_reason() or 'none',
    }


@pytest.mark.parametrize('debt_available', [True, False])
async def test_saturn_request(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        debt_collector,
        debt_available,
        saturn,
):
    grocery_user_debts_configs.settings_saturn()
    grocery_user_debts_configs.available_tech(debt_available=True)
    grocery_user_debts_configs.set_pass_payment_to_saturn(enabled=True)

    models.debt_reason(payment_type=PRIMARY_PAYMENT_TYPE)

    saturn.grocery_search_status = debt_available
    saturn.grocery_search.check(
        request_id=consts.DEBT_ID,
        puid=decimal.Decimal(consts.YANDEX_UID),
        service=consts.SERVICE,
        basket={'total_sum': decimal.Decimal(DEBT_AMOUNT)},
        formula_id=consts.SATURN_FORMULA_ID,
        payment_info=None,
        formula_threshold=consts.SATURN_FORMULA_THRESHOLD,
    )

    response = await grocery_user_debts_request()
    assert response == dict(debt_available=debt_available)

    assert saturn.grocery_search.times_called == 1
    assert debt_collector.list.times_called == 1


@pytest.mark.parametrize(
    'payment_type, payment_id, saturn_card_id, need_cardstorage_request',
    [
        pytest.param(
            'card',
            'card-x1234',
            PERMANENT_CARD_ID,
            True,
            id='pass_permanent_id_from_cardstorage',
        ),
        pytest.param(
            'card',
            CARD_ID,
            CARD_ID,
            False,
            id='pass_same_id_because_already_permanent',
        ),
        pytest.param(
            'applepay',
            'apple_token-1080_B900046B-E000-4000-A000-0001113C09B5',
            None,
            False,
            id='do_no_pass_payment_id_because_not_cardc',
        ),
    ],
)
async def test_payment_info_saturn_request(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        cardstorage,
        saturn,
        payment_type,
        payment_id,
        saturn_card_id,
        need_cardstorage_request,
):
    grocery_user_debts_configs.settings_saturn()
    grocery_user_debts_configs.available_tech(debt_available=True)
    grocery_user_debts_configs.set_pass_payment_to_saturn(enabled=True)

    reason = models.debt_reason(
        payment_type=payment_type, payment_id=payment_id,
    )

    cardstorage.card.mock_response(permanent_card_id=PERMANENT_CARD_ID)

    payment_info = {'payment_type': payment_type}
    if saturn_card_id is not None:
        payment_info['card_id'] = saturn_card_id

    saturn.grocery_search.check(payment_info=payment_info)

    await grocery_user_debts_request(reason=reason)

    assert saturn.grocery_search.times_called == 1
    assert cardstorage.card.times_called == int(need_cardstorage_request)


async def test_saturn_404(
        grocery_user_debts_request, grocery_user_debts_configs, saturn,
):
    grocery_user_debts_configs.available_tech(debt_available=True)
    grocery_user_debts_configs.settings_saturn()

    grocery_user_debts_configs.available_non_tech(debt_available=True)

    saturn.grocery_search.status_code = 404

    response = await grocery_user_debts_request()

    assert response == dict(debt_available=False)
    assert saturn.grocery_search.times_called == 1


@pytest.mark.parametrize(
    'grocery_fallback_params', [configs.GROCERY_FALLBACK_PARAMS, None],
)
async def test_saturn_fallback(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_fallback_params,
        saturn,
):
    grocery_user_debts_configs.available_tech(debt_available=True)
    grocery_user_debts_configs.settings_saturn(
        grocery_fallback_params=grocery_fallback_params,
    )

    debt_available = grocery_fallback_params is not None

    grocery_user_debts_configs.available_non_tech(
        debt_available=debt_available,
    )

    saturn.grocery_search.status_code = 400

    response = await grocery_user_debts_request()

    assert response == dict(debt_available=debt_available)
    assert saturn.grocery_search.times_called == 1


async def test_disabled_originator(
        grocery_user_debts_request, grocery_user_debts_configs,
):
    grocery_user_debts_configs.available(debt_available=True)
    grocery_user_debts_configs.originators(False)

    response = await grocery_user_debts_request(originator='tips')
    assert response == dict(debt_available=False)


@pytest.mark.parametrize(
    'exp3_name',
    ['grocery_user_debts_available_tech', 'grocery_user_debts_available'],
)
async def test_exp_available(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_order_log,
        experiments3,
        exp3_name,
):
    reason = models.debt_reason()
    orders_count = 5
    is_tech = exp3_name == 'grocery_user_debts_available_tech'

    exp3_recorder = experiments3.record_match_tries(exp3_name)

    grocery_user_debts_configs.available(debt_available=True)

    grocery_order_log.mock_ids_by_range(['id'] * orders_count)

    await grocery_user_debts_request(reason=reason)

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert exp3_kwargs['consumer'] == 'grocery-user-debts/available'
    assert exp3_kwargs['yandex_uid'] == consts.YANDEX_UID
    assert exp3_kwargs['personal_phone_id'] == consts.PERSONAL_PHONE_ID
    assert exp3_kwargs['country_iso3'] == consts.COUNTRY_ISO3
    assert exp3_kwargs['originator'] == 'grocery'
    assert exp3_kwargs['primary_payment_type'] == reason['payment_type']
    assert exp3_kwargs['error_reason_code'] == reason['error_reason_code']
    assert exp3_kwargs['is_technical_error'] == reason['is_technical_error']
    assert exp3_kwargs['debt_amount'] == float(DEBT_AMOUNT)
    assert exp3_kwargs['is_debt_exists'] is True
    assert exp3_kwargs['debt_id'] == consts.DEBT_ID
    if is_tech:
        assert 'orders_count' not in exp3_kwargs
    else:
        assert exp3_kwargs['orders_count'] == orders_count


async def test_exp_settings(
        grocery_user_debts_request, grocery_user_debts_configs, experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'grocery_user_debts_settings',
    )

    grocery_user_debts_configs.available(debt_available=True)

    await grocery_user_debts_request()

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert exp3_kwargs['consumer'] == 'grocery-user-debts'
    assert exp3_kwargs['yandex_uid'] == consts.YANDEX_UID
    assert exp3_kwargs['personal_phone_id'] == consts.PERSONAL_PHONE_ID
    assert exp3_kwargs['country_iso3'] == consts.COUNTRY_ISO3
    assert exp3_kwargs['originator'] == 'grocery'
    assert exp3_kwargs['primary_payment_type'] == PRIMARY_PAYMENT_TYPE
    assert exp3_kwargs['purpose'] == 'debt'


async def test_exp_originators(grocery_user_debts_request, experiments3):
    exp3_recorder = experiments3.record_match_tries(
        'grocery_user_debts_originators',
    )

    await grocery_user_debts_request()

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert exp3_kwargs['consumer'] == 'grocery-user-debts'
    assert exp3_kwargs['yandex_uid'] == consts.YANDEX_UID
    assert exp3_kwargs['personal_phone_id'] == consts.PERSONAL_PHONE_ID
    assert exp3_kwargs['country_iso3'] == consts.COUNTRY_ISO3
    assert exp3_kwargs['originator'] == 'grocery'
    assert exp3_kwargs['primary_payment_type'] == PRIMARY_PAYMENT_TYPE
    assert exp3_kwargs['purpose'] == 'debt'


@pytest.mark.parametrize('has_debt', [True, False])
async def test_without_reason(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        grocery_order_log,
        has_debt,
):
    if has_debt:
        grocery_user_debts_db.upsert(models.Debt())

    grocery_user_debts_configs.available(debt_available=True)

    response = await grocery_user_debts_request(reason=None)
    assert response['debt_available'] == has_debt


@pytest.mark.parametrize('has_debt', [True, False])
async def test_is_debt_exists(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        debt_collector,
        experiments3,
        has_debt,
):
    exp3_name = 'grocery_user_debts_available_tech'

    if has_debt:
        grocery_user_debts_db.upsert(
            models.Debt(debt_id=consts.DEBT_ID, order_id=consts.ORDER_ID),
        )

    exp3_recorder = experiments3.record_match_tries(exp3_name)

    grocery_user_debts_configs.available(debt_available=True)

    debt_collector.list.mock_response(id=consts.DEBT_ID)

    await grocery_user_debts_request()

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert exp3_kwargs['is_debt_exists'] is not has_debt


@pytest.mark.parametrize(
    'errors, expected',
    [(['code_true'], True), (['code_true', 'code_false'], False)],
)
async def test_multiple_error_reason_flow(
        grocery_user_debts_request,
        grocery_user_debts_configs,
        grocery_order_log,
        experiments3,
        errors,
        expected,
):
    debt_reason = models.debt_reason(
        errors=[dict(error_reason_code=it) for it in errors],
    )

    grocery_user_debts_configs.available_tech_by_error(
        code_true=True, code_false=False,
    )
    grocery_user_debts_configs.available_non_tech(debt_available=True)
    grocery_user_debts_configs.error_reason_flow('multiple')

    response = await grocery_user_debts_request(reason=debt_reason)

    assert response == dict(debt_available=expected)
