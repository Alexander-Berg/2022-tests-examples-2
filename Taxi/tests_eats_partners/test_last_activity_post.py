import datetime

import pytest
import pytz

PARTNERS_REQUEST = (123, 1000, 4000, 2000, 3000, 3000, 234, 678, 4000, 3000, 1)

PARTNERS_STATIC = (1, 2, 9000, 9001)
PARTNERS_STATIC_DATES = (
    '2020-01-01T01:01:01+00:00',
    '2020-02-02T02:02:02+00:00',
    '2020-03-03T03:03:03+00:00',
    '2020-04-04T04:04:04+00:00',
)

PARTNERS_STATIC_INSERTED = (1, 2, 2000, 9000, 9001)
PARTNERS_STATIC_INSERTED_DATES = (
    '2020-06-06T06:06:06+00:00',
    '2020-02-02T02:02:02+00:00',
    '2020-06-06T06:06:06+00:00',
    '2020-03-03T03:03:03+00:00',
    '2020-04-04T04:04:04+00:00',
)


def get_sql_data(pgsql):
    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        'SELECT partner_id,last_activity_at'
        ' FROM eats_partners.last_activity'
        ' ORDER BY partner_id',
    )
    return [
        {'partner_id': result[0], 'last_activity_at': result[1]}
        for result in list(cursor)
    ]


@pytest.mark.pgsql('eats_partners', files=['insert_activity.sql'])
async def test_last_activity_post_simple(taxi_eats_partners, pgsql):
    sql_data = get_sql_data(pgsql)
    assert len(PARTNERS_STATIC) == len(sql_data)
    for idx, partner_id in enumerate(PARTNERS_STATIC):
        assert partner_id == sql_data[idx]['partner_id']

    response = await taxi_eats_partners.post(
        '/internal/partners/v1/last-activity',
        json={'partner_ids': [1, 2, 3, 4, 5, 6, 9000, 9001, 9002]},
    )

    assert response.status_code == 200
    partners = response.json()['partners']

    assert len(PARTNERS_STATIC) == len(partners)
    for idx, partner_id in enumerate(PARTNERS_STATIC):
        assert partner_id == partners[idx]['id']
        assert PARTNERS_STATIC_DATES[idx] == partners[idx]['last_activity_at']


@pytest.mark.pgsql('eats_partners', files=['insert_activity.sql'])
async def test_last_activity_post_complex(
        taxi_eats_partners, pgsql, mocked_time, testpoint,
):
    @testpoint('mock_pg_now')
    def mock_pg_now(val):
        pass

    sql_data = get_sql_data(pgsql)
    assert len(PARTNERS_STATIC) == len(sql_data)
    for idx, partner_id in enumerate(PARTNERS_STATIC):
        assert partner_id == sql_data[idx]['partner_id']

    time1 = datetime.datetime(2020, 6, 6, 6, 6, 6, tzinfo=pytz.utc)
    mocked_time.set(time1)

    for partner_id in PARTNERS_REQUEST:
        response = await taxi_eats_partners.post(
            '/internal/partners/v1/log-activity',
            json={},
            params={'partner_id': partner_id},
        )
        assert response.status_code == 200

    response = await taxi_eats_partners.post(
        '/internal/partners/v1/last-activity',
        json={'partner_ids': [1, 2, 3, 4, 5, 6, 2000, 2001, 9000, 9001, 9002]},
    )

    assert response.status_code == 200
    partners = sorted(response.json()['partners'], key=lambda x: x['id'])

    assert len(PARTNERS_STATIC_INSERTED) == len(partners)
    for idx, partner_id in enumerate(PARTNERS_STATIC_INSERTED):
        assert partner_id == partners[idx]['id']
        assert (
            PARTNERS_STATIC_INSERTED_DATES[idx]
            == partners[idx]['last_activity_at']
        )

    response = await taxi_eats_partners.post(
        '/internal/partners/v1/last-activity',
        json={
            'partner_ids': [2, 3, 4, 5, 6, 2000, 2001, 9000, 9001, 9002],
            'later_than': '2020-06-06T06:06:06.000+00:00',
        },
    )
    assert response.status_code == 200
    partners = response.json()['partners']

    assert partners == [
        {'id': 2000, 'last_activity_at': '2020-06-06T06:06:06+00:00'},
    ]
    assert mock_pg_now.has_calls
