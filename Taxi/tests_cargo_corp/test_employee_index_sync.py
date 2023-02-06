import pytest  # noqa: F401

from tests_cargo_corp import utils


(
    LOCAL_CORP_ID0,
    LOCAL_CORP_ID1,
    LOCAL_CORP_ID2,
    LOCAL_CORP_ID3,
    LOCAL_CORP_ID4,
) = (
    utils.CORP_CLIENT_ID,  # effects due autouse fixture
    'corp_client_id_12345678910111213',
    'corp_client_id_12345678910111214',
    'corp_client_id_12345678910111215',
    'corp_client_id_12345678910111216',
)

# TODO (dipterix): rewrite test to ingnore order
SECONDARY_EXPECTED_DATA = [
    ('yandex_uid1', 3755605199, LOCAL_CORP_ID1),
    ('yandex_uid1', 3755605199, LOCAL_CORP_ID2),
    ('yandex_uid1', 3755605199, LOCAL_CORP_ID3),
    ('yandex_uid1', 3755605199, LOCAL_CORP_ID4),
    ('yandex_uid1', 3755605199, LOCAL_CORP_ID0),
    ('yandex_uid2', 1188081013, LOCAL_CORP_ID1),
    ('yandex_uid2', 1188081013, LOCAL_CORP_ID2),
    ('yandex_uid2', 1188081013, LOCAL_CORP_ID3),
    ('yandex_uid2', 1188081013, LOCAL_CORP_ID4),
    ('yandex_uid3', 836214243, LOCAL_CORP_ID1),
    ('yandex_uid3', 836214243, LOCAL_CORP_ID2),
    ('yandex_uid3', 836214243, LOCAL_CORP_ID3),
    ('yandex_uid3', 836214243, LOCAL_CORP_ID4),
    ('yandex_uid4', 2947745856, LOCAL_CORP_ID1),
    ('yandex_uid4', 2947745856, LOCAL_CORP_ID2),
    ('yandex_uid4', 2947745856, LOCAL_CORP_ID3),
    ('yandex_uid4', 2947745856, LOCAL_CORP_ID4),
    ('yandex_uid5', 3635689686, LOCAL_CORP_ID1),
    ('yandex_uid5', 3635689686, LOCAL_CORP_ID2),
    ('yandex_uid5', 3635689686, LOCAL_CORP_ID3),
    ('yandex_uid5', 3635689686, LOCAL_CORP_ID4),
]
SECONDARY_EXPECTED_DATA_CUT = [
    ('yandex_uid2', 1188081013, LOCAL_CORP_ID3),
    ('yandex_uid2', 1188081013, LOCAL_CORP_ID4),
    ('yandex_uid3', 836214243, LOCAL_CORP_ID3),
    ('yandex_uid3', 836214243, LOCAL_CORP_ID4),
    ('yandex_uid4', 2947745856, LOCAL_CORP_ID3),
    ('yandex_uid4', 2947745856, LOCAL_CORP_ID4),
]


async def compare_revisions(cursor, current_revision, is_equal=True):
    cursor.execute(
        """
        SELECT corp_client_id, yandex_uid, revision, uid_revision
        FROM corp_clients.employees ORDER BY yandex_uid;
        """,
    )
    for row in list(cursor):
        if current_revision == row[2]:
            assert is_equal == (row[2] == row[3])


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        f"""
        INSERT INTO corp_clients.clients
        (corp_client_id, sharded_key_hash)
        VALUES
        ('{LOCAL_CORP_ID1}', 1),
        ('{LOCAL_CORP_ID2}', 2),
        ('{LOCAL_CORP_ID3}', 3),
        ('{LOCAL_CORP_ID4}', 4);
        """,
        f"""
        INSERT INTO corp_clients.employees
        (corp_client_id, yandex_uid)
        VALUES
        ('{LOCAL_CORP_ID1}', 'yandex_uid1'),
        ('{LOCAL_CORP_ID1}', 'yandex_uid2'),
        ('{LOCAL_CORP_ID1}', 'yandex_uid3'),
        ('{LOCAL_CORP_ID1}', 'yandex_uid4'),
        ('{LOCAL_CORP_ID1}', 'yandex_uid5'),
        ('{LOCAL_CORP_ID2}', 'yandex_uid1'),
        ('{LOCAL_CORP_ID2}', 'yandex_uid2'),
        ('{LOCAL_CORP_ID2}', 'yandex_uid3'),
        ('{LOCAL_CORP_ID2}', 'yandex_uid4'),
        ('{LOCAL_CORP_ID2}', 'yandex_uid5'),
        ('{LOCAL_CORP_ID3}', 'yandex_uid1'),
        ('{LOCAL_CORP_ID3}', 'yandex_uid2'),
        ('{LOCAL_CORP_ID3}', 'yandex_uid3'),
        ('{LOCAL_CORP_ID3}', 'yandex_uid4'),
        ('{LOCAL_CORP_ID3}', 'yandex_uid5'),
        ('{LOCAL_CORP_ID4}', 'yandex_uid1'),
        ('{LOCAL_CORP_ID4}', 'yandex_uid2'),
        ('{LOCAL_CORP_ID4}', 'yandex_uid3'),
        ('{LOCAL_CORP_ID4}', 'yandex_uid4'),
        ('{LOCAL_CORP_ID4}', 'yandex_uid5');
        """,
    ],
)
async def test_employee_sync_with_secondary(
        run_employee_index_sync, user_has_rights, pgsql,
):
    cursor = pgsql['cargo_corp'].cursor()
    await compare_revisions(cursor, 1, False)
    await run_employee_index_sync()  # data for insert
    cursor.execute(
        """
        SELECT * FROM corp_employees.clients
        ORDER BY yandex_uid, corp_client_id;
        """,
    )
    assert list(cursor) == SECONDARY_EXPECTED_DATA
    await compare_revisions(cursor, 2, True)
    cursor.execute(
        f"""
        UPDATE corp_clients.employees
        SET is_disabled = TRUE
        WHERE
        corp_client_id IN ('{LOCAL_CORP_ID1}', '{LOCAL_CORP_ID2}')
        OR yandex_uid IN ('yandex_uid1', 'yandex_uid5');
        """,
    )
    await compare_revisions(cursor, 3, False)
    await run_employee_index_sync()  # data for delete
    cursor.execute(
        """
        SELECT * FROM corp_employees.clients
        ORDER BY yandex_uid, corp_client_id;
        """,
    )
    assert list(cursor) == SECONDARY_EXPECTED_DATA_CUT
    await compare_revisions(cursor, 4, True)
    await run_employee_index_sync()  # no data test
