import pytest


def make_auth(driver_profile_id):
    park_id, profile_id = driver_profile_id.split('_')
    return {
        'User-Agent': 'Taximeter 8.80 (562)',
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': profile_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.77 (456)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
    }


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_base(taxi_grocery_performer_mentorship, db):
    response = await taxi_grocery_performer_mentorship.post(
        '/driver/v1/mentorship/v1/mentorship/ask',
        headers=make_auth('123_101'),
    )
    assert response.status == 200
    assert db.check_mentorship('123_101') == {
        'newbie_id': '123_101',
        'newbie_shift_id': None,
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'pending',
    }
    response = await taxi_grocery_performer_mentorship.post(
        '/driver/v1/mentorship/v1/mentorship/ask',
        headers=make_auth('123_101'),
    )
    assert response.status == 200


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_two_shifts(taxi_grocery_performer_mentorship, db):
    response = await taxi_grocery_performer_mentorship.post(
        '/driver/v1/mentorship/v1/mentorship/ask',
        headers=make_auth('123_102'),
    )
    assert response.status == 200
    assert db.check_mentorship('123_102') == {
        'newbie_id': '123_102',
        'newbie_shift_id': None,
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'pending',
    }


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_closed(taxi_grocery_performer_mentorship, db):
    response = await taxi_grocery_performer_mentorship.post(
        '/driver/v1/mentorship/v1/mentorship/ask',
        headers=make_auth('123_103'),
    )
    assert response.status == 200
    assert db.check_mentorship('123_103') == {
        'newbie_id': '123_103',
        'newbie_shift_id': None,
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'pending',
    }


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_in_progress(taxi_grocery_performer_mentorship, db):
    response = await taxi_grocery_performer_mentorship.post(
        '/driver/v1/mentorship/v1/mentorship/ask',
        headers=make_auth('123_104'),
    )
    assert response.status == 200
    assert db.check_mentorship('123_104') == {
        'newbie_id': '123_104',
        'newbie_shift_id': None,
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'pending',
    }


@pytest.mark.pgsql('grocery_performer_mentorship', files=['shifts.sql'])
async def test_bad(taxi_grocery_performer_mentorship, db):
    response = await taxi_grocery_performer_mentorship.post(
        '/driver/v1/mentorship/v1/mentorship/ask',
        headers=make_auth('111_111'),
    )
    assert response.status == 200
    assert db.check_mentorship('111_111') == {
        'newbie_id': '111_111',
        'newbie_shift_id': None,
        'mentor_id': None,
        'mentor_shift_id': None,
        'status': 'pending',
    }
