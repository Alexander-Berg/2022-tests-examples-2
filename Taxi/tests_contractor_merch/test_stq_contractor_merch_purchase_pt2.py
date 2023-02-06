import copy
import decimal

import pytest

from tests_contractor_merch import util

TRANSLATIONS = util.STQ_TRANSLATIONS
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS

DEFAULT_TASK_ID = 'some_task_id'
DEFAULT_STQ_KWARGS = {
    'driver_id': 'driver1',
    'park_id': 'park_id',
    'feed_id': 'some_id',
    'idempotency_token': 'idemp1',
    'accept_language': 'en_GB',
    'price': '2.4',
    'price_with_currency': {'value': '2.4', 'currency': 'RUB'},
    'feed_payload': {
        'category': 'cat',
        'feeds_admin_id': 'feeds-admin-id-1',
        'balance_payment': True,
        'title': 'Gift card (1000 rub)',
        'partner': {'name': 'Apple'},
        'meta_info': {},
    },
}

RETRIEVE_BY_PROFILES_RESPONSE = {
    'uniques': [
        {
            'park_driver_profile_id': 'park_id_one_offer_total_limit_excceded',
            'data': {'unique_driver_id': 'some_uniq_id'},
        },
    ],
}

RETRIEVE_BY_PROFILES_RESPONSE_NO_UNIQ = {
    'uniques': [
        {'park_driver_profile_id': 'park_id_one_offer_total_limit_excceded'},
    ],
}

RETRIEVE_BY_UNIQUES_RESPONSE = {
    'profiles': [
        {
            'unique_driver_id': 'some_uniq_id',
            'data': [
                {
                    'park_id': 'park_id',
                    'driver_profile_id': 'one_offer_total_limit_excceded',
                    'park_driver_profile_id': (
                        'park_id_one_offer_total_limit_excceded'
                    ),
                },
                {
                    'park_id': 'park_id2',
                    'driver_profile_id': 'some_driver',
                    'park_driver_profile_id': (
                        'park_id_one_offer_total_limit_excceded'
                    ),
                },
            ],
        },
    ],
}

