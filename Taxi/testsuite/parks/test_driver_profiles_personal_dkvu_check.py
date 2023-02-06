# encoding=utf-8
import pytest

from . import error


ENDPOINT_URL = '/driver-profiles/personal-patch'
INTERNAL_ENDPOINT_URL = '/internal/driver-profiles/personal-patch'
DRIVER_UPDATED_TRIGGER_URL = (
    '/taximeter-xservice.taxi.yandex.net/' 'utils/driver-updated-trigger'
)

AUTHOR_YA_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-11',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-Ip': '1.2.3.4',
}
AUTHOR_YA_TEAM_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-team-11',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Real-Ip': '1.2.3.4',
}
PLATFORM_HEADERS = {'X-Ya-Service-Name': 'mock'}

DRIVER_PROFILES = [
    {'first_name': 'Влад'},
    {'middle_name': 'Иванович'},
    {'last_name': 'Петров'},
    {'first_name': 'Влад', 'middle_name': 'Иванович', 'last_name': 'Петров'},
    {
        'first_name': 'Влад',
        'driver_license': {
            'country': 'fra',
            'number': '12345EE',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
    {
        'middle_name': 'Иванович',
        'driver_license': {
            'country': 'fra',
            'number': '12345EE',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
    {
        'last_name': 'Петров',
        'driver_license': {
            'country': 'fra',
            'number': '12345EE',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
    {
        'first_name': 'Влад',
        'middle_name': 'Иванович',
        'last_name': 'Петров',
        'driver_license': {
            'country': 'fra',
            'number': '12345EE',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    },
]
LICENSE_NORMALIZED = '12345EE'
DRIVER_NAME_KEYS = ('first_name', 'middle_name', 'last_name')


@pytest.fixture
def driver_updated_trigger(mockserver):
    @mockserver.json_handler(DRIVER_UPDATED_TRIGGER_URL)
    def mock_callback(request):
        return {}

    return mock_callback


def get_driver(db, park_id, driver_id):
    return db.dbdrivers.find_one({'park_id': park_id, 'driver_id': driver_id})


@pytest.mark.config(PARKS_ENABLE_DKVU_CHECK_BEFORE_EDIT=True)
@pytest.mark.parametrize(
    'endpoint_url, author, expected_code',
    [
        pytest.param(ENDPOINT_URL, AUTHOR_YA_HEADERS, 400, id='ya user'),
        pytest.param(
            ENDPOINT_URL, AUTHOR_YA_TEAM_HEADERS, 200, id='ya team user',
        ),
        pytest.param(
            INTERNAL_ENDPOINT_URL,
            PLATFORM_HEADERS,
            400,
            id='internal endpoint',
        ),
    ],
)
@pytest.mark.parametrize('driver_profile', DRIVER_PROFILES)
def test_forbid_license_or_full_name_change_authors(
        db,
        taxi_parks,
        contractor_profiles_manager,
        driver_updated_trigger,
        dispatcher_access_control,
        personal_phones_bulk_find,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        taximeter_xservice_mock,
        endpoint_url,
        author,
        driver_profile,
        expected_code,
):
    taximeter_xservice_mock.set_driver_exams_retrieve_response(
        {'dkvu_exam': {'pass': {'status': 'pending'}}},
    )
    mongo_before = get_driver(db, '123', '0')
    response = taxi_parks.put(
        endpoint_url,
        params={'park_id': '123', 'id': '0'},
        json={'driver_profile': {'set': {**driver_profile}}},
        headers=author,
    )

    mongo_after = get_driver(db, '123', '0')

    if expected_code == 400:
        assert response.status_code == 400, response.text
        error_message = (
            'cannot_edit_driver_license_and_full_name_when_dkvu_passed'
        )
        assert response.json() == error.make_error_response(
            error_message, error_message,
        )

        assert mongo_before == mongo_after
    else:
        assert response.status_code == 200, response.text
        if 'driver_license' in driver_profile:
            assert mongo_after['license_normalized'] == LICENSE_NORMALIZED
        for key in DRIVER_NAME_KEYS:
            if key in driver_profile:
                assert mongo_after[key] == driver_profile[key]


@pytest.mark.config(PARKS_ENABLE_DKVU_CHECK_BEFORE_EDIT=True)
@pytest.mark.parametrize(
    'dkvu_state, expected_code',
    [
        pytest.param(None, 200, id='no dkvu'),
        pytest.param({}, 200, id='no pass'),
        pytest.param({'pass': {'status': 'pending'}}, 400, id='pending'),
        pytest.param({'pass': {'status': 'success'}}, 400, id='success'),
        pytest.param({'pass': {'status': 'fail'}}, 200, id='fail'),
    ],
)
def test_forbid_license_or_full_name_change_dkvu_state(
        db,
        taxi_parks,
        contractor_profiles_manager,
        driver_updated_trigger,
        dispatcher_access_control,
        personal_phones_bulk_find,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        taximeter_xservice_mock,
        dkvu_state,
        expected_code,
):
    driver_profile = {
        'first_name': 'Влад',
        'middle_name': 'Иванович',
        'last_name': 'Петров',
        'driver_license': {
            'country': 'fra',
            'number': '12345EE',
            'birth_date': '1939-09-01',
            'expiration_date': '2028-11-20',
            'issue_date': '2018-11-20',
        },
    }
    if dkvu_state:
        taximeter_xservice_mock.set_driver_exams_retrieve_response(
            {'dkvu_exam': dkvu_state},
        )
    else:
        taximeter_xservice_mock.set_driver_exams_retrieve_response({})
    mongo_before = get_driver(db, '123', '0')
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '123', 'id': '0'},
        json={'driver_profile': {'set': driver_profile}},
        headers=AUTHOR_YA_HEADERS,
    )

    mongo_after = get_driver(db, '123', '0')

    if expected_code == 400:
        assert response.status_code == 400, response.text
        error_message = (
            'cannot_edit_driver_license_and_full_name_when_dkvu_passed'
        )
        assert response.json() == error.make_error_response(
            error_message, error_message,
        )

        assert mongo_before == mongo_after
    else:
        assert response.status_code == 200, response.text
        assert mongo_after['license_normalized'] == LICENSE_NORMALIZED
        for key in DRIVER_NAME_KEYS:
            assert mongo_after[key] == driver_profile[key]


@pytest.mark.config(PARKS_ENABLE_DKVU_CHECK_BEFORE_EDIT=True)
@pytest.mark.parametrize(
    'driver_id, driver_profile, expected_code',
    [
        pytest.param(
            '0',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '123123',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            200,
            id='no changes',
        ),
        pytest.param('0', {'first_name': 'Andrew'}, 200, id='no changes 1'),
        pytest.param('0', {'middle_name': 'Al'}, 200, id='no changes 2'),
        pytest.param('0', {'last_name': 'Mir'}, 200, id='no changes 3'),
        pytest.param(
            '0',
            {'first_name': 'Andrew', 'middle_name': 'Al', 'last_name': 'Mir'},
            200,
            id='no changes 4',
        ),
        pytest.param(
            '0',
            {
                'first_name': 'Andrew',
                'middle_name': 'Al',
                'last_name': 'Mir',
                'driver_license': {
                    'country': 'fra',
                    'number': '123123',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            200,
            id='no changes 5',
        ),
        pytest.param(
            '0', {'first_name': 'Ivan'}, 400, id='first_name changed',
        ),
        pytest.param(
            '0', {'middle_name': 'Ivanovich'}, 400, id='middle_name changed',
        ),
        pytest.param(
            '0', {'last_name': 'Ivanov'}, 400, id='last_name changed',
        ),
        pytest.param(
            '0',
            {
                'first_name': 'Ivanovich',
                'middle_name': 'Ivanovich',
                'last_name': 'Ivanov',
            },
            400,
            id='first_name, middle_name and last_name changed ',
        ),
        pytest.param(
            '0',
            {
                'first_name': 'Ivanovich',
                'middle_name': 'Ivanovich',
                'last_name': 'Ivanov',
                'driver_license': {
                    'country': 'fra',
                    'number': '123123',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='first_name, middle_name and last_name changed ',
        ),
        pytest.param(
            '0',
            {
                'first_name': 'Ivanovich',
                'middle_name': 'Ivanovich',
                'last_name': 'Ivanov',
                'driver_license': {
                    'country': 'fra',
                    'number': '1231235',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='first_name, middle_name, last_name and number changed ',
        ),
        pytest.param(
            '0',
            {
                'first_name': 'Andrew',
                'middle_name': 'Al',
                'last_name': 'Mir',
                'driver_license': {
                    'country': 'fra',
                    'number': '1231235',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='number changed',
        ),
        pytest.param(
            '0',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '123555',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='number changed',
        ),
        pytest.param(
            '0',
            {
                'driver_license': {
                    'country': 'kaz',
                    'number': '12345EE',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='country changed',
        ),
        pytest.param(
            '0',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '12345EE',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='birth_date removed',
        ),
        pytest.param(
            '0',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '12345EE',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2027-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='expiration_date changed',
        ),
        pytest.param(
            '0',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '12345EE',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-21',
                },
            },
            400,
            id='issue_date changed',
        ),
        pytest.param(
            '1',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '523123',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            200,
            id='no changes 6',
        ),
        pytest.param(
            '1',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '523123',
                    'birth_date': '1939-09-01',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='add birthday',
        ),
        pytest.param(
            '2',
            {
                'driver_license': {
                    'country': 'fra',
                    'number': '423123',
                    'expiration_date': '2028-11-20',
                    'issue_date': '2018-11-20',
                },
            },
            400,
            id='no expiration_date and issue_date in mongo',
        ),
    ],
)
def test_forbid_license_or_full_name_change_license_state(
        db,
        taxi_parks,
        contractor_profiles_manager,
        driver_updated_trigger,
        dispatcher_access_control,
        personal_phones_bulk_find,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        taximeter_xservice_mock,
        driver_id,
        driver_profile,
        expected_code,
):
    taximeter_xservice_mock.set_driver_exams_retrieve_response(
        {'dkvu_exam': {'pass': {'status': 'success'}}},
    )
    mongo_before = get_driver(db, '123', driver_id)
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '123', 'id': driver_id},
        json={'driver_profile': {'set': {**driver_profile}}},
        headers=AUTHOR_YA_HEADERS,
    )

    mongo_after = get_driver(db, '123', driver_id)

    if expected_code == 400:
        assert response.status_code == 400, response.text
        error_message = (
            'cannot_edit_driver_license_and_full_name_when_dkvu_passed'
        )
        assert response.json() == error.make_error_response(
            error_message, error_message,
        )
        assert mongo_before == mongo_after
    else:
        assert response.status_code == 200, response.text


@pytest.mark.parametrize(
    'driver_profile_id, expected_code', [('0', 400), ('1', 200)],
)
@pytest.mark.config(PARKS_ENABLE_DKVU_CHECK_BEFORE_EDIT=True)
def test_forbid_unset_middle_name_when_dkvu_passed(
        db,
        taxi_parks,
        contractor_profiles_manager,
        driver_updated_trigger,
        dispatcher_access_control,
        personal_phones_bulk_find,
        personal_driver_licenses_bulk_store,
        personal_emails_bulk_store,
        personal_phones_bulk_store,
        taximeter_xservice_mock,
        driver_profile_id,
        expected_code,
):
    taximeter_xservice_mock.set_driver_exams_retrieve_response(
        {'dkvu_exam': {'pass': {'status': 'success'}}},
    )

    mongo_before = get_driver(db, '123', driver_profile_id)
    response = taxi_parks.put(
        ENDPOINT_URL,
        params={'park_id': '123', 'id': driver_profile_id},
        json={'driver_profile': {'unset': ['middle_name']}},
        headers=AUTHOR_YA_HEADERS,
    )
    mongo_after = get_driver(db, '123', driver_profile_id)

    if expected_code == 400:
        assert response.status_code == 400, response.text
        error_message = (
            'cannot_edit_driver_license_and_full_name_when_dkvu_passed'
        )
        assert response.json() == error.make_error_response(
            error_message, error_message,
        )
        assert mongo_before == mongo_after
    else:
        assert response.status_code == 200, response.text
