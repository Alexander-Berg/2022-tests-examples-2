import pytest

from tests_coupons import util

DB_NAME = 'user_referrals'

PHONE_ID = '5bbb5faf15870bd76635d5e2'
YANDEX_UID = '4001'


def build_request(coupon):
    return util.mock_request_activate(
        [YANDEX_UID], YANDEX_UID, coupon, phone_id=PHONE_ID,
    )


def get_coupon_events(pgsql, coupon):
    db_cursor = pgsql[DB_NAME].cursor()
    db_cursor.execute(
        f'SELECT * FROM coupons.events WHERE coupon = \'{coupon}\'',
    )
    columns = [desc[0] for desc in db_cursor.description]
    rows = list(db_cursor)
    return [dict(zip(columns, row)) for row in rows]


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(COUPONS_REPORTED_EVENT_TYPES=['activate'])
@pytest.mark.parametrize(
    'coupon, expected_status, event_extra',
    [
        ('firstpromocode', 'valid', {'status': 'valid'}),
        (
            'myyacode',
            'invalid',
            {'status': 'invalid', 'error_code': 'ERROR_INVALID_CODE'},
        ),
    ],
)
async def test_basic(
        taxi_coupons,
        local_services_card,
        pgsql,
        testpoint,
        coupon,
        expected_status,
        event_extra,
):
    @testpoint('activate-event-reported')
    def event_reported(data):
        pass

    response = await util.make_activate_request(
        taxi_coupons, data=build_request(coupon),
    )
    assert response.status_code == 200
    assert response.json()['coupon']['status'] == expected_status

    await event_reported.wait_call()

    events = get_coupon_events(pgsql, coupon)
    assert len(events) == 1

    event = events[0]
    assert event['moment'].isoformat() == '2019-03-06T11:30:00+03:00'
    assert event['type'] == 'activate'
    assert event['phone_id'] == PHONE_ID
    assert event['yandex_uid'] == YANDEX_UID
    assert event['extra'] == event_extra
