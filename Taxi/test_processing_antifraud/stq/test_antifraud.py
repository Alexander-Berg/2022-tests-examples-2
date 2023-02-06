# pylint: disable=redefined-outer-name
import datetime

import pytest

from processing_antifraud.internal import antifraud
from processing_antifraud.internal import models
from processing_antifraud.models import antifraud_proc
from processing_antifraud.models import events
from processing_antifraud.models import tariff_settings


@pytest.mark.config(
    FALLBACK_ANTIFRAUD_CONFIG={
        'hold_fix_price': True,
        'last_payment_delta': 300,
        'pause_before_hold': 30,
        'pause_before_hold_airport': 120,
        'pause_before_hold_fix_price': 150,
        'pause_before_hold_no_dest': 0,
        'payment_deltas': [300],
    },
    DEFAULT_ANTIFRAUD_CONFIG={'enabled': True, 'personal': []},
)
@pytest.mark.parametrize(
    'destinations, fixed_price, expected_eta',
    [
        ([], False, 0),
        (['other'], True, 150),
        (['other'], False, 30),
        (['other', 'аэропорт'], True, 150),
        (['other', 'other', 'аэропорт'], False, 120),
    ],
)
async def test_pause_before_start(
        stq3_context, destinations, fixed_price, expected_eta,
):
    app = stq3_context

    afd_doc = {
        '_id': 'random_id',
        'check_card_is_finished': True,
        'nearest_zone': 'moscow',
        'source': None,
        'last_known_ip': '::ffff:94.25.170.207',
        'main_card_payment_id': 'card-x988b7513b1b4235fb392377a',
        'antifraud_finished': False,
        'user_uid': '4020890530',
        'payment_type': 'card',
        'user_phone_id': 'random_phone_id',
        'destinations': destinations,
        'is_fixed_price': fixed_price,
        'client_application': 'yango_android',
        'client_version': '3.3.3',
        'transporting_timestamp': datetime.datetime.utcnow(),
    }

    doc = antifraud_proc.AntifraudProc(afd_doc)

    pause = await antifraud.pause_before_start(app, doc)
    assert pause == expected_eta


@pytest.mark.config(
    ANTIFRAUD_ENABLE_DEFAULT_CONFIG_AS_OVERRIDE=True,
    FALLBACK_ANTIFRAUD_CONFIG={
        'hold_fix_price': True,
        'last_payment_delta': 300,
        'pause_before_hold': 30,
        'pause_before_hold_airport': 120,
        'pause_before_hold_fix_price': 150,
        'pause_before_hold_no_dest': 0,
        'payment_deltas': [300],
        'allowed_debt': False,
    },
    DEFAULT_ANTIFRAUD_CONFIG={
        'enabled': True,
        'personal': [
            {
                'config': {
                    'hold_fix_price': False,
                    'last_payment_delta': 500,
                    'pause_before_hold': 30,
                    'pause_before_hold_airport': 120,
                    'pause_before_hold_fix_price': 120,
                    'pause_before_hold_no_dest': 0,
                    'payment_deltas': [500],
                    'allowed_debt': False,
                },
                'group_id': 1,
                'tariff_class': 'express',
            },
        ],
    },
)
async def test_antifraud_fallback_config(stq3_context):
    antifraud_config = (
        await tariff_settings.TariffSettings.find_antifraud_config_by_zone(
            stq3_context, 'moscow',
        )
    )

    config = antifraud_config.get_personal_config(stq3_context, 1, 'express')
    expected_config = stq3_context.config.DEFAULT_ANTIFRAUD_CONFIG['personal'][
        0
    ]['config']
    assert expected_config == config.to_dict()

    config = antifraud_config.get_personal_config(stq3_context, 2, 'express')
    assert stq3_context.config.FALLBACK_ANTIFRAUD_CONFIG == config.to_dict()


@pytest.mark.config(
    FALLBACK_ANTIFRAUD_CONFIG={
        'hold_fix_price': True,
        'last_payment_delta': 400,
        'pause_before_hold': 30,
        'pause_before_hold_airport': 120,
        'pause_before_hold_fix_price': 150,
        'pause_before_hold_no_dest': 0,
        'payment_deltas': [300],
    },
)
@pytest.mark.parametrize(
    'destinations, fixed_price, cost, expected_sum',
    [
        ([], False, 20, '30.0'),
        (['other'], True, 100, '100'),
        (['other', 'аэропорт'], True, 100, '100'),
        (['other', 'other'], False, 500, '300'),
        (['other', 'other'], False, 750, '700'),
        (['other', 'аэропорт'], False, 500, '500'),
    ],
)
@pytest.mark.parametrize(
    'exp_idx',
    [
        pytest.param(
            1,
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            2,
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_hold_sum(
        stq3_context,
        patch,
        individual_tariffs_mockserver,
        destinations,
        fixed_price,
        cost,
        expected_sum,
        exp_idx,
):
    @patch('taxi.clients.transactions.TransactionsApiClient.invoice_update')
    # pylint: disable=unused-variable
    async def invoice_update(*args, **kwargs):
        return {}

    app = stq3_context

    order_id = 'random_id'

    afd_doc = {
        '_id': order_id,
        'check_card_is_finished': True,
        'nearest_zone': 'moscow',
        'source': None,
        'last_known_ip': '::ffff:94.25.170.207',
        'main_card_payment_id': 'card-x988b7513b1b4235fb392377a',
        'antifraud_finished': False,
        'user_uid': '4020890530',
        'payment_type': 'card',
        'user_phone_id': 'random_phone_id',
        'destinations': destinations,
        'is_fixed_price': fixed_price,
        'client_application': 'yango_android',
        'client_version': '3.3.3',
        'transporting_timestamp': datetime.datetime.utcnow(),
        'surge': {'alpha': 0, 'beta': 1, 'surcharge': 0, 'surge': 1},
        'category_id': '0cda5880ec3b4b4b9079635d3faf8566',
    }

    card = {'billing_card_id': 'random_billing_id'}

    await app.mongo.antifraud_proc.insert(afd_doc)

    doc = antifraud_proc.AntifraudProc(afd_doc)
    zone_settings = tariff_settings.TariffSettings({})
    event = events.Events({'processing_index': 5, 'antifraud_index': 10})

    context = models.Context(doc)

    # pylint: disable=W0212
    await antifraud._update_ride_sum(
        app, event, context, card, cost, zone_settings,
    )

    assert context.antifraud.sum_to_pay == expected_sum
