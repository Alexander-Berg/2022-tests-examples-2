import datetime as dt
import uuid

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import scheduled_slots_tools

_SLOT_ID_OLD = uuid.UUID('a936b353-fcda-4b7a-b569-a7fb855819dd')
_OFFER_IDENTITY_OLD = {'slot_id': str(_SLOT_ID_OLD), 'rule_version': 1}

_SLOT_ID_OLD_2 = uuid.UUID('b7ae5704-cbce-4f67-9a72-c128bad3e63f')
_OFFER_IDENTITY_OLD_2 = {'slot_id': str(_SLOT_ID_OLD_2), 'rule_version': 1}

_SLOT_ID_OLD_3 = uuid.UUID('9fc36842-1d90-4b68-b066-c05cd618f3df')
_OFFER_IDENTITY_OLD_3 = {'slot_id': str(_SLOT_ID_OLD_3), 'rule_version': 1}

_SLOT_ID_OLD_4 = uuid.UUID('17da0221-fbbf-4312-8dc0-bec50185bdaf')
_OFFER_IDENTITY_OLD_4 = {'slot_id': str(_SLOT_ID_OLD_4), 'rule_version': 1}

_SLOT_ID_OLD_5 = uuid.UUID('4040d7d4-849a-4e40-b59a-d8399dd1077b')
_OFFER_IDENTITY_OLD_5 = {'slot_id': str(_SLOT_ID_OLD_5), 'rule_version': 1}

_SLOT_ID_NEW = uuid.UUID('9bea2686-05d0-4fbc-aef6-525dac74fabd')
_OFFER_IDENTITY_NEW = {'slot_id': str(_SLOT_ID_NEW), 'rule_version': 2}

_SLOT_ID_NEW_2 = uuid.UUID('6acef1cc-5e4d-4326-940e-8eff1ada4494')
_OFFER_IDENTITY_NEW_2 = {'slot_id': str(_SLOT_ID_NEW_2), 'rule_version': 2}

_CHANGE_REQUEST_OLD_TO_NEW = {
    'slot_id': str(_SLOT_ID_OLD),
    'new_offer_info': {
        'identity': _OFFER_IDENTITY_NEW,
        'time_range': {
            'begin': '2021-02-04T17:00:00+00:00',
            'end': '2021-02-04T18:00:00+00:00',
        },
    },
}

_CHANGE_REQUEST_OLD_TO_NEW_2 = {
    'slot_id': str(_SLOT_ID_OLD_2),
    'new_offer_info': {
        'identity': _OFFER_IDENTITY_NEW_2,
        'time_range': {
            'begin': '2021-02-04T17:00:00+00:00',
            'end': '2021-02-04T18:00:00+00:00',
        },
    },
}

_CANCEL_REQUEST_OLD = {'slot_id': str(_SLOT_ID_OLD)}
_CANCEL_REQUEST_OLD_2 = {'slot_id': str(_SLOT_ID_OLD_2)}
_CANCEL_REQUEST_OLD_3 = {'slot_id': str(_SLOT_ID_OLD_3)}
_CANCEL_REQUEST_OLD_5 = {'slot_id': str(_SLOT_ID_OLD_5)}

_DRIVER_PROFILE_1 = driver.Profile('parkid1_uuid1')
_DRIVER_PROFILE_2 = driver.Profile('parkid2_uuid2')


async def logistic_change_offers(
        taxi_driver_mode_subscription, changed, cancelled,
):
    request = {'changed': changed, 'cancelled': cancelled}

    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET}

    return await taxi_driver_mode_subscription.post(
        'v1/logistic-workshifts/slots/change-offers',
        json=request,
        headers=headers,
    )