RETRIEVE_BY_UNIQUES_RESPONSE_1_DRIVER = {
    'profiles': [
        {
            'unique_driver_id': 'some_uniq_id',
            'data': [
                {
                    'park_id': 'park_id',
                    'driver_profile_id': 'one_offer_total_limit_excceded',
                    'park_driver_profile_id': (
                        'park_id_one_offer_total_limit_excceded'
                    ),
                },
            ],
        },
    ],
}


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.config(
    CONTRACTOR_MERCH_DISABLED_PARK_IDS=['park_id', 'park1', 'some_other_id'],
)
async def test_marketplace_is_disabled_for_park(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp3',
            'accept_language': 'en_GB',
            'price': '120',
            'price_with_currency': {'value': '120', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': {},
            },
        },
    )

    assert mock_driver_profiles.driver_profiles.times_called == 0

    voucher = util.get_voucher_by_idemp(
        cursor, 'park_id', 'driver_id', 'idemp3', with_created_at=False,
    )

    assert voucher == {
        'id': 'idemp3',
        'park_id': 'park_id',
        'driver_id': 'driver_id',
        'idempotency_token': 'idemp3',
        'price': decimal.Decimal('120'),
        'currency': 'RUB',
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'promocode_id': None,
        'status': 'failed',
        'status_reason': 'marketplace_is_disabled_for_park',
    }

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': 'park_id_driver_id'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': {
            'alert': False,
            'format': 'Markdown',
            'important': True,
            'text': 'marketplace_is_disabled_for_park-tr',
            'title': 'Gift card (1000 rub): failed',
            'type': 'newsletter',
        },
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['limits.sql'])
@pytest.mark.parametrize(
    'meta_info, retrieve_by_profiles_response, '
    'retrieve_by_uniques_response, expected_problem_description',
    [
        pytest.param(
            {'total_per_unique_driver_limit': 2},
            RETRIEVE_BY_PROFILES_RESPONSE,
            RETRIEVE_BY_UNIQUES_RESPONSE,
            {
                'code': 'one_offer_per_unique_driver_total_limit_excceded',
                'localized_message': (
                    'one_offer_per_unique_driver_total_limit_excceded-tr'
                ),
            },
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='total_per_unique_driver_limit_excceded',
        ),
        pytest.param(
            {'total_per_unique_driver_limit': 2},
            RETRIEVE_BY_PROFILES_RESPONSE_NO_UNIQ,
            RETRIEVE_BY_UNIQUES_RESPONSE,
            {
                'code': 'some_error_occured',
                'localized_message': 'some_error_occured-tr',
            },
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='no_unique_driver',
        ),
        pytest.param(
            {'total_per_unique_driver_limit': 2},
            RETRIEVE_BY_PROFILES_RESPONSE,
            RETRIEVE_BY_UNIQUES_RESPONSE_1_DRIVER,
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='total_per_unique_driver_limit_unreached_1',
        ),
        pytest.param(
            {'total_per_unique_driver_limit': 3},
            RETRIEVE_BY_PROFILES_RESPONSE,
            RETRIEVE_BY_UNIQUES_RESPONSE,
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='total_per_unique_driver_limit_unreached_2',
        ),
    ],
)
async def test_unique_driver_limits(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_unique_drivers,
        mock_taximeter_xservice,
        meta_info,
        retrieve_by_profiles_response,
        retrieve_by_uniques_response,
        expected_problem_description,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    mock_unique_drivers.retrieve_by_profiles_response = (
        retrieve_by_profiles_response
    )
    mock_unique_drivers.retrieve_by_uniques_response = (
        retrieve_by_uniques_response
    )
    mock_taximeter_xservice.driver_exams_retrieve_response = {
        'dkvu_exam': {'summary': {'is_blocked': False}},
    }
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'one_offer_total_limit_excceded',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp3',
            'accept_language': 'en_GB',
            'price': '120',
            'price_with_currency': {'value': '120', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': meta_info,
            },
        },
    )

    assert mock_driver_profiles.driver_profiles.times_called == 1

    voucher = util.get_voucher_by_idemp(
        cursor,
        'park_id',
        'one_offer_total_limit_excceded',
        'idemp3',
        with_created_at=False,
    )
    assert voucher == {
        'id': 'idemp3',
        'park_id': 'park_id',
        'driver_id': 'one_offer_total_limit_excceded',
        'idempotency_token': 'idemp3',
        'price': decimal.Decimal('120'),
        'currency': 'RUB',
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'promocode_id': None if expected_problem_description else 'p1',
        'status': 'failed' if expected_problem_description else 'fulfilled',
        'status_reason': (
            expected_problem_description.get('code')
            if expected_problem_description
            else None
        ),
    }

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': 'park_id_one_offer_total_limit_excceded'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': {
            'alert': False,
            'format': 'Markdown',
            'important': True,
            'text': (
                expected_problem_description['localized_message']
                if expected_problem_description
                else 'Default text with number, here it is: 100500'
            ),
            'title': (
                'Gift card (1000 rub): failed'
                if expected_problem_description
                else 'Gift card (1000 rub): succ'
            ),
            'type': 'newsletter',
        },
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['limits.sql'])
async def test_dkvu(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_taximeter_xservice,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    mock_taximeter_xservice.driver_exams_retrieve_response = {
        'dkvu_exam': {'summary': {'is_blocked': True}},
    }

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'one_offer_total_limit_excceded',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp3',
            'accept_language': 'en_GB',
            'price': '120',
            'price_with_currency': {'value': '120', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': {'total_per_unique_driver_limit': 2},
            },
        },
    )

    assert mock_driver_profiles.driver_profiles.times_called == 1

    cursor = pgsql['contractor_merch'].cursor()
    voucher = util.get_voucher_by_idemp(
        cursor,
        'park_id',
        'one_offer_total_limit_excceded',
        'idemp3',
        with_created_at=False,
    )
    assert voucher == {
        'id': 'idemp3',
        'park_id': 'park_id',
        'driver_id': 'one_offer_total_limit_excceded',
        'idempotency_token': 'idemp3',
        'price': decimal.Decimal('120'),
        'currency': 'RUB',
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'promocode_id': None,
        'status': 'failed',
        'status_reason': 'drivers_license_is_not_verified',
    }

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': 'park_id_one_offer_total_limit_excceded'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': {
            'alert': False,
            'format': 'Markdown',
            'important': True,
            'text': 'drivers_license_is_not_verified-tr',
            'title': 'Gift card (1000 rub): failed',
            'type': 'newsletter',
        },
    }


