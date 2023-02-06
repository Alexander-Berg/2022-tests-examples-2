import datetime as dt
from email import header
import json

import pytest

from tests_eats_place_subscriptions import utils

HANDLER = '/internal/eats-place-subscriptions/v1/place/create-subscription'


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
@pytest.mark.experiments3(filename='subscriptions_enabled.json')
@pytest.mark.parametrize(
    'is_exp_enabled, tariff, is_trial',
    [
        pytest.param(True, 'business', True, id='exp_enabled'),
        pytest.param(False, 'free', False, id='exp_disabled'),
    ],
)
@pytest.mark.parametrize(
    'activated_at, valid_until',
    [
        pytest.param(
            dt.datetime(2020, 5, 15, 15, 0, tzinfo=utils.MSC_TIMEZONE),
            dt.datetime(2020, 6, 14, 0, 0, tzinfo=utils.MSC_TIMEZONE),
            id='2020-05-15',
        ),
        pytest.param(
            dt.datetime(2020, 12, 23, 10, 0, tzinfo=utils.MSC_TIMEZONE),
            dt.datetime(2021, 1, 22, 0, 0, tzinfo=utils.MSC_TIMEZONE),
            id='2020-12-23',
        ),
    ],
)
async def test_204(
        mocked_time,
        pg_realdict_cursor,
        taxi_eats_place_subscriptions,
        # parametrize params
        is_exp_enabled,
        tariff,
        is_trial,
        activated_at,
        valid_until,
):
    mocked_time.set(activated_at)

    new_place_id = 999
    business_type = 'restaurant' if is_exp_enabled else 'shop'
    response = await taxi_eats_place_subscriptions.post(
        HANDLER, json=_generate_request(new_place_id, business_type),
    )
    assert response.status_code == 204

    db_subscription = await utils.db_get_sub_with_place_dict(
        pg_realdict_cursor, new_place_id,
    )
    revision = db_subscription['revision']
    assert db_subscription == _generate_expected_subscription(
        new_place_id,
        tariff,
        is_trial,
        activated_at,
        valid_until,
        business_type,
        revision,
    )
    db_change_log = await utils.db_get_change_log_dict(
        pg_realdict_cursor, revision,
    )
    _check_change_log(
        db_change_log,
        _generate_expected_change_log(
            new_place_id,
            tariff,
            is_trial,
            activated_at,
            valid_until,
            business_type,
        ),
    )


@pytest.mark.pgsql(
    'eats_place_subscriptions', files=['db_places_subscriptions.sql'],
)
async def test_409(pg_realdict_cursor, taxi_eats_place_subscriptions):
    existing_place_id = 123

    old_subscription = await utils.db_get_sub_with_place_dict(
        pg_realdict_cursor, existing_place_id,
    )

    response = await taxi_eats_place_subscriptions.post(
        HANDLER, json=_generate_request(existing_place_id),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'already_exists',
        'message': (
            f'Subscription already exists for place_id={existing_place_id}'
        ),
    }

    db_subscription = await utils.db_get_sub_with_place_dict(
        pg_realdict_cursor, existing_place_id,
    )
    assert db_subscription == old_subscription


@pytest.mark.experiments3(filename='subscriptions_enabled.json')
async def test_custom_valid_until_and_tariff(
        pg_realdict_cursor, taxi_eats_place_subscriptions, mocked_time,
):
    place_id = 123
    valid_until = dt.datetime(2020, 6, 1, 0, 0, tzinfo=utils.MSC_TIMEZONE)
    valid_until_str = '2020-06-01T00:00:00.000+0300'
    tariff = 'business'
    now = dt.datetime(2020, 5, 15, 11, 0, tzinfo=utils.MSC_TIMEZONE)
    mocked_time.set(now)

    response = await taxi_eats_place_subscriptions.post(
        HANDLER,
        json=_generate_request(
            place_id, valid_until=valid_until_str, tariff=tariff,
        ),
    )
    assert response.status_code == 204

    db_subscription = await utils.db_get_sub_with_place_dict(
        pg_realdict_cursor, place_id,
    )
    revision = db_subscription['revision']
    assert db_subscription == _generate_expected_subscription(
        place_id, tariff, True, now, valid_until, revision=revision,
    )
    db_change_log = await utils.db_get_change_log_dict(
        pg_realdict_cursor, revision,
    )
    _check_change_log(
        db_change_log,
        _generate_expected_change_log(
            place_id, tariff, True, now, valid_until,
        ),
    )


def _generate_request(
        place_id, business_type='restaurant', valid_until=None, tariff=None,
):
    result = {
        'place_id': place_id,
        'business_type': business_type,
        'country_code': 'ru',
        'region_id': 1,
        'time_zone': 'Europe/Moscow',
        'inn': '1234567890',
    }
    if valid_until:
        result['subscription_valid_until'] = valid_until
    if tariff:
        result['tariff_type'] = tariff
    return result


def _generate_expected_subscription(
        place_id,
        tariff,
        is_trial,
        activated_at,
        valid_until,
        business_type='restaurant',
        revision=None,
):
    return {
        'place_id': place_id,
        'tariff': tariff,
        'next_tariff': None,
        'is_trial': is_trial,
        'activated_at': activated_at,
        'valid_until': valid_until,
        'is_partner_updated': False,
        'business_type': business_type,
        'country_code': 'ru',
        'region_id': 1,
        'timezone': 'Europe/Moscow',
        'inn': '1234567890',
        'revision': revision,
    }


def _generate_expected_change_log(
        place_id,
        tariff,
        is_trial,
        activated_at,
        valid_until,
        business_type='restaurant',
):
    return {
        'place_id': place_id,
        'change_type': 'create-subscription',
        'author': 'service-unknown',
        'state_before': None,
        'state_after': {
            'place_id': place_id,
            'tariff': tariff,
            'next_tariff': None,
            'is_trial': is_trial,
            'activated_at': activated_at.isoformat(),
            'valid_until': valid_until.isoformat(),
            'is_partner_updated': False,
        },
    }


def _check_change_log(db_change_log, expected):
    assert db_change_log['change_type'] == expected['change_type']
    assert db_change_log['author'] == expected['author']
    if expected['state_before']:
        assert (
            expected['state_before'].items()
            <= db_change_log['state_before'].items()
        )
    else:
        assert db_change_log['state_before'] is None
    if expected['state_after']:
        assert (
            expected['state_after'].items()
            <= db_change_log['state_after'].items()
        )
    else:
        assert db_change_log['state_after'] is None
