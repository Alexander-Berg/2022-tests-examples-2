import pytest

from taxi_billing_subventions.common import db as common_db


@pytest.mark.parametrize(
    'city_id, expected_city_json',
    [
        ('Москва', 'city_moscow.json'),
        ('Учкекен', 'city_uchkeken.json'),
        ('Вологда', 'city_vologda.json'),
    ],
)
@pytest.mark.filldb(cities='for_test_fetch_city')
async def test_fetch_city(db, load_py_json, city_id, expected_city_json):
    expected_city = load_py_json(expected_city_json)
    city = await common_db.cities.fetch_city(
        database=db, city_id=city_id, log_extra=None,
    )
    assert city == expected_city


async def test_fetch_city_not_found(db, load_json):
    with pytest.raises(common_db.cities.CityNotFoundError):
        await common_db.cities.fetch_city(
            database=db, city_id='This city never existed', log_extra=None,
        )
