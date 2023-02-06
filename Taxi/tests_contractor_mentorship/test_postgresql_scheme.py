import pytest


def row_assertion(row, assertion_dict):
    for key, value in assertion_dict.items():
        assert row[key] == value


@pytest.mark.parametrize(
    'id, expected_dict',
    [
        (
            '275477b7-96bc-5ac9-8af8-cd2fbcc1a142',
            {
                1: '620b5440f03452205a848432',
                2: 'rus',
                4: 'ТестовыйТестТестович',
                6: '068ed9d642424e1f80942b1d7f3e75de_74aa82d9d199436d8ac00ea108f30696',
                7: '94393ac6c83b430296cf7a35444d0c59',
                8: '5c4abc19e301b6012f9da829',
                10: '0467cef7e27c42d1a62223984ef27753_187dbd532179956a7bbb4f73f5cf4dc4',
                12: 'failed',
            },
        ),
        (None, {}),
    ],
)
@pytest.mark.pgsql('contractor_mentorship', files=['insert_mentorships.sql'])
async def test_mentorship(pgsql, id, expected_dict):
    query = f"""
    SELECT
        id,
        newbie_unique_driver_id,
        country_id,
        created_at,
        mentor_full_name,
        mentor_last_read_at,
        mentor_park_driver_profile_id,
        mentor_phone_pd_id,
        mentor_unique_driver_id,
        newbie_last_read_at,
        newbie_park_driver_profile_id,
        original_connected_dttm,
        "status"
    FROM contractor_mentorship.mentorships
    WHERE id = '{id}';
    """

    cursor = pgsql['contractor_mentorship'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    if id:
        row_assertion(rows[0], expected_dict)
    else:
        assert rows == []


@pytest.mark.parametrize(
    'id, expected_dict',
    [
        (
            '275477b7-96bc-5ac9-8af8-cd2fbcc1a142',
            {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: 0},
        ),
        (None, {}),
    ],
)
@pytest.mark.pgsql('contractor_mentorship', files=['insert_results.sql'])
async def test_results(pgsql, id, expected_dict):
    query = f"""
    SELECT
        mentorship_id,
        rate_avg_7d,
        rate_avg_14d,
        avg_dp_7d,
        avg_dp_14d,
        sh_7d,
        sh_14d,
        correct_answers,
        passed_test_flg
    FROM contractor_mentorship.results
    WHERE mentorship_id = '{id}';
    """

    cursor = pgsql['contractor_mentorship'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    if id:
        row_assertion(rows[0], expected_dict)
    else:
        assert rows == []


@pytest.mark.parametrize(
    'id, expected_dict',
    [
        (
            '275477b7-96bc-5ac9-8af8-cd2fbcc1a142',
            {
                2: '275477b7-96bc-5ac9-8af8-cd2fbcc1a142',
                3: 'in_progress',
                4: 'failed',
            },
        ),
        (None, {}),
    ],
)
@pytest.mark.pgsql(
    'contractor_mentorship', files=['insert_status_transitions.sql'],
)
async def test_status_transitions(pgsql, id, expected_dict):
    query = f"""
    SELECT
        id,
        created_at,
        mentorship_id,
        "from",
        "to"
    FROM contractor_mentorship.status_transitions
    WHERE mentorship_id = '{id}';
    """

    cursor = pgsql['contractor_mentorship'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    if id:
        row_assertion(rows[0], expected_dict)
    else:
        assert rows == []


@pytest.mark.parametrize(
    'id, expected_dict',
    [
        (
            0,
            {
                0: 0,
                1: 'Аккра',
                2: 'gha',
                3: 'Гана',
                4: '95e091c97677489daa395b605213f75b',
                5: '733d2ec6a0de4c5285a6b2dc5a0184bf',
                6: 'Test',
                7: 'Testington',
                8: '1659b583604742a2b8dcd3a3182bc3dd',
                9: '5c4abc19e301b6012f9da829',
                11: 'failed',
            },
        ),
        (1, {}),
    ],
)
@pytest.mark.pgsql('contractor_mentorship', files=['insert_mentors.sql'])
async def test_mentors(pgsql, id, expected_dict):
    query = f"""
    SELECT
        id,
        city,
        country_id,
        country_name_ru,
        db_id,
        driver_uuid,
        first_name,
        last_name,
        phone,
        unique_driver_id,
        updated_at,
        "status"
    FROM contractor_mentorship.mentors
    WHERE id = {id};
    """

    cursor = pgsql['contractor_mentorship'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    if id == 0:
        row_assertion(rows[0], expected_dict)
    else:
        assert rows == []
