import pytest

from . import consts
from . import models
from .plugins import grocery_user_debts_configs as configs

DEBT_AMOUNT = '12345'


@pytest.fixture(name='grocery_user_debts_append_prediction')
def _grocery_user_debts_append_prediction(taxi_grocery_user_debts):
    async def _inner(
            actual_debt_pred_status: str,
            status_code=200,
            originator='grocery',
    ):
        body = {
            'debt': {
                'debt_id': consts.DEBT_ID,
                'user': consts.USER_INFO,
                'actual_debt_pred_status': actual_debt_pred_status,
                'reason': models.debt_reason(),
                'originator': originator,
                'debt_amount': DEBT_AMOUNT,
            },
            'order': {
                'order_id': consts.ORDER_ID,
                'country_iso3': consts.COUNTRY_ISO3,
            },
        }

        response = await taxi_grocery_user_debts.post(
            '/processing/v1/debts/append-prediction', json=body,
        )

        assert response.status_code == status_code

    return _inner


@pytest.mark.parametrize('actual_debt_pred_status', ['paid', 'fail'])
async def test_basic_200(
        grocery_user_debts_append_prediction,
        grocery_user_debts_configs,
        grocery_order_log,
        actual_debt_pred_status,
):
    grocery_user_debts_configs.available_non_tech(debt_available=False)

    await grocery_user_debts_append_prediction(
        actual_debt_pred_status=actual_debt_pred_status,
    )


@pytest.mark.parametrize('actual_debt_pred_status', ['paid', 'fail'])
@pytest.mark.parametrize('debt_available', [True, False])
async def test_pgsql(
        grocery_user_debts_append_prediction,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        grocery_order_log,
        debt_available,
        actual_debt_pred_status,
):
    grocery_user_debts_configs.available_non_tech(
        debt_available=debt_available,
    )

    await grocery_user_debts_append_prediction(
        actual_debt_pred_status=actual_debt_pred_status,
    )

    prediction = grocery_user_debts_db.get_prediction(consts.DEBT_ID)
    assert prediction is not None
    assert prediction.order_id == consts.ORDER_ID
    assert prediction.debt_id == consts.DEBT_ID
    assert prediction.yandex_uid == consts.USER_INFO['yandex_uid']
    assert prediction.expected == 'paid' if debt_available else 'fail'
    assert prediction.actual == actual_debt_pred_status
    assert prediction.payload == models.prediction_payload(
        predictor_info={
            'source': 'grocery',
            'orders_history_period': configs.ORDERS_HISTORY_PERIOD,
            'orders_history_limit': configs.ORDERS_HISTORY_LIMIT,
        },
        country_iso3=consts.COUNTRY_ISO3,
    )


@pytest.mark.parametrize('debt_available', [True, False])
async def test_saturn_pgsql(
        grocery_user_debts_append_prediction,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        grocery_order_log,
        debt_available,
        saturn,
):
    grocery_user_debts_configs.settings_saturn()

    saturn.grocery_search_status = debt_available

    await grocery_user_debts_append_prediction(actual_debt_pred_status='paid')

    prediction = grocery_user_debts_db.get_prediction(consts.DEBT_ID)

    assert prediction is not None
    assert prediction.payload == models.prediction_payload(
        predictor_info={
            'source': 'saturn',
            'formula_id': consts.SATURN_FORMULA_ID,
            'saturn_service': consts.SATURN_SERVICE_RUSSIA,
            'formula_threshold': consts.SATURN_FORMULA_THRESHOLD,
        },
        country_iso3=consts.COUNTRY_ISO3,
    )


@pytest.mark.parametrize(
    'grocery_fallback_params', [configs.GROCERY_FALLBACK_PARAMS, None],
)
async def test_saturn_fallback(
        grocery_user_debts_append_prediction,
        grocery_user_debts_configs,
        grocery_user_debts_db,
        grocery_order_log,
        grocery_fallback_params,
        saturn,
):
    grocery_user_debts_configs.settings_saturn(
        grocery_fallback_params=grocery_fallback_params,
    )

    debt_available = grocery_fallback_params is not None

    grocery_user_debts_configs.available_non_tech(
        debt_available=debt_available,
    )

    saturn.grocery_search.status_code = 400

    await grocery_user_debts_append_prediction(actual_debt_pred_status='paid')

    assert saturn.grocery_search.times_called == 1

    prediction = grocery_user_debts_db.get_prediction(consts.DEBT_ID)

    if grocery_fallback_params is not None:
        assert prediction is not None
        assert prediction.payload == models.prediction_payload(
            predictor_info={
                'source': 'grocery',
                'orders_history_period': configs.ORDERS_HISTORY_PERIOD,
                'orders_history_limit': configs.ORDERS_HISTORY_LIMIT,
            },
            country_iso3=consts.COUNTRY_ISO3,
        )
    else:
        assert prediction is None


async def test_disabled_originator(
        grocery_user_debts_append_prediction,
        grocery_user_debts_configs,
        grocery_user_debts_db,
):
    grocery_user_debts_configs.available(debt_available=True)
    grocery_user_debts_configs.originators(False)

    await grocery_user_debts_append_prediction(
        actual_debt_pred_status='paid', originator='tips',
    )
