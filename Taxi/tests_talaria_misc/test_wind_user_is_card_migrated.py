import pytest


@pytest.mark.pgsql('talaria_misc', files=['users.sql'])
async def test_wind_user_is_card_migrated(taxi_talaria_misc, pgsql):
    wind_user_id = 'wind_user_id'

    response = await taxi_talaria_misc.post(
        '/talaria/v1/wind-user-is-card-migrated',
        json={'wind_user_ids': [wind_user_id]},
    )

    assert response.status_code == 200

    cursor = pgsql['talaria_misc'].cursor()
    cursor.execute(
        f'SELECT card_migrated_at '
        f'FROM talaria_misc.users '
        f'WHERE wind_user_id={wind_user_id};',
    )
    assert cursor.fetchall()[0][0] is not None
