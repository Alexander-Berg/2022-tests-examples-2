import pytest

URL = 'invites/v1/membership'
CLUB_NAME = 'yandex_go'
PHONE_ID_JUST_YANDEX_GO = '0'
PHONE_ID_JUST_ACTIVE_CLUBS = '1'
PHONE_ID_MIXED_CLUBS = '2'
PHONE_ID_JUST_INACTIVE_CLUBS = '3'
PHONE_ID_NO_CLUBS = '4'


@pytest.mark.parametrize(
    'data', [None, {}], ids=['none_request', 'empty_request'],
)
async def test_4xx(taxi_invites, data):
    response = await taxi_invites.post(URL, data)
    assert response.status_code == 400


@pytest.mark.pgsql('invites', files=['membership.sql'])
@pytest.mark.parametrize(
    'phone_id,expected_clubs',
    [
        pytest.param(
            PHONE_ID_JUST_YANDEX_GO, {CLUB_NAME}, id='just_yandex_go_club',
        ),
        pytest.param(
            PHONE_ID_JUST_ACTIVE_CLUBS,
            {'active_club_1', 'active_club_2'},
            id='just_active_clubs',
        ),
        pytest.param(
            PHONE_ID_MIXED_CLUBS, {'active_club_2'}, id='just_mixed_clubs',
        ),
        pytest.param(
            PHONE_ID_JUST_INACTIVE_CLUBS, set(), id='just_inactive_clubs',
        ),
        pytest.param(PHONE_ID_NO_CLUBS, set(), id='no_clubs'),
    ],
)
@pytest.mark.parametrize(
    'exp_on',
    [
        pytest.param(
            True,
            marks=[pytest.mark.experiments3(filename='experiments3.json')],
            id='exp_on',
        ),
        pytest.param(False, id='exp_off'),
    ],
)
async def test_clubs_for_user(taxi_invites, phone_id, expected_clubs, exp_on):
    response = await taxi_invites.post(URL, json={'phone_id': phone_id})
    assert response.status_code == 200
    content = response.json()
    assert 'clubs' in content
    clubs = content['clubs']
    assert len(clubs) == len(set(clubs))
    assert set(clubs) == expected_clubs | ({CLUB_NAME} if exp_on else set())


@pytest.mark.experiments3(filename='experiments3.json')
async def test_adding_from_exp(taxi_invites, invites_db, stq):
    response = await taxi_invites.post(URL, json={'phone_id': '0'})

    assert response.status_code == 200

    assert invites_db.club_exists(CLUB_NAME)
    assert invites_db.user_is_club_member('0', CLUB_NAME)

    assert stq.invites_member_set_club_tag.times_called == 1
    save_call = stq.invites_member_set_club_tag.next_call()
    assert save_call['kwargs']['phone_id'] == '0'
    assert save_call['kwargs']['club_id'] == invites_db.get_club_id(CLUB_NAME)
