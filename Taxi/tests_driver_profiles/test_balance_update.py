import datetime

import pytest
import pytz


ENDPOINT = '/internal/v1/contractor/balance'


@pytest.fixture()
def _get_driver(mongodb):
    return lambda park_id, contractor_profile_id: mongodb.dbdrivers.find_one(
        dict(park_id=park_id, driver_id=contractor_profile_id),
    )


def get_unchanged(doc):
    return {
        k: v
        for (k, v) in doc.items()
        if k
        not in {
            'balance',
            'billing_balance_last_entry_id',
            'updated_ts',
            'modified_date',
            'last_transaction_date',
        }
    }


@pytest.mark.parametrize(
    (
        'park_id',
        'contractor_profile_id',
        'balance_request',
        'expected_response_body',
    ),
    [
        (
            'park1',
            'driver1',
            {
                'balance': 20.0,
                'balance_last_entry_id': 1553500460166,
                'balance_changed_at': '2021-05-18T11:12:13+03:00',
            },
            {
                'balance': 17.1426,
                'balance_limit': 12.0,
                'balance_deny_onlycard': True,
            },
        ),
        (
            'park2',
            'driver2',
            {
                'balance': 20.0,
                'balance_last_entry_id': 1553500460166,
                'balance_changed_at': '2021-05-18T11:12:13+03:00',
            },
            {'balance': 0, 'balance_limit': 0, 'balance_deny_onlycard': False},
        ),
    ],
)
async def test_balance_success(
        taxi_driver_profiles,
        _get_driver,
        park_id,
        contractor_profile_id,
        balance_request,
        expected_response_body,
):
    driver_before = _get_driver(park_id, contractor_profile_id)

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        params=dict(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
        json=balance_request,
    )
    assert response.status_code == 200

    driver_after = _get_driver(park_id, contractor_profile_id)

    assert response.json() == expected_response_body
    assert get_unchanged(driver_before) == get_unchanged(driver_after)
    assert driver_after['balance'] == balance_request['balance']
    assert (
        driver_after['billing_balance_last_entry_id']
        == balance_request['balance_last_entry_id']
    )
    assert driver_after['last_transaction_date'] == datetime.datetime.strptime(
        balance_request['balance_changed_at'], '%Y-%m-%dT%H:%M:%S%z',
    ).astimezone(pytz.utc).replace(tzinfo=None)
    assert driver_after['updated_ts'] != driver_before['updated_ts']
    assert driver_after['modified_date'] != driver_before['modified_date']


@pytest.mark.parametrize(
    ('park_id', 'contractor_profile_id', 'balance_request'),
    [
        (
            'park1',
            'driver1',
            {
                'balance': 20.0,
                'balance_last_entry_id': 1543500460165,
                'balance_changed_at': '2021-05-18T11:12:13+03:00',
            },
        ),
        (
            'park0',
            'driver1',
            {
                'balance': 20.0,
                'balance_last_entry_id': 1543500460165,
                'balance_changed_at': '2021-05-18T11:12:13+03:00',
            },
        ),
        (
            'park1',
            'driver0',
            {
                'balance': 20.0,
                'balance_last_entry_id': 1543500460165,
                'balance_changed_at': '2021-05-18T11:12:13+03:00',
            },
        ),
    ],
)
async def test_balance_conflict(
        taxi_driver_profiles,
        _get_driver,
        park_id,
        contractor_profile_id,
        balance_request,
):
    driver_before = _get_driver(park_id, contractor_profile_id)

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        params=dict(
            park_id=park_id, contractor_profile_id=contractor_profile_id,
        ),
        json=balance_request,
    )
    assert response.status_code == 409

    driver_after = _get_driver(park_id, contractor_profile_id)

    assert driver_before == driver_after
