import pytest

from tests_contractor_merch import util

TRANSLATIONS = util.STQ_TRANSLATIONS

DEFAULT_LOCALE = 'en'
DEFAULT_TASK_ID = 'some_task_id'
DEFAULT_FEEDS_ADMIN_ID = 'feeds-admin-id-1'
DEFAULT_PAYLOAD = {
    'feeds_admin_id': DEFAULT_FEEDS_ADMIN_ID,
    'category': 'tire',
    'balance_payment': True,
    'title': 'Gift card (tire)',
    'name': 'RRRR',
    'partner': {'name': 'Apple'},
    'meta_info': {'display_on_main_screen': True},
}
DEFAULT_STQ_KWARGS = {
    'park_id': 'park_id',
    'driver_id': 'driver_id',
    'idempotency_token': 'idemp1',
    'feed_id': 'feed-id-1',
    'accept_language': 'en_GB',
    'price': '300',
    'price_with_currency': {'value': '300', 'currency': 'RUB'},
    'feed_payload': DEFAULT_PAYLOAD,
    'feed_locale': DEFAULT_LOCALE,
}
DEFAULT_CALL_ARGS = dict(task_id=DEFAULT_TASK_ID, kwargs=DEFAULT_STQ_KWARGS)


def _check_database_state(pgsql, stq_kwargs, expected_payload=None):
    result = util.get_feeds_history(
        pgsql['contractor_merch'].cursor(),
        stq_kwargs['feed_id'],
        DEFAULT_LOCALE,
    )
    if expected_payload is None:
        assert not result
        return
    assert len(result) == 1
    assert result[0]['feed_payload'] == expected_payload


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
async def test_feeds_history_is_saved(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_wall,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    _check_database_state(pgsql, DEFAULT_STQ_KWARGS)
    await stq_runner.contractor_merch_purchase.call(**DEFAULT_CALL_ARGS)
    assert mock_driver_profiles.driver_profiles.times_called == 1
    _check_database_state(pgsql, DEFAULT_STQ_KWARGS, DEFAULT_PAYLOAD)


NO_EXTRA_STQ_KWARGS = {
    **DEFAULT_STQ_KWARGS,
    'price': '3.1415',
    'price_with_currency': {'value': '3.1415', 'currency': 'RUB'},
    'feed_payload': {
        'feeds_admin_id': DEFAULT_FEEDS_ADMIN_ID,
        'category': 'tire',
        'balance_payment': True,
        'title': 'Gift card (tire)',
        'partner': {'name': 'Apple'},
        'meta_info': {},
    },
}
NO_EXTRA_CALL_ARGS = dict(task_id=DEFAULT_TASK_ID, kwargs=NO_EXTRA_STQ_KWARGS)


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
async def test_no_saving_if_no_extra(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_wall,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    assert (
        NO_EXTRA_CALL_ARGS['kwargs']['price_with_currency']
        != DEFAULT_CALL_ARGS['kwargs']['price_with_currency']
    )
    _check_database_state(pgsql, DEFAULT_STQ_KWARGS)
    await stq_runner.contractor_merch_purchase.call(**NO_EXTRA_CALL_ARGS)
    assert mock_driver_profiles.driver_profiles.times_called == 1
    _check_database_state(pgsql, DEFAULT_STQ_KWARGS)


SIMILAR_STQ_KWARGS = {
    **DEFAULT_STQ_KWARGS,
    'price': '3.1415',
    'price_with_currency': {'value': '3.1415', 'currency': 'RUB'},
    'feed_payload': {
        'feeds_admin_id': DEFAULT_FEEDS_ADMIN_ID,
        'category': 'tire',
        'balance_payment': True,
        'title': 'Gift card (tire)',
        'partner': {'name': 'Apple'},
        'meta_info': {'display_on_main_screen': True},
        'definitely_an_extra_field': 'some_garbage',
    },
}
SIMILAR_CALL_ARGS = dict(task_id=DEFAULT_TASK_ID, kwargs=SIMILAR_STQ_KWARGS)


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
async def test_feeds_history_is_not_overwritten(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_wall,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    _check_database_state(pgsql, DEFAULT_STQ_KWARGS)
    await stq_runner.contractor_merch_purchase.call(**DEFAULT_CALL_ARGS)

    _check_database_state(pgsql, DEFAULT_STQ_KWARGS, DEFAULT_PAYLOAD)
    await stq_runner.contractor_merch_purchase.call(**SIMILAR_CALL_ARGS)

    assert mock_driver_profiles.driver_profiles.times_called == 2
    _check_database_state(pgsql, DEFAULT_STQ_KWARGS, DEFAULT_PAYLOAD)