@pytest.mark.parametrize(
    'requested_changed, requested_cancelled, '
    'expected_scheduled_slots_meta_old, expected_scheduled_slots_meta_new, '
    'expected_changed_result, '
    'expected_cancelled_result, '
    'expected_scheduled_slots',
    [
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW],
            [],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [(_SLOT_ID_NEW.hex, None)],
            [
                {
                    'new_identity': _OFFER_IDENTITY_NEW,
                    'slot_id': str(_SLOT_ID_OLD),
                    'status': 'success',
                },
            ],
            [],
            [],
            id='change (and close) not existing slot',
        ),
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW],
            [],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [(_SLOT_ID_NEW.hex, None)],
            [
                {
                    'new_identity': _OFFER_IDENTITY_NEW,
                    'slot_id': str(_SLOT_ID_OLD),
                    'status': 'success',
                },
            ],
            [],
            [],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex, None,
                        ),
                    ],
                ),
            ],
            id='close existing not closed slot',
        ),
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW],
            [],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2020, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [(_SLOT_ID_NEW.hex, None)],
            [
                {
                    'new_identity': _OFFER_IDENTITY_NEW,
                    'slot_id': str(_SLOT_ID_OLD),
                    'status': 'success',
                },
            ],
            [],
            [],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex,
                            dt.datetime(
                                2020, 5, 5, 10, 1, tzinfo=dt.timezone.utc,
                            ),
                        ),
                    ],
                ),
            ],
            id='do nothing on existing closed slot (change request)',
        ),
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW],
            [],
            [(_SLOT_ID_OLD.hex, None)],
            [(_SLOT_ID_NEW.hex, None)],
            [{'slot_id': str(_SLOT_ID_OLD), 'status': 'already_started'}],
            [],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 5, 5, 12, 1, tzinfo=dt.timezone.utc),
                    'some_mode',
                    _OFFER_IDENTITY_OLD,
                ),
            ],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _SLOT_ID_OLD.hex,
                            'some_mode',
                            _OFFER_IDENTITY_OLD,
                            dt.datetime(
                                2021, 5, 5, 10, 0, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 5, 5, 12, 1, tzinfo=dt.timezone.utc,
                            ),
                            'some_quota2',
                            1,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex,
                        ),
                    ],
                ),
            ],
            id='already started slot (change request)',
        ),
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW],
            [],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [(_SLOT_ID_NEW.hex, None)],
            [
                {
                    'slot_id': str(_SLOT_ID_OLD),
                    'new_identity': _OFFER_IDENTITY_NEW,
                    'status': 'success',
                },
            ],
            [],
            [
                (
                    _SLOT_ID_NEW.hex,
                    dt.datetime(2021, 2, 4, 17, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 2, 4, 18, 0, tzinfo=dt.timezone.utc),
                    'some_mode_1',
                    _OFFER_IDENTITY_NEW,
                ),
                (
                    _SLOT_ID_NEW.hex,
                    dt.datetime(2021, 2, 4, 17, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 2, 4, 18, 0, tzinfo=dt.timezone.utc),
                    'some_mode_2',
                    _OFFER_IDENTITY_NEW,
                ),
            ],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _SLOT_ID_OLD.hex,
                            'some_mode_1',
                            _OFFER_IDENTITY_OLD,
                            dt.datetime(
                                2021, 5, 5, 20, 0, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 5, 5, 22, 0, tzinfo=dt.timezone.utc,
                            ),
                            'some_quota2',
                            1,
                        ),
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _SLOT_ID_OLD.hex,
                            'some_mode_2',
                            _OFFER_IDENTITY_OLD,
                            dt.datetime(
                                2021, 5, 5, 20, 0, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 5, 5, 22, 0, tzinfo=dt.timezone.utc,
                            ),
                            'some_quota2',
                            1,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex,
                        ),
                    ],
                ),
            ],
            id='existing slots updated',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [],
            [],
            [{'slot_id': str(_SLOT_ID_OLD), 'status': 'success'}],
            [],
            id='cancel not existing slot',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [],
            [],
            [{'slot_id': str(_SLOT_ID_OLD), 'status': 'success'}],
            [],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex, None,
                        ),
                    ],
                ),
            ],
            id='cancel existing not closed slot',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2020, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [],
            [],
            [{'slot_id': str(_SLOT_ID_OLD), 'status': 'success'}],
            [],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex,
                            dt.datetime(
                                2020, 5, 5, 10, 1, tzinfo=dt.timezone.utc,
                            ),
                        ),
                    ],
                ),
            ],
            id='do nothing on existing closed slot (cancel request)',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD],
            [(_SLOT_ID_OLD.hex, None)],
            [],
            [],
            [{'slot_id': str(_SLOT_ID_OLD), 'status': 'already_started'}],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 5, 5, 12, 1, tzinfo=dt.timezone.utc),
                    'some_mode',
                    _OFFER_IDENTITY_OLD,
                ),
            ],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _SLOT_ID_OLD.hex,
                            'some_mode',
                            _OFFER_IDENTITY_OLD,
                            dt.datetime(
                                2021, 5, 5, 10, 0, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 5, 5, 12, 1, tzinfo=dt.timezone.utc,
                            ),
                            'some_quota2',
                            1,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex,
                        ),
                    ],
                ),
            ],
            id='already started slot (cancel request)',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                ),
            ],
            [],
            [],
            [{'slot_id': str(_SLOT_ID_OLD), 'status': 'success'}],
            [
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 20, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 5, 5, 22, 0, tzinfo=dt.timezone.utc),
                    'some_mode_1',
                    _OFFER_IDENTITY_OLD,
                ),
                (
                    _SLOT_ID_OLD.hex,
                    dt.datetime(2021, 5, 5, 20, 0, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 5, 5, 22, 0, tzinfo=dt.timezone.utc),
                    'some_mode_2',
                    _OFFER_IDENTITY_OLD,
                ),
            ],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _SLOT_ID_OLD.hex,
                            'some_mode_1',
                            _OFFER_IDENTITY_OLD,
                            dt.datetime(
                                2021, 5, 5, 20, 0, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 5, 5, 22, 0, tzinfo=dt.timezone.utc,
                            ),
                            'some_quota2',
                            1,
                        ),
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _SLOT_ID_OLD.hex,
                            'some_mode_2',
                            _OFFER_IDENTITY_OLD,
                            dt.datetime(
                                2021, 5, 5, 20, 0, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 5, 5, 22, 0, tzinfo=dt.timezone.utc,
                            ),
                            'some_quota2',
                            1,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_OLD.hex,
                        ),
                    ],
                ),
            ],
            id='existing slots cancelled',
        ),
    ],
)
@pytest.mark.now('2021-05-05T13:01:00+03:00')
async def test_logistic_workshifts_slots_change(
        taxi_driver_mode_subscription,
        pgsql,
        requested_changed,
        requested_cancelled,
        expected_changed_result,
        expected_cancelled_result,
        expected_scheduled_slots_meta_old,
        expected_scheduled_slots_meta_new,
        expected_scheduled_slots,
):

    response = await logistic_change_offers(
        taxi_driver_mode_subscription, requested_changed, requested_cancelled,
    )

    assert response.status_code == 200

    assert response.json() == {
        'cancelled': expected_cancelled_result,
        'changed': expected_changed_result,
    }

    assert (
        scheduled_slots_tools.get_scheduled_slots_meta(pgsql, _SLOT_ID_OLD.hex)
        == expected_scheduled_slots_meta_old
    )

    assert (
        scheduled_slots_tools.get_scheduled_slots_meta(pgsql, _SLOT_ID_NEW.hex)
        == expected_scheduled_slots_meta_new
    )

    assert (
        scheduled_slots_tools.get_scheduled_slots(pgsql)
        == expected_scheduled_slots
    )


