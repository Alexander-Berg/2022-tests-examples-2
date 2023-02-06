import datetime

import psycopg2
import pytest


MOCK_NOW = datetime.datetime(2022, 5, 16, 14, 15, 16)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_constraints(pgsql):
    cursor = pgsql['shuttle_control'].cursor()

    # test check_vfh_id_trigger
    with pytest.raises(psycopg2.DatabaseError):
        cursor.execute(
            """
            INSERT INTO state.passengers
            (booking_id, offer_id, yandex_uid, user_id, shuttle_id, stop_id,
            dropoff_stop_id, origin, locale, created_at, status, ticket,
            finished_at)
            VALUES (
                '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
                '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
                '0123456789',
                'user_id_1',
                1,
                1,
                2,
                'application',
                'ru',
                '2022-05-16T15:00:00',
                'finished',
                '0400',
                '2022-05-16T17:00:00'
            )
            """,
        )