VKUSVILL_TRANSLATIONS = {
    **util.CUSTOM_MESSAGES_TRANSLATIONS,
    'vkusvill.success_with_number.text': {
        'en': 'Waiting for you in Vkusvill with promo: %(promocode_value)s',
    },
    'vkusvill.success_without_number.text': {
        'en': 'Just waiting for you in Vkusvill, have a nice day',
    },
}


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['url_unsafe_promocode.sql'])
@pytest.mark.config(
    CONTRACTOR_MERCH_SUPPORTED_BARCODES={
        'ean13': {
            'render_url_template': 'https://ean13?barcode={promocode_number}',
            'url_text_tanker_key': (
                'notification_v1.success.linear_barcode_url_text'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'is_send_enabled, send_number_along_with_barcode, expected_text',
    [
        pytest.param(
            True, True, 'Default text with number, here it is: 100/500',
        ),
        pytest.param(
            False, True, 'Default text with number, here it is: 100/500',
        ),
        pytest.param(
            True, False, 'Default text without number, nothing to show',
        ),
        pytest.param(
            False, None, 'Default text without number, nothing to show',
        ),
    ],
)
async def test_send_barcode(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        is_send_enabled,
        send_number_along_with_barcode,
        expected_text,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    mock_fleet_transactions_api.balance = '2.4'

    await stq_runner.contractor_merch_purchase.call(
        task_id=DEFAULT_TASK_ID,
        kwargs={
            **DEFAULT_STQ_KWARGS,
            'feed_payload': {
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'feeds_admin_id': 'feeds-admin-id-1',
                'category': 'tire',
                'balance_payment': True,
                'meta_info': {
                    'barcode_params': {
                        'is_send_enabled': is_send_enabled,
                        'type': 'ean13',
                        'send_number_along_with_barcode': (
                            send_number_along_with_barcode
                        ),
                    },
                },
            },
        },
    )
    assert mock_driver_profiles.driver_profiles.times_called == 1

    expected_template = {
        'alert': False,
        'format': 'Markdown',
        'important': True,
        'text': expected_text,
        'title': 'Gift card (1000 rub): succ',
        'type': 'newsletter',
    }
    if is_send_enabled:
        expected_template.update(
            {
                'url': 'https://ean13?barcode=100%2F500',
                'teaser': 'Your barcode',
                'url_open_mode': 'webview',
            },
        )

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': f'park_id_driver1'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': expected_template,
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=VKUSVILL_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['url_unsafe_promocode.sql'])
@pytest.mark.config(
    CONTRACTOR_MERCH_SUPPORTED_BARCODES={
        'ean13': {
            'render_url_template': 'https://ean13?barcode={promocode_number}',
            'url_text_tanker_key': (
                'notification_v1.success.linear_barcode_url_text'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'barcode_params_enabled, '
    'is_send_enabled, send_number_along_with_barcode, '
    'custom_key, expected_text',
    [
        pytest.param(
            True,
            False,
            True,
            'vkusvill.success_with_number.text',
            'Waiting for you in Vkusvill with promo: 100/500',
        ),
        pytest.param(
            True,
            True,
            False,
            'vkusvill.success_without_number.text',
            'Just waiting for you in Vkusvill, have a nice day',
        ),
        pytest.param(
            False,
            None,
            True,
            'vkusvill.success_with_number.text',
            'Waiting for you in Vkusvill with promo: 100/500',
        ),
    ],
)
async def test_custom_tanker_keys(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        barcode_params_enabled,
        is_send_enabled,
        send_number_along_with_barcode,
        custom_key,
        expected_text,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    mock_fleet_transactions_api.balance = '2.4'

    feed_payload = {
        'title': 'Gift card (1000 rub)',
        'partner': {'name': 'Apple'},
        'category': 'tire',
        'balance_payment': True,
        'feeds_admin_id': 'feeds-admin-id-1',
        'meta_info': {
            'barcode_params': {
                'is_send_enabled': is_send_enabled,
                'type': 'ean13',
                'send_number_along_with_barcode': (
                    send_number_along_with_barcode
                ),
            },
        },
    }

    if not barcode_params_enabled:
        del feed_payload['meta_info']['barcode_params']

    if send_number_along_with_barcode:
        feed_payload['meta_info'][
            'chat_instructions_tanker_key_with_promocode_number'
        ] = custom_key
    else:
        feed_payload['meta_info'][
            'chat_instructions_tanker_key_without_promocode_number'
        ] = custom_key

    await stq_runner.contractor_merch_purchase.call(
        task_id=DEFAULT_TASK_ID,
        kwargs={**DEFAULT_STQ_KWARGS, 'feed_payload': feed_payload},
    )
    assert mock_driver_profiles.driver_profiles.times_called == 1

    expected_template = {
        'alert': False,
        'format': 'Markdown',
        'important': True,
        'text': expected_text,
        'title': 'Gift card (1000 rub): succ',
        'type': 'newsletter',
    }
    if is_send_enabled:
        expected_template.update(
            {
                'url': 'https://ean13?barcode=100%2F500',
                'teaser': 'Your barcode',
                'url_open_mode': 'webview',
            },
        )

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': f'park_id_driver1'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': expected_template,
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['offer_with_few_promocodes.sql'])
@pytest.mark.parametrize(
    'feeds_admin_id, is_offer_with_few_promocodes',
    [
        pytest.param('f1', True),
        pytest.param('f2', False),
        pytest.param('f2', None),
    ],
)
async def test_offer_with_few_promocodes(
        stq_runner,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        feeds_admin_id,
        is_offer_with_few_promocodes,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    feed_payload = {
        'feeds_admin_id': feeds_admin_id,
        'title': 'Специальный оффер для СМЗ',
        'partner': {'name': 'Apple'},
        'category': 'food',
        'balance_payment': True,
        'meta_info': {},
    }

    if is_offer_with_few_promocodes is not None:
        feed_payload['meta_info'][
            'is_offer_with_few_promocodes'
        ] = is_offer_with_few_promocodes

    await stq_runner.contractor_merch_purchase.call(
        task_id=DEFAULT_TASK_ID,
        kwargs={**DEFAULT_STQ_KWARGS, 'feed_payload': feed_payload},
    )

    assert mock_driver_profiles.driver_profiles.times_called == 1

    promocodes_info = [
        ('WSFWF151', 'Макдоналдс'),
        ('WSFWF132', 'Автомойка'),
        ('WSFWF21323', 'Шаверма'),
    ]

    promocode_number = (
        '  \n'.join(
            [
                f'1. {caption}: **{number}**'
                for number, caption in promocodes_info
            ],
        )
        if bool(is_offer_with_few_promocodes)
        else 'WSFWF11412'
    )

    expected_template = {
        'alert': False,
        'format': 'Markdown',
        'important': True,
        'text': f'Default text with number, here it is: {promocode_number}',
        'title': 'Специальный оффер для СМЗ: succ',
        'type': 'newsletter',
    }

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': f'park_id_driver1'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': expected_template,
    }


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.pgsql('contractor_merch', files=['url_unsafe_promocode.sql'])
async def test_offer_with_hyperlinked_promocodes(
        stq_runner,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    feed_payload = {
        'title': 'Оффер с сертификатом',
        'partner': {'name': 'Decathlon'},
        'category': 'other',
        'balance_payment': True,
        'feeds_admin_id': 'feeds-admin-id-1',
        'meta_info': {
            'promocode_params': {
                'text': 'Открыть сертификат',
                'url': 'https://decathlon.digift.ru/card/show/code/{}',
            },
        },
    }

    await stq_runner.contractor_merch_purchase.call(
        task_id=DEFAULT_TASK_ID,
        kwargs={**DEFAULT_STQ_KWARGS, 'feed_payload': feed_payload},
    )
    assert mock_driver_profiles.driver_profiles.times_called == 1

    expected_template = {
        'alert': False,
        'format': 'Markdown',
        'important': True,
        'text': (
            'Default text with number, here it is: '
            '[Открыть сертификат]'
            '(https://decathlon.digift.ru/card/show/code/100/500)'
        ),
        'title': 'Оффер с сертификатом: succ',
        'type': 'newsletter',
    }

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': f'park_id_driver1'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': expected_template,
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.parametrize(
    'expect_fail, expected_message, fulfilled',
    [
        pytest.param(
            False,
            'Default text with number, here it is: WSFWF11412',
            True,
            marks=(
                pytest.mark.config(
                    CONTRACTOR_MERCH_SEND_DRIVER_NOTIFICATIONS={
                        'fulfilled': 'send_if_can',
                        'failed': 'send',
                    },
                ),
            ),
            id='fulfilled, with fallback',
        ),
        pytest.param(
            True,
            'Default text with number, here it is: WSFWF11412',
            True,
            marks=(
                pytest.mark.config(
                    CONTRACTOR_MERCH_SEND_DRIVER_NOTIFICATIONS={
                        'fulfilled': 'send',
                        'failed': 'send',
                    },
                ),
            ),
            id='fulfilled, no fallback',
        ),
        pytest.param(
            False,
            'marketplace_is_disabled_for_park-tr',
            False,
            marks=(
                pytest.mark.config(
                    CONTRACTOR_MERCH_DISABLED_PARK_IDS=[
                        'park_id',
                        'park1',
                        'some_other_id',
                    ],
                    CONTRACTOR_MERCH_SEND_DRIVER_NOTIFICATIONS={
                        'fulfilled': 'send',
                        'failed': 'send_if_can',
                    },
                ),
            ),
            id='failed, with fallback',
        ),
        pytest.param(
            True,
            'marketplace_is_disabled_for_park-tr',
            False,
            marks=(
                pytest.mark.config(
                    CONTRACTOR_MERCH_DISABLED_PARK_IDS=[
                        'park_id',
                        'park1',
                        'some_other_id',
                    ],
                    CONTRACTOR_MERCH_SEND_DRIVER_NOTIFICATIONS={
                        'fulfilled': 'send',
                        'failed': 'send',
                    },
                ),
            ),
            id='failed, no fallback',
        ),
    ],
)
@pytest.mark.pgsql('contractor_merch', files=['offer_with_few_promocodes.sql'])
async def test_driver_wall_fallback(
        stq_runner,
        mockserver,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
        expect_fail,
        expected_message,
        fulfilled,
):
    @mockserver.json_handler('/driver-wall/internal/driver-wall/v1/add')
    def _driver_wall(request):
        return mockserver.make_response(status=500)

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp3',
            'accept_language': 'en_GB',
            'price': '120',
            'price_with_currency': {'value': '120', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'f2',
                'balance_payment': True,
                'partner': {'name': 'Apple'},
                'title': 'Gift card (1000 rub)',
                'meta_info': {},
            },
        },
        expect_fail=expect_fail,
    )
    if fulfilled:
        assert mock_driver_profiles.driver_profiles.times_called == 1
    else:
        assert mock_driver_profiles.driver_profiles.times_called == 0

    assert _driver_wall.times_called >= 1
    assert (
        _driver_wall.next_call()['request'].json['template']['text']
        == expected_message
    )


PRICE_ZERO_STQ_KWARGS: dict = copy.deepcopy(DEFAULT_STQ_KWARGS)
PRICE_ZERO_STQ_KWARGS['feed_payload']['price'] = '0'
PRICE_ZERO_STQ_KWARGS['price'] = '0'
PRICE_ZERO_STQ_KWARGS['price_with_currency']['value'] = '0'
PRICE_ZERO_CALL_ARGS = dict(
    task_id=DEFAULT_TASK_ID, kwargs=PRICE_ZERO_STQ_KWARGS,
)

PRICE_ZERO_VOUCHER = {
    'id': 'idemp1',
    'park_id': 'park_id',
    'driver_id': 'driver1',
    'idempotency_token': 'idemp1',
    'price': decimal.Decimal(
        PRICE_ZERO_STQ_KWARGS['price_with_currency']['value'],
    ),
    'currency': 'RUB',
    'promocode_id': 'p1',
    'feeds_admin_id': 'feeds-admin-id-1',
    'feed_id': 'some_id',
    'status': 'fulfilled',
    'status_reason': None,
}


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize(
    'balance', [pytest.param('-100'), pytest.param('0'), pytest.param('100')],
)
async def test_price_zero_voucher(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        balance,
):
    mock_fleet_transactions_api.balance = balance
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(**PRICE_ZERO_CALL_ARGS)

    assert util.get_vouchers(cursor) == [PRICE_ZERO_VOUCHER]