@pytest.mark.parametrize(
    'requested_changed, requested_cancelled, delay, '
    'expected_changed_result, expected_cancelled_result',
    [
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW, _CHANGE_REQUEST_OLD_TO_NEW_2],
            [],
            1,
            [
                {
                    'new_identity': _OFFER_IDENTITY_NEW,
                    'slot_id': str(_SLOT_ID_OLD),
                    'status': 'success',
                },
                {
                    'new_identity': _OFFER_IDENTITY_NEW_2,
                    'slot_id': str(_SLOT_ID_OLD_2),
                    'status': 'success',
                },
            ],
            [],
            id='change - small delay, all pass',
        ),
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW, _CHANGE_REQUEST_OLD_TO_NEW_2],
            [],
            60 * 5,
            [
                {'slot_id': str(_SLOT_ID_OLD), 'status': 'already_started'},
                {
                    'new_identity': _OFFER_IDENTITY_NEW_2,
                    'slot_id': str(_SLOT_ID_OLD_2),
                    'status': 'success',
                },
            ],
            [],
            id='change - 5 minutes delay, one pass, one fail',
        ),
        pytest.param(
            [_CHANGE_REQUEST_OLD_TO_NEW, _CHANGE_REQUEST_OLD_TO_NEW_2],
            [],
            60 * 60,
            [
                {'slot_id': str(_SLOT_ID_OLD), 'status': 'already_started'},
                {'slot_id': str(_SLOT_ID_OLD_2), 'status': 'already_started'},
            ],
            [],
            id='change - 1 hour delay, one pass, both fail',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD, _CANCEL_REQUEST_OLD_2],
            1,
            [],
            [
                {'slot_id': str(_SLOT_ID_OLD), 'status': 'success'},
                {'slot_id': str(_SLOT_ID_OLD_2), 'status': 'success'},
            ],
            id='cancel - small delay, all pass',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD, _CANCEL_REQUEST_OLD_2],
            60 * 5,
            [],
            [
                {'slot_id': str(_SLOT_ID_OLD), 'status': 'already_started'},
                {'slot_id': str(_SLOT_ID_OLD_2), 'status': 'success'},
            ],
            id='cancel - 5 minutes delay, one pass, one fail',
        ),
        pytest.param(
            [],
            [_CANCEL_REQUEST_OLD, _CANCEL_REQUEST_OLD_2],
            60 * 60,
            [],
            [
                {'slot_id': str(_SLOT_ID_OLD), 'status': 'already_started'},
                {'slot_id': str(_SLOT_ID_OLD_2), 'status': 'already_started'},
            ],
            id='cancel - 1 hour delay, one pass, both fail',
        ),
    ],
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_OLD.hex,
            'some_mode',
            _OFFER_IDENTITY_OLD,
            dt.datetime(2021, 5, 5, 10, 3, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 5, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota2',
            1,
        ),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_OLD.hex),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_OLD_2.hex,
            'some_mode',
            _OFFER_IDENTITY_OLD_2,
            dt.datetime(2021, 5, 5, 10, 45, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 5, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota2',
            1,
        ),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_OLD_2.hex),
    ],
)
@pytest.mark.now('2021-05-05T13:01:00+03:00')
async def test_logistic_workshifts_slots_change_config_delay(
        taxi_driver_mode_subscription,
        pgsql,
        taxi_config,
        requested_changed,
        requested_cancelled,
        delay,
        expected_changed_result,
        expected_cancelled_result,
):

    taxi_config.set_values(
        {
            'DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS': {
                'slot_change_delay_s': delay,
            },
        },
    )
    await taxi_driver_mode_subscription.invalidate_caches()

    response = await logistic_change_offers(
        taxi_driver_mode_subscription, requested_changed, requested_cancelled,
    )

    assert response.status_code == 200

    assert response.json() == {
        'cancelled': expected_cancelled_result,
        'changed': expected_changed_result,
    }


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_OLD.hex,
            'some_mode',
            _OFFER_IDENTITY_OLD,
            dt.datetime(2021, 5, 5, 10, 3, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 5, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota1',
            10,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_OLD_2.hex,
            'some_mode',
            _OFFER_IDENTITY_OLD_2,
            dt.datetime(2021, 5, 6, 10, 45, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 6, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota2_3',
            2,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_OLD_3.hex,
            'some_mode',
            _OFFER_IDENTITY_OLD_3,
            dt.datetime(2021, 5, 7, 10, 45, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 7, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota2_3',
            2,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_OLD_4.hex,
            'some_mode',
            _OFFER_IDENTITY_OLD_4,
            dt.datetime(2021, 5, 8, 10, 45, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 8, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota4',
            42,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_OLD_5.hex,
            'some_mode',
            _OFFER_IDENTITY_OLD_5,
            dt.datetime(2021, 5, 9, 10, 45, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 9, 12, 10, tzinfo=dt.timezone.utc),
            'some_quota5',
            54,
        ),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_OLD.hex),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_OLD_2.hex),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_OLD_3.hex),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_OLD_4.hex),
        scheduled_slots_tools.make_insert_slot_meta_query(_SLOT_ID_OLD_5.hex),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_OLD.hex, _DRIVER_PROFILE_1, True,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_OLD_2.hex, _DRIVER_PROFILE_1, False,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_OLD_3.hex, _DRIVER_PROFILE_1, False,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_OLD_4.hex, _DRIVER_PROFILE_1, False,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_OLD_5.hex, _DRIVER_PROFILE_1, False,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_OLD.hex, _DRIVER_PROFILE_2, False,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            'some_mode', _SLOT_ID_OLD_5.hex, _DRIVER_PROFILE_2, False,
        ),
    ],
)
@pytest.mark.now('2021-05-05T13:01:00+03:00')
async def test_logistic_workshifts_slots_cancel_reservations(
        taxi_driver_mode_subscription, pgsql,
):

    response = await logistic_change_offers(
        taxi_driver_mode_subscription,
        [],
        [
            _CANCEL_REQUEST_OLD,
            _CANCEL_REQUEST_OLD_2,
            _CANCEL_REQUEST_OLD_3,
            _CANCEL_REQUEST_OLD_5,
        ],
    )

    assert response.status_code == 200
    assert response.json() == {
        'cancelled': [
            {'slot_id': str(_SLOT_ID_OLD), 'status': 'success'},
            {'slot_id': str(_SLOT_ID_OLD_2), 'status': 'success'},
            {'slot_id': str(_SLOT_ID_OLD_3), 'status': 'success'},
            {'slot_id': str(_SLOT_ID_OLD_5), 'status': 'success'},
        ],
        'changed': [],
    }

    driver1_reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_1,
    )
    assert driver1_reservations == [
        (
            _SLOT_ID_OLD_4.hex,
            dt.datetime(2021, 5, 8, 10, 45, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 5, 8, 12, 10, tzinfo=dt.timezone.utc),
            'some_mode',
            _OFFER_IDENTITY_OLD_4,
            'some_quota4',
            42,
            None,
            None,
        ),
    ]

    driver2_reservations = scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _DRIVER_PROFILE_2,
    )

    assert driver2_reservations == []

    assert scheduled_slots_tools.get_scheduled_quota(pgsql, 'some_quota1') == [
        ('some_quota1', 9),
    ]
    assert scheduled_slots_tools.get_scheduled_quota(
        pgsql, 'some_quota2_3',
    ) == [('some_quota2_3', 0)]
    assert scheduled_slots_tools.get_scheduled_quota(pgsql, 'some_quota4') == [
        ('some_quota4', 42),
    ]
    assert scheduled_slots_tools.get_scheduled_quota(pgsql, 'some_quota5') == [
        ('some_quota5', 52),
    ]
